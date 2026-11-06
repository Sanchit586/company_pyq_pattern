"""Build browsable topic-only outputs from curated public-source reports (stdlib)."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
YEARS = (2023, 2024, 2025, 2026)
AS_OF = '2026-11-06'
ALLOWED_GROUPS = {'IIT', 'NIT', 'IIIT', 'BITS'}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def load_reports():
    return [r for path in sorted((ROOT / 'data/reports').glob('*.json')) for r in read_json(path)]


def eligible(report):
    return (report['scope'] == 'supported' and report['oa_year'] in YEARS
            and report['campus_group'] in ALLOWED_GROUPS and report['assessment_kind'] == 'coding')


def difficulty_text(topic):
    if topic.get('difficulty_range'):
        return '–'.join(topic['difficulty_range']) + ' (range only)'
    return topic.get('difficulty') or 'Unknown'


def safe(text):
    if isinstance(text, list):
        text = ', '.join(map(str, text))
    return str(text or 'Not stated').replace('|', '\\|').replace('\n', ' ')


def basis_text(topic):
    basis = topic['difficulty_basis']
    basis = 'official' if basis == 'official_leetcode' else 'estimate' if basis == 'estimated' else basis.replace('_', ' ')
    return f"[{basis}]({topic['difficulty_reference']})" if topic.get('difficulty_reference') else basis


def main():
    companies = read_json(ROOT / 'data/companies.json')
    reports = load_reports()
    access_path = ROOT / 'research/archive_year_access.json'
    access = read_json(ROOT / 'research/archive_access.json')
    if access_path.exists():
        access = list({r['url']: r for r in access + read_json(access_path)}.values())
    known_sources = {r['source_url'] for r in reports}
    exclusions_path = ROOT / 'research/exclusions.json'
    if exclusions_path.exists():
        known_sources.update(r['url'] for r in read_json(exclusions_path))
    observations, unverified, coverage = [], [], []
    for report in reports:
        for position, topic in enumerate(report['topics'], 1):
            row = {k: report[k] for k in ('company', 'oa_year', 'year_basis', 'campus', 'campus_group',
                                         'campus_basis', 'scope', 'source_url')}
            row.update({'report_id': report['id'], 'observation_id': f"{report['id']}-T{position:02}",
                        **topic})
            (observations if eligible(report) else unverified).append(row)
    docs = ROOT / 'companies'
    docs.mkdir(exist_ok=True)
    index = ['# Company coverage, 2023–2026', '',
             'Public-source research as of ' + AS_OF + '. Every cell is partial; no cell claims a complete paper set.', '',
             'T = usable topic evidence; R = coding report without topics; L = source lead/access gap; — = no qualifying dated evidence.', '',
             '| Company | 2023 | 2024 | 2025 | 2026 |', '|---|---|---|---|---|']
    status_counts = Counter()
    for company in companies:
        name = company['name']
        company_reports = [r for r in reports if r['company'] == name]
        lines = ['# ' + name, '', 'Scope: campus OA coding at IITs, NITs, IIITs, and BITS; calendar years 2023–2026.', '',
                 'Research date: ' + AS_OF + '. Public reports are incomplete. Counts represent source observations, not unique questions.', '',
                 'Difficulty: **official** = checked LeetCode match; **estimate** = researcher estimate on that scale; **reported** = source author’s label. Ranges and unknowns remain unresolved.', '']
        cells = []
        for year in YEARS:
            selected = [r for r in company_reports if eligible(r) and r['oa_year'] == year]
            topics = [r for r in observations if r['company'] == name and r['oa_year'] == year]
            leads = [r for r in access if r['company'] == name and str(year) in r.get('year_title_hints', [])
                     and r['url'] not in known_sources and (r.get('campus_title_hint') or r.get('campus_body_hint')
                     or any(tag.lower() in {'iit', 'iits', 'nit', 'nits', 'iiit', 'iiits', 'bits'} for tag in r.get('source_tags', [])))]
            status, cell = ('topics_found', f'T ({len(topics)})') if topics else (
                ('report_without_topics', 'R') if selected else ('source_lead_gap', 'L') if leads
                else ('no_qualifying_public_evidence_found', '—'))
            status_counts[status] += 1
            coverage.append({'company': name, 'oa_year': year, 'status': status, 'complete': False,
                             'topic_observations': len(topics), 'curated_coding_reports': len(selected),
                             'unreviewed_or_access_limited_campus_leads': len(leads),
                             'report_ids': [r['id'] for r in selected]})
            cells.append(cell)
            lines += [f'## {year}', '', f'Coverage: `{status}`. Completeness: **not established**.', '']
            if topics:
                lines += ['| Topic | Difficulty | Basis | Campus | Evidence |', '|---|---|---|---|---|']
                for row in topics:
                    basis = basis_text(row)
                    lines.append(f"| {safe(row['topic'])} | {difficulty_text(row)} | {basis} | {safe(row['campus'])} | [{row['report_id']}]({row['source_url']}) |")
                lines.append('')
            for report in selected:
                overall = report.get('reported_oa_difficulty') or report.get('overall_difficulty')
                lines += [f"- [{report['id']}]({report['source_url']}), {safe(report['campus'])}. "
                          + ('No specific OA topics disclosed. ' if not report['topics'] else '')
                          + (f'Overall source rating: {safe(overall)}. ' if overall else '')
                          + safe(report['notes']) + f" Year evidence: `{report['year_basis']}`."]
            if selected:
                lines.append('')
            if not topics and not selected:
                lines += ['No qualifying dated topic evidence has been curated. This does not establish that no OA took place.', '']
            if leads:
                lines += ['Additional campus leads (metadata only; topics not inferred from titles):', '']
                for lead in leads:
                    lines.append(f"- [Source]({lead['url']}): `{lead['access']}`. Campus/year hints still need confirmation.")
                lines.append('')
        uncertain = [r for r in company_reports if not eligible(r)]
        lines += ['## Evidence outside the main dated coding tables', '']
        if not uncertain:
            lines += ['None curated.', '']
        for report in uncertain:
            lines += [f"### [{report['id']}]({report['source_url']})", '',
                      f"Year: {report['oa_year'] or 'unconfirmed'}; campus: {safe(report['campus'])}; status: `{report['scope']}`; assessment: `{report['assessment_kind']}`.", '',
                      safe(report['notes']), '']
            if report['topics']:
                lines += ['| Topic | Difficulty | Basis |', '|---|---|---|']
                for topic in report['topics']:
                    lines.append(f"| {safe(topic['topic'])} | {difficulty_text(topic)} | {basis_text(topic)} |")
                lines.append('')
        (docs / (company['slug'] + '.md')).write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
        index.append(f"| [{name}](companies/{company['slug']}.md) | " + ' | '.join(cells) + ' |')
    (ROOT / 'COVERAGE.md').write_text('\n'.join(index) + '\n', encoding='utf-8')
    write_json(ROOT / 'data/topics.json', observations)
    write_json(ROOT / 'data/unverified_topics.json', unverified)
    write_json(ROOT / 'data/coverage.json', coverage)
    queries = [q for path in (ROOT / 'research/searches').glob('*.json') for q in read_json(path)['queries']]
    summary = {'as_of': AS_OF, 'years': list(YEARS), 'companies': len(companies), 'company_year_cells': len(coverage),
               'curated_reports': len(reports), 'qualifying_coding_reports': sum(eligible(r) for r in reports),
               'qualifying_topic_observations': len(observations), 'unverified_topic_observations': len(unverified),
               'companies_with_qualifying_topics': len({r['company'] for r in observations}),
               'recorded_company_search_queries': len(queries), 'unique_recorded_company_search_queries': len(set(queries)),
               'archive_access_audits': len(access), 'coverage_status_counts': dict(status_counts), 'complete': False}
    write_json(ROOT / 'data/summary.json', summary)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
