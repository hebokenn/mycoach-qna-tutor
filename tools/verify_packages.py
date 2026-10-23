#!/usr/bin/env python3
"""Verify archive CRCs, hashes and independent installs without the source workspace."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def verify():
    results=[]
    for manifest in sorted((ROOT/'releases').glob('v*/manifest.json')):
        content=json.loads(manifest.read_text())
        for entry in content['packages']:
            archive=manifest.parent/entry['file']
            assert hashlib.sha256(archive.read_bytes()).hexdigest()==entry['sha256']
            with tempfile.TemporaryDirectory(prefix='qna-independent-install-') as tmp:
                temp=Path(tmp)
                with zipfile.ZipFile(archive) as z:
                    assert z.testzip() is None
                    for member in z.infolist():
                        assert (temp/member.filename).resolve().is_relative_to(temp.resolve())
                    z.extractall(temp)
                skill=temp/'mycoach-qna-tutor'
                hashes=json.loads((skill/'PACKAGE-SHA256.json').read_text())
                for name,expected in hashes.items():
                    file=(skill/name).resolve()
                    assert file.is_relative_to(skill.resolve()) and file.is_file()
                    assert hashlib.sha256(file.read_bytes()).hexdigest()==expected
                topics=json.loads(subprocess.check_output([sys.executable,str(skill/'scripts/tutor.py'),'topics'],cwd=temp))
                assert len(topics)==20
                persona=json.loads(subprocess.check_output([sys.executable,str(skill/'scripts/tutor.py'),'persona','--topic','black-screen-sound','--seed','8'],cwd=temp))
                assert persona['persona']['topicKey']=='black-screen-sound'
                score=json.loads(subprocess.check_output([sys.executable,str(skill/'scripts/score_record.py'),'--input','-'],input=b'{"items":{}}',cwd=temp))
                assert score['completeTotal'] is None and score['fullScoreInterval']==[0,100]
                results.append({'package':entry['file'],'sha256':entry['sha256'],'verifiedFiles':len(hashes),'crc':'ok','independentInstall':'passed'})
    assert len(results)>=2,'No packages found; run tools/package.py first.'
    print(json.dumps(results,ensure_ascii=False,indent=2))
    return results

if __name__=='__main__':verify()
