"""Read ordinary public student-body PDF links; retain no extracted source text."""
import argparse
import json
import re
import urllib.request
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    origin = parser.add_mutually_exclusive_group(required=True)
    origin.add_argument('--id')
    origin.add_argument('--drive-id', help='Ordinary public Google Drive PDF attachment identifier')
    parser.add_argument('--pages', help='Comma-separated one-based PDF page numbers')
    parser.add_argument('--index', action='store_true')
    parser.add_argument('--compact', action='store_true', help='Print requested-company OA leads only')
    parser.add_argument('--memory', action='store_true', help='Read a public download in memory without source files')
    args = parser.parse_args()
    sources = json.loads((ROOT / 'research/handbooks.json').read_text(encoding='utf-8'))
    if args.drive_id:
        if not re.fullmatch(r'[A-Za-z0-9_-]+', args.drive_id):
            raise ValueError('Invalid public Drive identifier')
        source = {'drive_id': args.drive_id,
                  'source_url': 'https://drive.google.com/file/d/' + args.drive_id + '/view'}
        args.memory = True
    else:
        source = next(s for s in sources if s['id'] == args.id)
    folder = ROOT / 'tmp/handbooks'
    if not args.memory:
        folder.mkdir(parents=True, exist_ok=True)
    path = folder / ((args.id or args.drive_id) + '.pdf')
    if args.memory or not path.exists():
        req = urllib.request.Request('https://drive.google.com/uc?export=download&id=' + source['drive_id'],
                                     headers={'User-Agent': 'Mozilla/5.0 (public source review)'})
        with urllib.request.urlopen(req, timeout=90) as response:
            content = response.read()
        if not content.startswith(b'%PDF'):
            raise ValueError('Public PDF download unavailable; no authentication or bypass attempted')
        if not args.memory:
            path.write_bytes(content)
    reader = PdfReader(BytesIO(content) if args.memory else path)
    print(json.dumps({'source': source['source_url'], 'pages': len(reader.pages)}))
    pages = {int(n) for n in args.pages.split(',')} if args.pages else None
    for number, page in enumerate(reader.pages, 1):
        if pages is not None and number not in pages:
            continue
        body = page.extract_text() or ''
        if args.compact:
            companies = json.loads((ROOT / 'data/companies.json').read_text(encoding='utf-8'))
            aliases = {'Eternal (Zomato)': ['Zomato'], 'DE Shaw': ['DE Shaw', 'D E Shaw', 'DEShaw'],
                       'Samsung (R&D)': ['Samsung'], 'Graviton Research Capital': ['Graviton'],
                       'Squarepoint Capital': ['Squarepoint'], 'JP Morgan': ['JP Morgan', 'JPMorgan'],
                       'Meta (Facebook)': ['Meta', 'Facebook'], 'HCL Technologies': ['HCL']}
            compact_body = re.sub(r'\s+', ' ', body)
            names = [c['name'] for c in companies if any(re.search(r'\b' + re.escape(s) + r'\b', compact_body, re.I)
                     for s in aliases.get(c['name'], [c['name']]))]
            if not names:
                continue
            matches = list(re.finditer(r'online assessment|coding test|coding round|\bOA\b|online test', compact_body, re.I))
            if not matches:
                continue
            snippets = ' / '.join(compact_body[max(0,m.start()-30):m.end()+260] for m in matches[:2])
            print(('PAGE ' + str(number) + ' | ' + ', '.join(names) + ' | ' + snippets).encode('ascii', 'backslashreplace').decode())
            continue
        if args.index and not re.search(r'online assessment|coding test|coding round|\bOA\b|online test', body, re.I):
            continue
        if args.index:
            matching = []
            for match in re.finditer(r'online assessment|coding test|coding round|\bOA\b|online test', body, re.I):
                matching.append(body[max(0, match.start()-130):match.end()+650])
            body = body[:170] + '\n' + '\n'.join(matching)
        print(('PDF PAGE ' + str(number) + '\n' + body[:1800 if args.index else 11000]).encode('ascii', 'backslashreplace').decode())


if __name__ == '__main__':
    main()
