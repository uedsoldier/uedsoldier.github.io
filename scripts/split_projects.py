#!/usr/bin/env python3
"""
Split projects from `data/portfolio.json` into individual files and produce
`data/projects.json` bundle suitable for merging back into portfolio.json.

Behavior:
- Writes per-project files to `data/projects/<id>-<lang>.json` for every project
  found under `portfolio['languages'][<lang>]['projects']`.
- Creates `data/projects.json` with structure {
    "es": {"projects": [...]},
    "en": {"projects": [...]} }

Usage:
  python3 scripts/split_projects.py --input data/portfolio.json
"""
import argparse
import json
import os
import sys
from typing import Dict, List


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(path, data):
    tmp = path + '.tmp'
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    os.replace(tmp, path)


def split_projects(portfolio_path: str, out_dir: str = 'data/projects', bundle_path: str = 'data/projects.json') -> int:
    if not os.path.exists(portfolio_path):
        print('portfolio.json not found:', portfolio_path, file=sys.stderr)
        return 2

    portfolio = load_json(portfolio_path)
    langs = portfolio.get('languages', {})

    # Ensure output directory
    os.makedirs(out_dir, exist_ok=True)

    # Collect per-language project lists from written per-project files
    bundle: Dict[str, Dict[str, List]] = {}

    for lang, lang_content in langs.items():
        projects = lang_content.get('projects', []) if isinstance(lang_content, dict) else []
        out_list = []
        for proj in projects:
            # Each project should have an `id` (recommended). Fall back to slug if missing.
            pid = proj.get('id') or proj.get('slug')
            if pid is None:
                print(f'Warning: project in {lang} missing id and slug; skipping', file=sys.stderr)
                continue

            fname = os.path.join(out_dir, f"{pid}-{lang}.json")
            write_json(fname, proj)
            out_list.append(proj)
            print('Wrote per-project file:', fname)

        bundle[lang] = {'projects': out_list}

    # Write bundle file
    write_json(bundle_path, bundle)
    print('Wrote bundle:', bundle_path)
    return 0


def main():
    parser = argparse.ArgumentParser(description='Split projects into individual JSON and build projects.json')
    parser.add_argument('--input', '-i', default='data/portfolio.json', help='Path to portfolio.json')
    parser.add_argument('--out-dir', '-d', default='data/projects', help='Directory to write per-project files')
    parser.add_argument('--bundle', '-b', default='data/projects.json', help='Output bundle path')
    args = parser.parse_args()

    rc = split_projects(args.input, out_dir=args.out_dir, bundle_path=args.bundle)
    sys.exit(rc)


if __name__ == '__main__':
    main()
