"""Collect public source metadata, never question statements or private content.

Uses ordinary unauthenticated HTTP requests. No logins, paywall bypass, or hidden APIs.
The output is a discovery queue, NOT verified OA evidence.
"""
import argparse
import concurrent.futures
import json
import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current = None
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs = dict(attrs)
            href = attrs.get('href', '')
            self.current = [href, []]

    def handle_data(self, data):
        if self.current is not None:
            self.current[1].append(data)

    def handle_endtag(self, tag):
        if tag == 'a' and self.current is not None:
            href, parts = self.current
            title = ' '.join(' '.join(parts).split())
            self.links.append((href, title))
            self.current = None


def collect(company):
    # The site's public tag URLs are discovered through web search.
    aliases = {
        'Goldman Sachs': 'goldmansachs', 'DE Shaw': 'deshaw',
        'Samsung (R&D)': 'samsung', 'Meta (Facebook)': 'facebook',
        'Graviton Research Capital': 'graviton', 'Squarepoint Capital': 'squarepoint',
        'IMC Trading': 'imc', 'Eternal (Zomato)': 'zomato',
        'Capital One': 'capitalone', 'JP Morgan': 'JP-Morgan',
        'HCL Technologies': 'HCL', 'LTIMindtree': 'LTI',
    }
    tag = aliases.get(company['name'], company['name'].replace(' ', '-'))
    found, visited, errors = {}, [], []
    for page in range(1, 5):
        url = 'https://thejoboverflow.com/?' + urllib.parse.urlencode({'tag': tag, 'page': page})
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (public source research)'})
            with urllib.request.urlopen(req, timeout=25) as response:
                html = response.read().decode('utf-8', 'replace')
            parser = Links()
            parser.feed(html)
            posts = [(href, title) for href, title in parser.links
                     if re.match(r'^/(?:p/p\d+|problem/\d+)', href) and title and not title.startswith('Answer:')]
            new = 0
            for href, title in posts:
                link = urllib.parse.urljoin(url, href)
                if link not in found:
                    found[link] = {'title': title, 'url': link,
                                   'campus_title_hint': bool(re.search(r'\b(?:IIT|NIT|IIIT|BITS|MANIT|MNNIT|MNIT)\b', title, re.I)),
                                   'year_title_hints': sorted(set(re.findall(r'\b202[3-6]\b', title)))}
                    new += 1
            visited.append(url)
            if new == 0:
                break
            time.sleep(0.4)
        except Exception as exc:
            errors.append({'url': url, 'error': str(exc)})
            break
    return {'company': company['name'], 'accessed_at': '2026-11-06',
            'index_urls': visited, 'errors': errors, 'sources': list(found.values())}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    companies = json.loads((ROOT / 'data/companies.json').read_text(encoding='utf-8'))
    if args.limit:
        companies = companies[:args.limit]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(collect, companies))
    target = ROOT / 'research/archive_index.json'
    target.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'companies': len(results), 'sources': sum(len(r['sources']) for r in results),
                      'errors': sum(len(r['errors']) for r in results)}))


if __name__ == '__main__':
    main()
