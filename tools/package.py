#!/usr/bin/env python3
"""Build standard and WorkBuddy ZIPs from the versioned skill source."""
from pathlib import Path
import hashlib
import json
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'skills/mycoach-qna-tutor'

def build():
    entry=(SOURCE/'SKILL.md').read_text(encoding='utf-8')
    version=re.search(r'^  version: ([0-9.]+)$',entry,re.M).group(1)
    out=ROOT/'releases'/('v'+version)
    out.mkdir(parents=True,exist_ok=True)
    files=sorted(p for p in SOURCE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name!='.DS_Store' and p.name!='PACKAGE-SHA256.json')
    head,body=entry[4:].split('\n---\n',1)
    extra=f'\ndisplay_name: 私教答疑\ndescription_zh: 私教答疑考试答疑、双向角色对练、对练记录评分与Apple官方知识补充。\ndescription_en: Private Q&A exam tutoring, two-way roleplay, evidence-based practice assessment, and Apple official guidance.\nversion: {version}\nauthor: MyCoach\n'
    wb='---\n'+head+extra+'---\n'+body
    receipts=[]
    for host in ['standard','workbuddy']:
        payload={str(p.relative_to(SOURCE)):p.read_bytes() for p in files}
        if host=='workbuddy':payload['SKILL.md']=wb.encode('utf-8')
        manifest={name:hashlib.sha256(data).hexdigest() for name,data in payload.items()}
        payload['PACKAGE-SHA256.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
        suffix='-workbuddy' if host=='workbuddy' else ''
        archive=out/f'mycoach-qna-tutor{suffix}-v{version}.zip'
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for name,data in sorted(payload.items()):
                info=zipfile.ZipInfo('mycoach-qna-tutor/'+name,date_time=(2026,10,23,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o644<<16
                z.writestr(info,data,compresslevel=9)
        with zipfile.ZipFile(archive) as z:assert z.testzip() is None
        receipts.append({'file':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'bytes':archive.stat().st_size,'files':len(payload)})
    (out/'SHA256SUMS').write_text(''.join(f"{r['sha256']}  {r['file']}\n" for r in receipts))
    (out/'manifest.json').write_text(json.dumps({'version':version,'packages':receipts},ensure_ascii=False,indent=2)+'\n')
    return receipts

if __name__=='__main__':print(json.dumps(build(),ensure_ascii=False,indent=2))
