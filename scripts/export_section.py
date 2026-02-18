#!/usr/bin/env python3
"""
Export a section from `data/portfolio.json` into a bundle file under `data/`.

Example: export `projects` will write `data/projects.json` with structure:
{
  "es": { "projects": [...] },
  "en": { "projects": [...] }
}

Usage:
  python3 scripts/export_section.py --input data/portfolio.json --section projects
"""
import argparse
import json
import os
import sys


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(path, data):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    os.replace(tmp, path)


def export_section(portfolio_path, section, out_path=None, dry_run=False):
    if out_path is None:
        out_path = os.path.join('data', f'{section}.json')

    portfolio = load_json(portfolio_path)
    langs = portfolio.get('languages', {})

    bundle = {}
    for lang, content in langs.items():
        if not isinstance(content, dict):
            continue
        if section in content:
            bundle[lang] = {section: content[section]}
        else:
            bundle[lang] = {section: None}

    if dry_run:
        print('[dry-run] would write', out_path)
        return 0

    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    write_json(out_path, bundle)
    print('Written:', out_path)
    return 0


def main():
    parser = argparse.ArgumentParser(description='Export section from portfolio.json into data/<section>.json')
    parser.add_argument('--input', '-i', default='data/portfolio.json', help='Path to portfolio.json')
    parser.add_argument('--section', '-s', required=True, help='Section key to export (e.g. projects)')
    parser.add_argument('--out', '-o', default=None, help='Output bundle path (default: data/<section>.json)')
    parser.add_argument('--dry-run', action='store_true', help='Show actions but do not write')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print('Input portfolio not found:', args.input, file=sys.stderr)
        sys.exit(2)

    rc = export_section(args.input, args.section, out_path=args.out, dry_run=args.dry_run)
    sys.exit(rc)


if __name__ == '__main__':
    main()
