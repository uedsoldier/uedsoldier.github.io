#!/usr/bin/env python3
"""
Merge per-language section files into the master `data/portfolio.json`.

Example: data/es/education.json -> portfolio.json.languages.es.education

Usage:
  python3 scripts/merge_into_portfolio.py --input data/portfolio.json --fields education

Options:
  --data-dir    Root directory where per-lang files live (default: data)
  --fields      Comma-separated list of section keys to merge (default: education)
  --backup      Create a timestamped backup of the original portfolio.json
  --dry-run     Show planned changes without writing
"""
import argparse
import json
import os
import shutil
import sys
from datetime import datetime


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json_atomic(path, data):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    os.replace(tmp, path)


def merge_sections(portfolio_path, data_dir='data', fields=None, files=None, backup=False, dry_run=False):
    """
    Merge either per-lang files under `data/<lang>/<field>.json` (old behavior) or
    take bundle files like `data/education.json` which contain per-language keys.

    - If `files` is provided (list of file paths), each file is assumed to be a bundle
      with top-level language keys (e.g. 'es', 'en'). The section key is derived from
      the filename (basename without extension), e.g. 'education.json' -> 'education'.
    - Otherwise, `fields` and `data_dir` are used: look for `data/<lang>/<field>.json`.
    """
    if fields is None:
        fields = []

    portfolio = load_json(portfolio_path)

    if backup and not dry_run:
        ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        bak = portfolio_path + f'.bak.{ts}'
        shutil.copyfile(portfolio_path, bak)
        print(f'Backup written: {bak}')

    changed = False

    # Case A: files provided that contain languages at top-level (e.g. data/education.json)
    if files:
        for fpath in files:
            if not os.path.exists(fpath):
                print(f'Skipping missing file: {fpath}')
                continue
            try:
                bundle = load_json(fpath)
            except Exception as e:
                print(f'Failed to read {fpath}: {e}', file=sys.stderr)
                continue

            field = os.path.splitext(os.path.basename(fpath))[0]

            if not isinstance(bundle, dict):
                print(f'Expected object in {fpath}, skipping', file=sys.stderr)
                continue

            for lang, lang_content in bundle.items():
                # lang_content may be {field: value} or direct value
                if isinstance(lang_content, dict) and field in lang_content:
                    value = lang_content[field]
                else:
                    value = lang_content

                # ensure language object exists in portfolio
                if 'languages' not in portfolio:
                    portfolio['languages'] = {}
                if lang not in portfolio['languages'] or not isinstance(portfolio['languages'][lang], dict):
                    portfolio['languages'][lang] = {}

                # Always overwrite when merging from bundle files
                print(f'Overwriting portfolio.languages.{lang}.{field} (from {fpath})')
                portfolio['languages'][lang][field] = value
                changed = True

    # Case B: old behavior - per-lang directories with <field>.json
    else:
        for lang in os.listdir(data_dir):
            lang_dir = os.path.join(data_dir, lang)
            if not os.path.isdir(lang_dir):
                continue

            for field in fields:
                src = os.path.join(lang_dir, f'{field}.json')
                if not os.path.exists(src):
                    continue
                try:
                    payload = load_json(src)
                except Exception as e:
                    print(f'Failed to read {src}: {e}', file=sys.stderr)
                    continue

                # payload may be {field: value} or direct value
                value = payload.get(field) if isinstance(payload, dict) and field in payload else payload

                # ensure language object exists in portfolio
                if 'languages' not in portfolio:
                    portfolio['languages'] = {}
                if lang not in portfolio['languages'] or not isinstance(portfolio['languages'][lang], dict):
                    portfolio['languages'][lang] = {}

                # Always overwrite when merging from per-lang files
                print(f'Overwriting portfolio.languages.{lang}.{field} (from {src})')
                portfolio['languages'][lang][field] = value
                changed = True

    if dry_run:
        print('Dry-run enabled; no file written.')
        return 0

    if changed:
        write_json_atomic(portfolio_path, portfolio)
        print(f'Updated: {portfolio_path}')
    else:
        print('No changes detected; portfolio left unchanged.')

    return 0


def main():
    parser = argparse.ArgumentParser(description='Merge per-lang JSON sections into portfolio.json')
    parser.add_argument('--input', '-i', default='data/portfolio.json', help='Path to portfolio.json')
    parser.add_argument('--data-dir', '-d', default='data', help='Root data directory with <lang>/<field>.json')
    parser.add_argument('--fields', '-f', default='education', help='Comma-separated fields to merge')
    parser.add_argument('--files', '-F', action='append', help='Bundle files to merge (can be provided multiple times)')
    parser.add_argument('--backup', action='store_true', help='Create a timestamped backup')
    parser.add_argument('--dry-run', action='store_true', help='Show planned changes without writing')
    args = parser.parse_args()

    fields = [s.strip() for s in args.fields.split(',') if s.strip()]

    if not os.path.exists(args.input):
        print(f'Input portfolio not found: {args.input}', file=sys.stderr)
        sys.exit(2)

    rc = merge_sections(args.input, data_dir=args.data_dir, fields=fields, files=args.files, backup=args.backup, dry_run=args.dry_run)
    sys.exit(rc)


if __name__ == '__main__':
    main()
