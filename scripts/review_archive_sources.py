"""Review public archive pages; persist metadata only, never problem text.

Optional --preview prints public excerpts to the research terminal for review.
Requires beautifulsoup4 in the local Python environment.
"""
import argparse
import concurrent.futures
import json
import re
import urllib.request
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def read_source(item):
    try:
        req = urllib.request.Request(item['url'], headers={'User-Agent': 'Mozilla/5.0 (public source research)'})
        with urllib.request.urlopen(req, timeout=25) as response:
            soup = BeautifulSoup(response.read(), 'html.parser')
        heading = soup.find('h1')
        title = heading.get_text(' ', strip=True) if heading else item['title']
        content = soup.select_one('.post .body .content.wrap-text')
        body = content.get_text(' ', strip=True) if content else ''
        dates = [t.get('datetime') for t in soup.find_all('time') if t.get('datetime')]
        locked = 'premium members' in soup.get_text(' ', strip=True).lower()
        attachments = []
        if content:
            for element in content.find_all(['img', 'iframe']):
                src = element.get('src', '')
                if src.startswith('https://'):
                    attachments.append(src)
        source_tags = sorted({a.get_text(' ', strip=True) for a in soup.find_all('a', href=True)
                              if '?tag=' in a['href'] and len(a.get_text(' ', strip=True)) < 70})
        result = {**item, 'public_title': title, 'date_metadata': dates,
                  'access': 'public_excerpt' if locked and body else 'title_only' if locked else 'public_page',
                  'public_body_characters': len(body), 'public_attachments': attachments,
                  'source_tags': source_tags,
                  'campus_body_hint': bool(re.search(r'\b(?:IIT|NIT|IIIT|BITS|MANIT|MNNIT|MNIT)\b', body, re.I))}
        return result, body
    except Exception as exc:
        return {**item, 'access': 'fetch_failed', 'error': str(exc)}, ''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ids', help='Comma-separated post ids, e.g. 1301,1462')
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--all-years', action='store_true', help='Access audit of all 2023–2026 title leads')
    args = parser.parse_args()
    index = json.loads((ROOT / 'research/archive_index.json').read_text(encoding='utf-8'))
    ids = set(args.ids.split(',')) if args.ids else None
    selected = {}
    for company in index:
        for source in company['sources']:
            post_id = re.search(r'/p/p(\d+)', source['url']).group(1)
            include = bool(source['year_title_hints']) if args.all_years else source['campus_title_hint']
            if (ids and post_id in ids) or (ids is None and include):
                selected[source['url']] = {'company': company['company'], **source}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        reviewed = list(pool.map(read_source, selected.values()))
    if not ids:
        target = 'archive_year_access.json' if args.all_years else 'archive_access.json'
        (ROOT / 'research' / target).write_text(
            json.dumps([row for row, _ in reviewed], indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    if not ids and not args.preview:
        print(json.dumps({'reviewed': len(reviewed), 'public_pages': sum(r['access'] == 'public_page' for r, _ in reviewed)}))
        return
    for row, body in reviewed:
        print(json.dumps(row, ensure_ascii=True))
        if args.preview:
            print('PUBLIC REVIEW TEXT:', body[:9000].encode('ascii', 'backslashreplace').decode())


if __name__ == '__main__':
    main()
