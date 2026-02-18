#!/usr/bin/env python3
"""
Clear contents of bundle JSON files such as data/projects.json, data/skills.json,
data/education.json, data/contact.json, etc.

The script supports two modes:
- --fields a comma-separated list of logical sections to clear (projects, skills, education, contact, ...)
- --files one or more explicit bundle paths to clear (data/projects.json)

By default the script will build per-language placeholders using the languages
defined in `data/portfolio.json`. Use `--backup` to create backups and `--dry-run`
to preview actions without writing files.

Example:
  python3 scripts/clear_bundles.py --fields projects,skills,education,contact --backup

This will write `data/projects.json`, `data/skills.json`, etc., with empty structures.
"""
import argparse
import json
import os
import shutil
import sys


DEFAULT_EMPTY_FOR_FIELD = {
    'projects': [],
    'skills': [],
    'education': [],
    'tags': [],
    'categories': [],
    'contact': {},
}


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json_atomic(path, data):
    tmp = path + '.tmp'
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    os.replace(tmp, path)


def make_empty_bundle(langs, field_name):
    empty_value = DEFAULT_EMPTY_FOR_FIELD.get(field_name, [])
    bundle = {}
    for lang in langs:
        bundle[lang] = {field_name: empty_value}
    return bundle


def clear_files(files, portfolio_path='data/portfolio.json', backup=False, dry_run=False):
    if not os.path.exists(portfolio_path):
        print(f'Warning: {portfolio_path} not found; languages will be inferred as ["es","en"]')
        langs = ['es', 'en']
    else:
        portfolio = load_json(portfolio_path)
        langs = list(portfolio.get('languages', {}).keys()) or ['es', 'en']

    actions = []
    for f in files:
        field = os.path.splitext(os.path.basename(f))[0]
        bundle = make_empty_bundle(langs, field)
        actions.append((f, bundle))

    for path, bundle in actions:
        if dry_run:
            print(f'[dry-run] would write {path} (languages: {list(bundle.keys())})')
            continue

        if backup and os.path.exists(path):
            bak = path + '.bak'
            shutil.copyfile(path, bak)
            print(f'Backup created: {bak}')

        write_json_atomic(path, bundle)
        print(f'Wrote empty bundle: {path}')

    return 0


def main():
    parser = argparse.ArgumentParser(description='Clear bundle JSON files under data/')
    parser.add_argument('--fields', '-f', help='Comma-separated field names to clear (e.g. projects,skills)')
    parser.add_argument('--files', '-F', action='append', help='Explicit bundle file paths to clear (can repeat)')
    parser.add_argument('--portfolio', '-p', default='data/portfolio.json', help='Path to portfolio.json for language list')
    parser.add_argument('--backup', action='store_true', help='Create .bak copies of existing files before overwriting')
    parser.add_argument('--dry-run', action='store_true', help='Show planned actions without writing files')
    args = parser.parse_args()

    files = []
    if args.fields:
        for field in [s.strip() for s in args.fields.split(',') if s.strip()]:
            files.append(os.path.join('data', f'{field}.json'))
    if args.files:
        for f in args.files:
            files.append(f)

    if not files:
        print('No files specified. Use --fields or --files.', file=sys.stderr)
        parser.print_help()
        sys.exit(2)

    rc = clear_files(files, portfolio_path=args.portfolio, backup=args.backup, dry_run=args.dry_run)
    sys.exit(rc)


if __name__ == '__main__':
    main()
