"""Validate research integrity and generated artifacts without network access."""
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from build_dataset import ROOT, YEARS, eligible, load_reports, read_json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    companies = read_json(ROOT / 'data/companies.json')
    require(len(companies) == 52, 'Expected all 52 requested companies')
    names = {c['name'] for c in companies}
    require(len(names) == len({c['slug'] for c in companies}) == 52, 'Duplicate company name/slug')
    references = {r['url']: r['difficulty'] for r in read_json(ROOT / 'research/difficulty_references.json')}
    reports = load_reports()
    require(len({r['id'] for r in reports}) == len(reports), 'Duplicate report ID')
    require(len({(r['company'], r['source_url']) for r in reports}) == len(reports), 'Duplicate source report')
    allowed_report = {'id', 'company', 'oa_year', 'year_candidates', 'year_basis', 'campus', 'campus_group',
                      'campus_basis', 'role', 'source_url', 'source_type', 'access', 'assessment_kind', 'scope',
                      'topics', 'notes', 'published_date', 'supporting_urls', 'reported_oa_difficulty',
                      'overall_difficulty', 'overall_difficulty_basis'}
    allowed_topic = {'topic', 'difficulty', 'difficulty_basis', 'rationale', 'difficulty_reference',
                     'difficulty_range', 'reported_difficulty'}
    bases = {'estimated', 'official_leetcode', 'reported', 'reported_range', 'reported_oa_range', 'unknown'}
    levels = {'Easy', 'Medium', 'Hard', 'Unknown'}
    for report in reports:
        rid = report['id']
        require(not (set(report) - allowed_report), f'{rid}: unexpected fields (question text is not allowed)')
        require(report['company'] in names, f'{rid}: unknown company')
        require(report['oa_year'] is None or report['oa_year'] in YEARS, f'{rid}: year outside scope')
        require(report['year_basis'] and report['campus_basis'] and report['notes'], f'{rid}: missing evidence notes')
        require(urlparse(report['source_url']).scheme == 'https', f'{rid}: missing HTTPS source')
        if report['oa_year'] is None:
            require(report['scope'] != 'supported', f'{rid}: undated report cannot enter dated tables')
        if report['assessment_kind'] == 'mcq_only':
            require(not report['topics'], f'{rid}: MCQ-only report must not contribute coding topics')
        for topic in report['topics']:
            require(not (set(topic) - allowed_topic), f'{rid}: unexpected topic fields')
            require(topic['topic'] and topic['rationale'], f'{rid}: topic or rationale absent')
            require(topic['difficulty'] in levels, f'{rid}: invalid difficulty')
            require(topic['difficulty_basis'] in bases, f'{rid}: invalid difficulty basis')
            if topic['difficulty_basis'] == 'official_leetcode':
                require(references.get(topic.get('difficulty_reference')) == topic['difficulty'],
                        f'{rid}: official difficulty has no matching checked reference')
            if topic['difficulty_basis'] in {'reported_range', 'reported_oa_range'}:
                require(topic['difficulty'] == 'Unknown' and len(topic.get('difficulty_range', [])) == 2,
                        f'{rid}: range must not be silently converted to a single level')
    main_rows = read_json(ROOT / 'data/topics.json')
    other_rows = read_json(ROOT / 'data/unverified_topics.json')
    by_id = {r['id']: r for r in reports}
    expected = {(r['id'], i) for r in reports if eligible(r) for i in range(1, len(r['topics']) + 1)}
    require(len(main_rows) == len(expected), 'Main export is missing or duplicating observations')
    require({(r['report_id'], int(r['observation_id'].split('-T')[1])) for r in main_rows} == expected,
            'Main observation identifiers do not match curated reports')
    for row in main_rows + other_rows:
        report = by_id[row['report_id']]
        index = int(row['observation_id'].split('-T')[1]) - 1
        require(all(row[k] == v for k, v in report['topics'][index].items()), f"Stale export: {row['observation_id']}")
    require(all(eligible(by_id[r['report_id']]) for r in main_rows), 'Uncertain report leaked into main export')
    require(all(not eligible(by_id[r['report_id']]) for r in other_rows), 'Qualifying report in unverified export')
    coverage = read_json(ROOT / 'data/coverage.json')
    require(len(coverage) == 208 and {(r['company'], r['oa_year']) for r in coverage} ==
            {(name, year) for name in names for year in YEARS}, 'Coverage must include all 208 company/year pairs')
    require(all(r['complete'] is False for r in coverage), 'Exhaustive coverage is not established')
    counts = Counter((r['company'], r['oa_year']) for r in main_rows)
    require(all(r['topic_observations'] == counts[r['company'], r['oa_year']] for r in coverage), 'Stale coverage counts')
    for company in companies:
        page = ROOT / 'companies' / (company['slug'] + '.md')
        require(page.exists(), 'Missing company page: ' + company['name'])
        content = page.read_text(encoding='utf-8')
        require(all(f'## {year}\n' in content for year in YEARS), f'{page.name}: missing year section')
    for page in [ROOT / 'README.md', ROOT / 'COVERAGE.md', *sorted((ROOT / 'companies').glob('*.md'))]:
        for target in re.findall(r'\]\(([^)]+)\)', page.read_text(encoding='utf-8')):
            if not target.startswith(('https://', '#')):
                require((page.parent / target.split('#')[0]).exists(), f'{page.name}: broken local link {target}')
    # Temporary downloaded question media must never become part of the delivered dataset.
    require(not (ROOT / 'tmp').exists(), 'Remove temporary source PDFs/images before delivery')
    print(f'PASS: 52 companies, 208 year cells, {len(reports)} reports, {len(main_rows)} qualifying topic observations; exports and evidence rules checked.')


if __name__ == '__main__':
    main()
