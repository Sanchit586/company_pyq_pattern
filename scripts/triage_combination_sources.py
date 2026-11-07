"""List unreviewed primary-source candidates; never infer OA facts from hits."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit
from record_combination_search import all_batches

ROOT = Path(__file__).resolve().parents[1]


def canonical(url):
    parts = urlsplit(unquote(url))
    return urlunsplit((parts.scheme, parts.netloc.lower().removeprefix('www.'), parts.path.rstrip('/'), '', '')).lower()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--all-hosts', action='store_true', help='Include other blogs and discovery aggregators')
    args = parser.parse_args()
    companies = json.loads((ROOT / 'data/companies.json').read_text(encoding='utf-8'))
    done = {canonical(r['source_url']) for p in (ROOT / 'data/reports').glob('*.json')
            for r in json.loads(p.read_text(encoding='utf-8'))}
    done.update(canonical(r['url']) for r in json.loads((ROOT / 'research/exclusions.json').read_text(encoding='utf-8')))
    reviews = ROOT / 'research/combination_search/reviews.jsonl'
    if reviews.exists():
        done.update(canonical(json.loads(line)['source_url']) for line in reviews.read_text(encoding='utf-8').splitlines() if line)
    for review_file in (ROOT / 'research/combination_search/reviews').glob('*.jsonl'):
        done.update(canonical(json.loads(line)['source_url']) for line in review_file.read_text(encoding='utf-8').splitlines() if line)
    candidates = {}
    for batch in all_batches().values():
        if batch:
            for source in batch.get('sources', []):
                key = canonical(source['url'])
                if key in done:
                    continue
                title = source['title']
                if re.search(r'Microsoft Word\s*-|walk.in|assistant prof|faculty|accreditation|accredited|approval process|recruitment of teachers', title, re.I):
                    continue
                host = urlsplit(source['url']).netloc.lower()
                primary = any(s in host for s in ['geeksforgeeks.org', 'medium.com', 'leetcode.com', 'codeforces.com',
                                                 'github.com', 'github.io', 'thejoboverflow.com'])
                pdf = bool(re.search(r'\.pdf(?:[?#]|$)', source['url'], re.I))
                if not (primary or pdf or args.all_hosts):
                    continue
                if pdf and not re.search(r'internpedia|placementpedia|placement.*handbook|interview experiences|placement.*experience', title, re.I):
                    continue
                if not re.search(r'interview|\bOA\b|assessment|handbook|internpedia|placementpedia', title, re.I):
                    continue
                if re.search(r'Archives|Interview Questions & Experience|All interview|Company Questions|Last \d+ days', title, re.I):
                    continue
                score = 3 * bool(re.search(r'\bOA\b|assessment', title, re.I))
                score += 2 * bool(re.search(r'IIT|NIT|IIIT|BITS', title, re.I))
                score += bool(re.search(r'202[3-6]', title))
                score += pdf
                company_hints = [c['name'] for c in companies if any(
                    re.sub(r'[^a-z0-9]', '', s.lower()) in re.sub(r'[^a-z0-9]', '', title.lower())
                    for s in [c['name'], *c['aliases']] if len(s) > 2)]
                if not company_hints and not pdf:
                    continue
                if key not in candidates:
                    candidates[key] = {**source, 'company_hints': company_hints, 'discovered_for': [], 'priority': score}
                context = batch['company'] + ' / ' + batch['campus']
                if context not in candidates[key]['discovered_for'] and len(candidates[key]['discovered_for']) < 3:
                    candidates[key]['discovered_for'].append(context)
    rows = sorted(candidates.values(), key=lambda x: (-x['priority'], x['url']))
    print(json.dumps({'unreviewed_candidates': len(rows), 'candidates': rows[args.offset:args.offset+args.limit]},
                     ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
