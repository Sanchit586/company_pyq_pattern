"""Compact, resumable ledger of actually executed company/campus/year searches."""
import argparse
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'research/combination_search'


def attempts():
    for path in sorted((DIRECTORY / 'raw').glob('*.jsonl*')):
        if path.name.endswith('.jsonl.gz'):
            with gzip.open(path, 'rt', encoding='utf-8') as stream:
                lines = stream.read().splitlines()
        elif path.name.endswith('.jsonl'):
            lines = path.read_text(encoding='utf-8').splitlines()
        else:
            continue
        for line in lines:
            if line.strip():
                batch = json.loads(line)
                yield batch


def all_batches():
    result = {}
    for batch in attempts():
        key = (batch['company_slug'], batch['campus_id'])
        if (key not in result or all(q['status'] == 'searched' for q in batch['queries'])
                or not all(q['status'] == 'searched' for q in result[key]['queries'])):
            result[key] = batch
    return result


def summary():
    companies = json.loads((ROOT / 'data/companies.json').read_text(encoding='utf-8'))
    campuses = json.loads((ROOT / 'research/campuses.json').read_text(encoding='utf-8'))['campuses']
    expected = {(c['slug'], p['id'], y) for c in companies for p in campuses for y in (2023, 2024, 2025, 2026)}
    completed, failed, urls, batches, company_counts = set(), set(), set(), 0, {}
    for batch in all_batches().values():
        urls.update(source['url'] for source in batch.get('sources', []))
        batches += 1
        if {q['year'] for q in batch['queries']} != {2023, 2024, 2025, 2026}:
            raise ValueError('Incomplete calendar-year query batch')
        company_counts.setdefault(batch['company_slug'], 0)
        for query in batch['queries']:
            key = (batch['company_slug'], batch['campus_id'], query['year'])
            if key not in expected:
                raise ValueError('Unexpected combination')
            if query['status'] == 'searched':
                completed.add(key)
                company_counts[batch['company_slug']] += 1
            else:
                failed.add(key)
    return {'expected_combinations': len(expected), 'searched_combinations': len(completed),
            'failed_combinations': len(failed - completed), 'remaining_combinations': len(expected - completed),
            'company_campus_batches': batches,
            'recorded_query_attempts': sum(len(b['queries']) for b in attempts()),
            'unique_candidate_urls': len(urls),
            'all_combination_searches_executed': completed == expected,
            'source_review_complete': False, 'paper_coverage_complete': False,
            'company_search_counts': company_counts,
            'note': 'Four calendar-year queries share a candidate pool per company/campus batch. Hits are not verified OA evidence.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--summary', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--batch', nargs=2, metavar=('COMPANY_SLUG', 'CAMPUS_ID'))
    args = parser.parse_args()
    if args.batch:
        print(json.dumps(all_batches()[tuple(args.batch)], ensure_ascii=True, indent=2))
    elif args.resume:
        resume = {}
        for (company, campus), batch in all_batches().items():
            if all(q['status'] == 'searched' for q in batch['queries']):
                resume.setdefault(company, []).append(campus)
        print(json.dumps(resume))
    else:
        result = summary()
        DIRECTORY.mkdir(parents=True, exist_ok=True)
        (DIRECTORY / 'summary.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(result))


if __name__ == '__main__':
    main()
