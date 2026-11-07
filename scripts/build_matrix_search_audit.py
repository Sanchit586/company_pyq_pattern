"""Build an auditable search matrix from executed requests, not planned queries."""
import json
from collections import Counter
from pathlib import Path

from record_combination_search import DIRECTORY, ROOT, all_batches, summary

YEARS = (2023, 2024, 2025, 2026)


def reviews():
    paths = [DIRECTORY / 'reviews.jsonl', *sorted((DIRECTORY / 'reviews').glob('*.jsonl'))]
    return [json.loads(line) for path in paths if path.exists()
            for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def main():
    progress = summary()
    companies = json.loads((ROOT / 'data/companies.json').read_text(encoding='utf-8'))
    campuses = json.loads((ROOT / 'research/campuses.json').read_text(encoding='utf-8'))['campuses']
    batches = all_batches()
    decisions = reviews()
    counts = Counter()
    for batch in batches.values():
        for query in batch['queries']:
            if query['status'] == 'searched':
                counts[batch['company_slug'], query['year']] += 1
    progress['reviewed_source_decisions'] = len(decisions)
    progress['review_decision_counts'] = dict(Counter(r['decision'] for r in decisions))
    (DIRECTORY / 'summary.json').write_text(json.dumps(progress, indent=2) + '\n', encoding='utf-8')
    cells = [{'company': c['name'], 'company_slug': c['slug'], 'year': y,
              'expected_campus_searches': len(campuses), 'searched_campuses': counts[c['slug'], y]}
             for c in companies for y in YEARS]
    (DIRECTORY / 'coverage.json').write_text(json.dumps(cells, indent=2) + '\n', encoding='utf-8')
    lines = ['# Company × campus × year search audit', '',
             f"Searches executed: **{progress['searched_combinations']:,} / {progress['expected_combinations']:,}**. "
             f"Remaining: **{progress['remaining_combinations']:,}**; unresolved failed combinations: "
             f"**{progress['failed_combinations']:,}**.", '',
             f"Recorded query attempts including retries: {progress['recorded_query_attempts']:,}. "
             'The coverage total counts each company/campus/year combination once.', '',
             'Scope: the [52 companies](data/companies.json), [88 campuses](research/campuses.json), '
             'and calendar years 2023–2026. Each cell below counts campus-specific searches out of 88.', '',
             '| Company | 2023 | 2024 | 2025 | 2026 | Total / 352 |',
             '|---|---:|---:|---:|---:|---:|']
    for company in companies:
        values = [counts[company['slug'], y] for y in YEARS]
        lines.append(f"| [{company['name']}](companies/{company['slug']}.md) | "
                     + ' | '.join(map(str, values)) + f' | {sum(values)} |')
    lines += ['', '## What the audit establishes', '',
              '- [Raw execution ledger](research/combination_search/raw) records actual query strings, '
              'calendar year, request status, search date, and returned source titles/URLs. '
              'Failed attempts remain in the ledger and are superseded only by executed retries.',
              '- Completed checkpoints may be losslessly compressed as `.jsonl.gz` to conserve disk space. '
              'Inspect any batch with `python scripts/record_combination_search.py --batch google iit-bombay`; '
              'the reader supports both compressed and plain checkpoints.',
              '- Each company/campus request contains four separate year queries. The search tool returns '
              'a shared result pool for the request; a hit is not attributed to all four years.',
              '- A successful search may return no relevant public account. The count establishes query '
              'execution, not the existence of an OA or completion of a paper collection.',
              '- [Source review decisions](research/combination_search/reviews) and '
              '[initial decisions](research/combination_search/reviews.jsonl) explain selected inclusions '
              'and exclusions. Unreviewed URLs remain discovery metadata.',
              '- [Curated reports](data/reports) establish campus, assessment round, year, topic, and '
              'difficulty evidence separately. No question statements are retained.', '',
              f"Unique candidate URLs returned: {progress['unique_candidate_urls']:,}. "
              f"Recorded source-review decisions in this matrix pass: {len(decisions)}.", '',
              '**All OA questions found: not established. Source review complete: no.** '
              'Search indexes omit private and unindexed reports; titles, publication dates, and role years '
              'cannot establish task-level historical evidence. The topic dataset remains partial.', '']
    (ROOT / 'MATRIX_SEARCHES.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(progress))


if __name__ == '__main__':
    main()
