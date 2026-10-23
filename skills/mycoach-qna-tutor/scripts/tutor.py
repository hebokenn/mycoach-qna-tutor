#!/usr/bin/env python3
"""Read-only, offline lookup for the bundled private-Q&A learning corpus."""
from pathlib import Path
import argparse
import json
import random
import sys

BASE = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads((BASE / path).read_text(encoding='utf-8'))

def lookup(args):
    catalog = read('references/catalog.json')
    if args.command == 'topics':
        return [{k: t[k] for k in ('number', 'key', 'title', 'guide', 'exerciseCount')} | {
            'personaCount': len(t['personaIds']), 'caseCount': len(t['caseIds'])
        } for t in catalog]
    topics = [t for t in catalog if not args.topic or t['key'] == args.topic]
    if not topics:
        raise ValueError('题目不存在，请先运行topics查询20题目录。')
    if args.command == 'persona':
        if args.id:
            hits = [(t, args.id) for t in topics if args.id in t['personaIds']]
        else:
            rng = random.Random(args.seed) if args.seed is not None else random.SystemRandom()
            available = [(t, [i for i in t['personaIds'] if i not in args.exclude]) for t in topics]
            available = [(t, ids) for t, ids in available if ids]
            if not available:
                raise ValueError('当前筛选下没有未排除的人设。')
            topic, ids = rng.choice(available)
            hits = [(topic, rng.choice(ids))]
        if not hits:
            raise ValueError('当前题目内没有这个人设ID。')
        topic, persona_id = hits[0]
        persona = read(f"references/personas/{topic['key']}/{persona_id}.json")
        return {'aiOnly': '这是AI的隐藏设定；顾客模式仅向学员输出opening与按条件披露的信息。', 'topic': topic['title'], 'persona': persona}
    if args.id:
        ids = {case_id for t in topics for case_id in t['caseIds']}
        if args.id not in ids:
            raise ValueError('当前范围内没有这个历史案例。')
        return read(f'references/cases/{args.id}.json')
    ids = [i for t in topics for i in t['caseIds']]
    cases = [read(f'references/cases/{i}.json') for i in ids]
    if args.query:
        query = args.query.casefold()
        cases = [c for c in cases if query in (str(c.get('question', '')) + str(c.get('comment', ''))).casefold()]
    cases.sort(key=lambda c: str(c.get('date') or ''), reverse=True)
    return {'matched': len(cases), 'cases': cases[:args.limit]}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('topics')
    persona = commands.add_parser('persona', help='抽取一份独立的真实顾客人设，或指定ID')
    persona.add_argument('--topic')
    persona.add_argument('--id')
    persona.add_argument('--seed', type=int)
    persona.add_argument('--exclude', nargs='*', default=[])
    cases = commands.add_parser('cases', help='按题目、ID或评语检索历史案例')
    cases.add_argument('--topic')
    cases.add_argument('--id')
    cases.add_argument('--query')
    cases.add_argument('--limit', type=int, default=3, choices=range(1, 21))
    args = parser.parse_args()
    try:
        result = lookup(args)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(2, f'检索失败：{error}\n')
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()

if __name__ == '__main__':
    main()
