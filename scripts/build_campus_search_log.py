"""Expose the distinction between discovery queries and actual paper coverage."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    campuses = read(ROOT / 'research/campuses.json')['campuses']
    companies = read(ROOT / 'data/companies.json')
    matrix = None
    if (ROOT / 'research/combination_search/raw').exists():
        from record_combination_search import summary as matrix_summary
        matrix = matrix_summary()
    lines = ['# Campus search audit', '',
             'The first research pass did not search every campus separately. This audit was added on November 7, 2026 to make that gap visible.', '',
             '**Q means an exact campus/alias + calendar year + online-assessment phrase was searched. It does not mean the campus paper pool or all 52 companies were reviewed.**', '',
             'The roster has 88 campuses and 352 campus/year discovery searches. A full company/campus/year matrix has '
             + f'{len(campuses) * len(companies) * 4:,} combinations. Its actual execution is recorded separately in the '
             '[company/campus/year audit](MATRIX_SEARCHES.md).', '',
             'Sources returned by discovery can be unrelated, old, off-campus, or descriptions of later interviews. Only reviewed and qualifying reports contribute to the topic dataset.', '',
             '| Campus | Group | 2023 | 2024 | 2025 | 2026 | Search metadata |',
             '|---|---|---|---|---|---|---|']
    queries = 0
    sources = set()
    for campus in campuses:
        path = ROOT / 'research/campus_searches' / (campus['id'] + '-oa.json')
        log = read(path) if path.exists() else {'queries': []}
        years = {q['year'] for q in log['queries']}
        queries += len(log['queries'])
        sources.update(s['url'] for q in log['queries'] for s in q['results'])
        cells = ['Q' if year in years else 'Pending' for year in (2023, 2024, 2025, 2026)]
        lines.append('| ' + campus['name'] + ' | ' + campus['group'] + ' | ' + ' | '.join(cells)
                     + f" | [Log](research/campus_searches/{path.name}) |")
    (ROOT / 'CAMPUS_SEARCHES.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    summary = {'as_of': '2026-11-07', 'roster_campuses': len(campuses),
               'executed_campus_year_queries': queries, 'unique_result_urls': len(sources),
               'company_campus_year_combinations': len(campuses) * len(companies) * 4,
               'individual_company_campus_year_search_complete': bool(matrix and matrix['all_combination_searches_executed']),
               'paper_coverage_complete': False,
               'note': 'Search execution is not source review or exhaustive question coverage.'}
    (ROOT / 'research/campus_search_summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
