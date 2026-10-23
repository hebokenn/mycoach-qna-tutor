#!/usr/bin/env python3
"""Calculate evidence-based practice scores; does not judge a transcript itself."""
from pathlib import Path
from decimal import Decimal, InvalidOperation
import argparse
import json
import math
import sys

BASE = Path(__file__).resolve().parents[1]
VALID_STATUSES = {'observed', 'not_done', 'unobservable', 'missing'}

def rounded(value):
    # Match the project's JavaScript Math.round(value * 100) / 100.
    return math.floor(float(value) * 100 + 0.5) / 100

def calculate(record):
    if not isinstance(record, dict) or not isinstance(record.get('items'), dict):
        raise ValueError('输入必须是包含items对象的JSON。')
    scope = record.get('record_scope', 'unknown')
    if scope not in {'complete', 'partial', 'unknown'}:
        raise ValueError('record_scope须为complete、partial或unknown。')
    medium = record.get('medium', 'unknown')
    if medium not in {'text', 'transcript', 'audio', 'video', 'mixed', 'unknown'}:
        raise ValueError('medium须为text、transcript、audio、video、mixed或unknown。')
    standard = json.loads((BASE / 'references/exam-standard.json').read_text(encoding='utf-8'))
    definition = {i['key']: i for i in standard['items']}
    extra = set(record['items']) - set(definition)
    if extra:
        raise ValueError('未知量尺项目：' + ', '.join(sorted(extra)))
    dims = {d['key']: Decimal(str(d['weight'])) for d in standard['dimensions']}
    observed_weight = Decimal(0)
    dim_subtotals = {d: 0.0 for d in dims}
    dim_observed = {d: Decimal(0) for d in dims}
    rows = []
    for key, item in definition.items():
        value = record['items'].get(key, {'status': 'missing', 'reason': '输入未提供此项证据'})
        if not isinstance(value, dict):
            raise ValueError(f'{key}须为对象。')
        status = value.get('status', 'missing')
        if status not in VALID_STATUSES:
            raise ValueError(f'{key}状态无效。')
        evidence = value.get('evidence', [])
        if not isinstance(evidence, list) or any(not isinstance(e, str) or not e.strip() for e in evidence):
            raise ValueError(f'{key} evidence须为非空字符串组成的列表。')
        reason = value.get('reason', '')
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(f'{key}须说明评分或暂不评分的理由。')
        dimension = item['itemColumn']
        maximum = dims[dimension] * Decimal(str(item['weight'])) / 100
        raw = value.get('score')
        score = None
        contribution = None
        if status in {'observed', 'not_done'}:
            if not evidence:
                raise ValueError(f'{key}已评分项须附对话位置、时间码或完整片段的证据。')
            if status == 'not_done' and scope != 'complete':
                raise ValueError(f'{key}仅完整记录才能认定not_done；片段缺失应为missing。')
            if item['scoreType'] == 'yes_no':
                if raw not in ('有', '是', '无', '否'):
                    raise ValueError(f'{key}流程项只接受有/无（兼容历史是/否）。')
                score = Decimal(10) if raw in ('有', '是') else Decimal(0)
                if status == 'not_done' and score != 0:
                    raise ValueError(f'{key}认定未做时，流程项不能为有。')
            else:
                if isinstance(raw, bool) or raw is None or isinstance(raw, (dict, list)):
                    raise ValueError(f'{key}原始分须为0–10的有限数值。')
                try:
                    score = Decimal(str(raw))
                except InvalidOperation as error:
                    raise ValueError(f'{key}原始分不是数值。') from error
                if not score.is_finite() or not 0 <= score <= 10:
                    raise ValueError(f'{key}原始分须在0–10之间。')
            subtotal = float(score) * (item['weight'] / 100)
            contribution = subtotal * (float(dims[dimension]) / 10)
            dim_subtotals[dimension] += subtotal
            observed_weight += maximum
            dim_observed[dimension] += maximum
        elif raw is not None:
            raise ValueError(f'{key}未观察/缺失项必须留空，不能填0或默认满分。')
        rows.append({'key': key, 'number': item['number'], 'checkpoint': item['checkPoint'], 'dimension': dimension, 'status': status, 'rawScore': float(score) if score is not None else None, 'maximumContribution': rounded(maximum), 'contribution': rounded(contribution) if contribution is not None else None, 'evidence': evidence, 'reason': reason})
    dim_scores = {dim: subtotal * (float(dims[dim]) / 10) for dim, subtotal in dim_subtotals.items()}
    total = sum(dim_scores.values())
    all_scored = all(r['rawScore'] is not None for r in rows)
    complete = all_scored and scope == 'complete'
    missing_weight = Decimal(100) - observed_weight
    lower, upper = rounded(total), rounded(total + float(missing_weight))
    return {
        'kind': 'practice_evaluation_only', 'recordScope': scope, 'medium': medium,
        'scoredItems': sum(r['rawScore'] is not None for r in rows), 'totalItems': len(rows),
        'observedPoints': rounded(total), 'observedMaximum': rounded(observed_weight),
        'observedOnlyPercent': rounded(total / float(observed_weight) * 100) if observed_weight else None,
        'fullScoreInterval': [lower, upper],
        'completeTotal': rounded(total) if complete else None,
        'simulationThreshold': 80,
        'simulationResult': ('通过' if rounded(total) >= 80 else '未通过') if complete else None,
        'note': '仅完整且16项都有足够证据时给模拟总分/判定。局部归一化值不能当整场分数；80来自MyCoach模拟口径。',
        'dimensions': {dim: {'observedPoints': rounded(dim_scores[dim]), 'observedMaximum': rounded(dim_observed[dim]), 'fullMaximum': rounded(dims[dim])} for dim in dims},
        'items': rows,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, help='JSON文件，或-表示标准输入')
    args = parser.parse_args()
    try:
        record = json.load(sys.stdin) if args.input == '-' else json.loads(Path(args.input).read_text(encoding='utf-8'))
        result = calculate(record)
    except (ValueError, OSError, TypeError, KeyError) as error:
        parser.exit(2, f'计分失败：{error}\n')
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()

if __name__ == '__main__':
    main()
