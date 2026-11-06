"""Temporarily render public linked PDFs and print local OCR for research.

Question text is never exported as a repository data artifact. Delete tmp/ after review.
Use only attachments exposed on public archive pages; no authenticated requests.
"""
import argparse
import json
import os
import re
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ids', required=True)
    parser.add_argument('--chars-per-page', type=int, default=1150)
    args = parser.parse_args()
    ids = set(args.ids.split(','))
    records = json.loads((ROOT / 'research/archive_access.json').read_text(encoding='utf-8'))
    folder = ROOT / 'tmp/pdfs'
    folder.mkdir(parents=True, exist_ok=True)
    for record in records:
        post_id = re.search(r'/p/p(\d+)', record['url']).group(1)
        if post_id not in ids:
            continue
        attachments = [url for url in record.get('public_attachments', []) if 'drive.google.com/file/d/' in url]
        for i, attachment in enumerate(attachments):
            file_id = attachment.split('/file/d/')[1].split('/')[0]
            download = 'https://drive.google.com/uc?export=download&id=' + file_id
            pdf = folder / f'{post_id}-{i}.pdf'
            try:
                with urllib.request.urlopen(download, timeout=35) as response:
                    data = response.read()
                if not data.startswith(b'%PDF'):
                    print(json.dumps({'source': record['url'], 'attachment': attachment, 'status': 'not_public_pdf'}), flush=True)
                    continue
                pdf.write_bytes(data)
                info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
                pages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
                print(json.dumps({'source': record['url'], 'attachment': attachment, 'pages': pages}), flush=True)
                for page in range(1, pages + 1):
                    image_prefix = folder / f'{post_id}-{i}-p{page}'
                    subprocess.run(['pdftoppm', '-f', str(page), '-singlefile', '-scale-to', '1900', '-png', str(pdf), str(image_prefix)], check=True, capture_output=True)
                    ocr = subprocess.check_output(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(ROOT / 'scripts/ocr_public_image.ps1'), '-ImagePath', str(image_prefix) + '.png'], text=True, errors='replace')
                    print(f'PAGE {page}: ' + ocr[:args.chars_per_page].encode('ascii', 'backslashreplace').decode(), flush=True)
            except Exception as exc:
                print(json.dumps({'source': record['url'], 'attachment': attachment, 'error': str(exc)}), flush=True)


if __name__ == '__main__':
    main()
