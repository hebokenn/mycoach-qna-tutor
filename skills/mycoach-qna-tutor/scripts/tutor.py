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
    if args.command == 'flow':
        return read('references/service-flow.json')
    catalog = read('references/catalog.json')
    if args.command == 'topics':
        return [{k: t[k] for k in ('number', 'key', 'title', 'guide', 'exerciseCount')} | {
            'personaCount': len(t['personaIds']), 'caseCount': len(t['caseIds'])
        } for t in catalog]
    topics = [t for t in catalog if not args.topic or t['key'] == args.topic]
    if not topics:
        raise ValueError('题目不存在，请先运行topics查询20题目录。')
    if args.command == 'lesson':
        topic = topics[0]
        lessons = read('references/topic-lessons.json').get(topic['key'], [])
        if args.number is not None:
            if not 1 <= args.number <= len(lessons):
                raise ValueError('讲解单元不存在；第一题沿用原攻略，其余题先不加--number查看目录。')
            return {'topic': topic['title'], 'number': args.number, 'lesson': lessons[args.number-1]}
        return {'topic': topic['title'], 'guide': topic['guide'], 'lessons': [
            {'number': i+1, 'title': item['title'], 'feature': item['learning']['feature']}
            for i, item in enumerate(lessons)
        ]}
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
        defaults = read('references/simulation-defaults.json')
        historical = args.historical
        roleplay = {
            'mode': 'historical_replay' if historical else defaults['defaultMode'],
            'runtimeCompletionAllowed': not historical,
            'cachedStableSystems': {} if historical else defaults['cachedStableSystems'],
            'cacheVerifiedOn': defaults['verifiedOn'],
            'source': defaults['source'],
            'officialRefreshAtRoundStart': not historical,
            'instructions': '严格按原记录，未知项保持未知。' if historical else (
                '按references/roleplay.md进行有情绪的可操作模拟；原persona保留历史原貌，'
                '其中未知项不禁止补齐本轮必要界面。核对最新正式系统后本轮固定，'
                '口述具体显示，不让学员看AI屏幕。新增信息记入模拟状态，不改历史人设。'
            ),
        }
        return {'aiOnly': '这是AI隐藏设定；遵循roleplay模式，仅披露当前问到的信息，不展示隐藏答案。', 'topic': topic['title'], 'persona': persona, 'roleplay': roleplay}
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
    commands.add_parser('flow', help='读取六环节完整服务流程和来源范围')
    lesson = commands.add_parser('lesson', help='查看本题深入讲解目录或一个完整单元；第一题沿用原攻略')
    lesson.add_argument('--topic', required=True)
    lesson.add_argument('--number', type=int)
    persona = commands.add_parser('persona', help='抽取一份独立的真实顾客人设，或指定ID')
    persona.add_argument('--topic')
    persona.add_argument('--id')
    persona.add_argument('--seed', type=int)
    persona.add_argument('--exclude', nargs='*', default=[])
    persona.add_argument('--historical', action='store_true', help='严格历史回放，不补齐模拟界面、系统和结果；默认可操作模拟')
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
