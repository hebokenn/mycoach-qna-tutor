#!/usr/bin/env python3
"""Render the saved actual text trials as a transparent browser evidence report."""
from pathlib import Path
import hashlib
import html
import json
import re

ROOT=Path(__file__).resolve().parents[1]

def inline(text):
    text=html.escape(text)
    text=re.sub(r'\[([^\]]+)\]\((https://[^\s)]+)\)',r'<a href="\2">\1</a>',text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',text)
    text=re.sub(r'`([^`]+)`',r'<code>\1</code>',text)
    return text

def markdown(text):
    lines=text.splitlines();result=[];i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('|') and i+1<len(lines) and re.match(r'^\|?[\s:|-]+\|',lines[i+1].strip()):
            headers=[x.strip() for x in line.strip('|').split('|')]
            result.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+inline(x)+'</th>' for x in headers)+'</tr></thead><tbody>');i+=2
            while i<len(lines) and lines[i].strip().startswith('|'):
                cols=[x.strip() for x in lines[i].strip().strip('|').split('|')]
                result.append('<tr>'+''.join('<td>'+inline(x)+'</td>' for x in cols)+'</tr>');i+=1
            result.append('</tbody></table></div>');continue
        if line.startswith('#'):
            level=min(len(line)-len(line.lstrip('#')),5)
            result.append(f'<h{level}>'+inline(line.lstrip('#').strip())+f'</h{level}>')
        elif re.match(r'^[-*] ',line):result.append('<p class="list">'+inline(line[2:])+'</p>')
        elif re.match(r'^\d+[.、] ',line):result.append('<p class="list">'+inline(line)+'</p>')
        else:result.append('<p>'+inline(line)+'</p>')
        i+=1
    return ''.join(result)

def build():
    scenarios=[json.loads(p.read_text()) for p in sorted((ROOT/'docs/scenarios').glob('scenario-*.json'))]
    views=[]
    for s in scenarios:
        count=sum(bool(c['passed']) for c in s['checks'])
        turns=''.join('<article class="turn '+t['role']+'"><div class="role">'+('测试输入' if t['role']=='user' else 'AI 实际回复')+'</div>'+markdown(t['content'])+'</article>' for t in s['turns'])
        notes=''.join('<li>'+inline(c['name'])+'</li>' for c in s['checks'])
        limits=''.join('<li>'+inline(c)+'</li>' for c in s.get('limitations',[]))
        views.append(f'<section class="scenario" id="{s["id"]}"><div class="scene-head"><div class="eyebrow">SCENARIO {s["id"]} · {inline(s["mode"])}</div><h1>{inline(s["title"])}</h1><p class="caption">预设用户输入 + 加载本地 Skill 后的 AI 实际输出 · 文字试用 · 2026-10-23</p></div><div class="columns"><div class="conversation">{turns}</div><aside><h2>本场检查</h2><p>{count} / {len(s["checks"])} 项已核对</p><ul>{notes}</ul><h2>适用范围</h2><ul>{limits}</ul><p><a href="scenarios/scenario-{s["id"]}.json">查看完整原始记录</a></p></aside></div></section>')
    nav=''.join(f'<a href="?scenario={s["id"]}">{s["id"]} {inline(s["title"][:14])}</a>' for s in scenarios)
    document='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>私教答疑 Skill · 场景实测记录</title><link rel="icon" href="data:,"><style>
*{box-sizing:border-box}body{margin:0;background:#f5f5f1;color:#202622;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;font-size:16px;line-height:1.75}header{background:#202b24;color:#fff;padding:20px 44px}header strong{font-size:22px}header span{font-size:13px;margin-left:18px;color:#cfd8d0}.notice{background:#e9eee7;border-bottom:1px solid #cbd5c9;padding:12px 44px;font-size:14px}nav{padding:17px 40px;display:flex;flex-wrap:wrap;gap:8px;border-bottom:1px solid #ddd}nav a{font-size:12px;border:1px solid #cbd2c8;padding:5px 10px;background:#fff;text-decoration:none;color:#364b3c;border-radius:4px}main{max-width:1360px;margin:0 auto;padding:28px 36px 60px}.scenario{display:none}.scenario.active{display:block}.eyebrow{font-size:12px;letter-spacing:1px;color:#526954}h1{font-size:31px;line-height:1.35;margin:8px 0 12px}h2{font-size:18px;line-height:1.4;margin:20px 0 8px}h3{font-size:17px;margin:15px 0 8px}.caption{font-size:13px;color:#687269;margin:0 0 24px}.columns{display:grid;grid-template-columns:minmax(0,1fr) 266px;gap:24px;align-items:start}.turn{padding:22px 25px;margin-bottom:18px;border:1px solid #dce0d8;border-radius:6px;background:#fff;overflow-wrap:anywhere}.turn.user{background:#eef1eb;border-color:#ced8cc}.role{font-size:12px;font-weight:700;letter-spacing:1px;color:#4f6b55;margin-bottom:12px}.turn p{margin:0 0 12px}.turn p:last-child{margin-bottom:0}aside{background:#fff;padding:20px;border:1px solid #dce0d8;border-radius:6px;font-size:13px;color:#465148}aside h2:first-child{margin-top:0}aside ul{padding-left:18px}aside li{margin-bottom:8px}a{color:#245b3b}code{font-size:.9em;background:#eff1eb;padding:2px 5px;border-radius:3px}.list{padding-left:12px;border-left:2px solid #c8d3c5}table{width:100%;border-collapse:collapse;font-size:13px;line-height:1.6}th,td{text-align:left;border:1px solid #d8ded5;padding:8px;vertical-align:top}th{background:#f0f3ec}footer{margin-top:28px;color:#687269;font-size:12px}.table-wrap{overflow:auto}@media(max-width:800px){header,.notice{padding-left:20px;padding-right:20px}header span{display:block;margin:3px 0 0}nav{padding:12px 16px}main{padding:20px 16px}.columns{grid-template-columns:1fr}h1{font-size:25px}.turn{padding:18px}aside{order:-1}}
</style><header><strong>私教答疑 Skill</strong><span>使用场景实测记录 · v1.1.0</span></header><div class="notice">本页展示已保存的实际文字测试输出；A/B保留历史版本，C2/C3为v1.1.0补测。不是 Codex / WorkBuddy 原生界面截图，也不代表电话、语音或视频功能已实测。</div><nav>'''+nav+'</nav><main>'+''.join(views)+'''<footer>所有回复原文、检查依据与限制保存在同目录JSON；截图仅展示报告页面，不替代完整记录。</footer></main><script>const id=new URLSearchParams(location.search).get('scenario')||'A1';const target=document.getElementById(id)||document.querySelector('.scenario');if(target)target.classList.add('active');document.documentElement.dataset.scenario=target?target.id:'';</script></html>'''
    (ROOT/'docs/scenario-report.html').write_text(document)
    summary={'date':'2026-10-23','method':'independent AI trials loading the local skill; preset user turns; actual generated assistant responses; browser rendering is a record viewer, not native host UI','scenarios':[{'id':s['id'],'title':s['title'],'turns':len(s['turns']),'checks':len(s['checks']),'passed':sum(bool(c['passed']) for c in s['checks']),'sha256':hashlib.sha256((ROOT/f'docs/scenarios/scenario-{s["id"]}.json').read_bytes()).hexdigest()} for s in scenarios]}
    (ROOT/'docs/scenarios/manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    return summary

if __name__=='__main__':print(json.dumps(build(),ensure_ascii=False,indent=2))
