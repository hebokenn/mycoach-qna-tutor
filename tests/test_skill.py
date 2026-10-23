from pathlib import Path
import copy, hashlib, importlib.util, json, random, re, subprocess, sys, unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'skills/mycoach-qna-tutor'
FIXTURES = ROOT / 'tests/fixtures'
spec = importlib.util.spec_from_file_location('scorer', BASE/'scripts/score_record.py')
scorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scorer)
standard = json.loads((BASE/'references/exam-standard.json').read_text())
catalog = json.loads((BASE/'references/catalog.json').read_text())
import xml.etree.ElementTree as ET
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def original_cells():
    import zipfile
    with zipfile.ZipFile(BASE/'assets/private-qna-standard.xlsx') as z:
        strings=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
        cells=[]
        for name in z.namelist():
            if not re.match(r'xl/worksheets/sheet[0-9]+[.]xml',name):continue
            for c in ET.fromstring(z.read(name)).findall('.//s:c',NS):
                v=c.find('s:v',NS);value=v.text if v is not None else ''
                if c.get('t')=='s' and value:value=strings[int(value)]
                if value:cells.append(value)
        return cells

def fixture(score=8, yes='有'):
    return {'record_scope':'complete','medium':'video','items':{i['key']:{'status':'observed','score':yes if i['scoreType']=='yes_no' else score,'evidence':['00:01–00:20 测试夹具位置；不代表真实学员表现'],'reason':'仅用于计分算术验证'} for i in standard['items']}}

class SkillTests(unittest.TestCase):
    def test_full_maximum(self):
        r=scorer.calculate(fixture(10));self.assertEqual(r['completeTotal'],100);self.assertEqual(r['simulationResult'],'通过')
    def test_full_zero(self):
        r=scorer.calculate(fixture(0,'无'));self.assertEqual(r['completeTotal'],0);self.assertEqual(r['simulationResult'],'未通过')
    def test_weighted_eight_with_process(self):
        r=scorer.calculate(fixture(8));self.assertEqual(r['completeTotal'],82)
        self.assertEqual({k:v['observedPoints'] for k,v in r['dimensions'].items()},{'dim1':24,'dim2':28,'dim3':20,'dim4':10})
    def test_empty_is_unknown_not_zero(self):
        r=scorer.calculate({'items':{}});self.assertIsNone(r['completeTotal']);self.assertIsNone(r['simulationResult']);self.assertIsNone(r['observedOnlyPercent']);self.assertEqual(r['fullScoreInterval'],[0,100]);self.assertEqual(r['observedMaximum'],0)
    def test_partial_does_not_become_pass(self):
        r=scorer.calculate({'record_scope':'partial','medium':'text','items':{'qna-12':{'status':'observed','score':6,'evidence':['T008：上限80%就是最大容量80%。'],'reason':'混淆不同概念'}}})
        self.assertEqual(r['observedPoints'],8.4);self.assertEqual(r['observedMaximum'],14);self.assertEqual(r['observedOnlyPercent'],60);self.assertEqual(r['fullScoreInterval'],[8.4,94.4]);self.assertIsNone(r['simulationResult'])
    def test_unknown_is_not_missing_action(self):
        d=fixture();d['record_scope']='partial';d['items']['qna-01']['status']='not_done';d['items']['qna-01']['score']='无'
        with self.assertRaises(ValueError):scorer.calculate(d)
    def test_unobservable_cannot_receive_a_score(self):
        d=fixture();d['items']['qna-15']['status']='unobservable'
        with self.assertRaises(ValueError):scorer.calculate(d)
        d['items']['qna-15']['score']=None;r=scorer.calculate(d);self.assertEqual(r['observedMaximum'],93);self.assertIsNone(r['completeTotal'])
    def test_evidence_required_for_score(self):
        d=fixture();d['items']['qna-12']['evidence']=[]
        with self.assertRaises(ValueError):scorer.calculate(d)
    def test_invalid_scores_fail_instead_of_clamping(self):
        for invalid in [-1,11,True,None,'NaN','Infinity','abc']:
            d=fixture();d['items']['qna-12']['score']=invalid
            with self.subTest(value=invalid),self.assertRaises(ValueError):scorer.calculate(d)
    def test_unknown_keys_fail(self):
        d=fixture();d['items']['item-99']=d['items']['qna-12']
        with self.assertRaises(ValueError):scorer.calculate(d)
    def test_process_legacy_values(self):
        self.assertEqual(scorer.calculate(fixture(8,'是'))['completeTotal'],82)
        self.assertEqual(scorer.calculate(fixture(8,'否'))['completeTotal'],72)
    def test_random_scores_match_original_project_engine(self):
        samples=json.loads((FIXTURES/'scoring-golden.json').read_text())['samples']
        self.assertEqual(len(samples),100)
        for sample in samples:
            d=fixture()
            for key,value in sample['scores'].items():d['items'][key]['score']=value
            expected=sample['expected'];actual=scorer.calculate(d)
            self.assertEqual(actual['completeTotal'],expected['totalScore'])
            self.assertEqual(actual['simulationResult'],expected['result'])
            self.assertEqual({k:v['observedPoints'] for k,v in actual['dimensions'].items()},expected['dimensionScores'])
    def test_topic_and_evidence_coverage(self):
        self.assertEqual(len(catalog),20);self.assertEqual(sum(len(t['personaIds']) for t in catalog),1267);self.assertEqual(sum(len(t['caseIds']) for t in catalog),1281);self.assertEqual(sum(t['exerciseCount'] for t in catalog),201)
        for t in catalog:
            self.assertTrue((BASE/t['guide']).exists())
            for pid in t['personaIds']:
                p=json.loads((BASE/f"references/personas/{t['key']}/{pid}.json").read_text());self.assertEqual(p['topicKey'],t['key']);self.assertIn(p['sourceExamId'],t['caseIds']);self.assertTrue(p['opening']);self.assertTrue(p['evidence'])
                for disclosure in p['disclosures']:
                    self.assertGreaterEqual(disclosure['evidence'],0);self.assertLess(disclosure['evidence'],len(p['evidence']))
                for evidence in p['evidence']:self.assertLessEqual(evidence['start'],evidence['end'])
    def test_original_excel_preserved(self):
        expected=json.loads((BASE/'references/provenance.json').read_text())['originalXlsxSha256']
        self.assertEqual(hashlib.sha256((BASE/'assets/private-qna-standard.xlsx').read_bytes()).hexdigest(),expected)
        cells=original_cells()
        for item in standard['items']:self.assertIn(item['standard'],cells)
    def test_flow_source_and_transcript_preserve_original(self):
        import zipfile
        flow=json.loads((BASE/'references/service-flow.json').read_text())
        source=BASE/'references'/flow['source']['original']
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),flow['source']['sha256'])
        transcript=json.loads((BASE/'references'/flow['source']['transcript']).read_text())
        with zipfile.ZipFile(source) as z:
            doc=ET.fromstring(z.read('word/document.xml'))
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        rows=[{'paragraph':i,'text':''.join(t.text or '' for t in p.findall('.//w:t',ns))} for i,p in enumerate(doc.findall('.//w:body/w:p',ns),1)]
        self.assertEqual(transcript['paragraphs'],rows)
        self.assertIn({'paragraph':16,'text':'4、'},rows)
        self.assertEqual(transcript['sourceSha256'],flow['source']['sha256'])
    def test_flow_lookup_and_rubric_mapping(self):
        flow=json.loads(subprocess.check_output([sys.executable,str(BASE/'scripts/tutor.py'),'flow']))
        self.assertEqual(flow['source']['trainingMinutes'],15)
        mapped={n for stage in flow['stages'] for n in stage['itemNumbers']}
        self.assertEqual(mapped,{i['number'] for i in standard['items']})
        self.assertTrue({n for n in flow['qualityBranch']['itemNumbers']}.issubset(mapped))
    def test_weights_are_nested_not_flat(self):
        self.assertEqual(sum(d['weight'] for d in standard['dimensions']),100)
        for d in standard['dimensions']:self.assertEqual(sum(i['weight'] for i in standard['items'] if i['itemColumn']==d['key']),100)
    def test_score_band_headings_and_details_match_excel(self):
        cells=original_cells()
        normalize=lambda text:re.sub(r'[\s。．.，,；;：:、"“”‘’\u0027（）()]+','',text)
        available={normalize(c) for c in cells}
        for item in standard['items']:
            for field in ['score04Text','score57Text','score8Text','score910Text','yesCriteria','noCriteria']:
                for part in item.get(field,'').splitlines():
                    self.assertIn(normalize(part),available,(item['number'],field,part))
    def test_local_references_resolve(self):
        for p in BASE.rglob('*.md'):
            for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
                if '://' not in link and not link.startswith('#'):self.assertTrue((p.parent/link.split('#')[0]).exists(),(p,link))
    def test_persona_draw_and_exclusion(self):
        command=[sys.executable,str(BASE/'scripts/tutor.py'),'persona','--topic','battery-quality','--seed','7']
        first=json.loads(subprocess.check_output(command))['persona'];second=json.loads(subprocess.check_output(command))['persona'];self.assertEqual(first['id'],second['id'])
        third=json.loads(subprocess.check_output(command+['--exclude',first['id']]))['persona'];self.assertNotEqual(first['id'],third['id'])
    def test_persona_bad_id_no_traversal(self):
        r=subprocess.run([sys.executable,str(BASE/'scripts/tutor.py'),'persona','--id','../../SKILL'],capture_output=True);self.assertEqual(r.returncode,2)
    def test_no_contact_credentials_or_host_paths(self):
        for p in BASE.rglob('*'):
            if p.suffix not in {'.json','.md','.py','.yaml'}:continue
            value=re.sub(r'\b[a-f0-9]{64}\b','[SHA256]',p.read_text(),flags=re.I)
            for pattern in [r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}',r'(?<!\d)1[3-9]\d{9}(?!\d)',r'BEGIN (?:RSA |OPENSSH )?PRIVATE KEY',r'eyJ[A-Za-z0-9_-]{10,}\.eyJ',r'(?:/Users/[^/\s]+/|/home/[^/\s]+/)']:
                self.assertIsNone(re.search(pattern,value,re.I),(str(p),pattern))

if __name__=='__main__':unittest.main(verbosity=2)
