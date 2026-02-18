#!/usr/bin/env python3
"""
Assemble individual project JSON files into a single bundle `data/projects.json`.

It expects per-project files named like `<id>-<lang>.json` (e.g. `1-es.json`, `2-en.json`),
but will also attempt to infer language from a `lang` key inside the file if present.

Usage:
  python3 scripts/assemble_projects_bundle.py --projects-dir data/projects --out data/projects.json
"""
import argparse
import json
import os
import sys
from glob import glob


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


def infer_lang_from_filename(name):
    base = os.path.splitext(os.path.basename(name))[0]
    if '-' in base:
        parts = base.rsplit('-', 1)
        if len(parts) == 2 and parts[1].isalpha():
            return parts[1]
    return None


def assemble(projects_dir: str, out_path: str, dry_run: bool = False) -> int:
    pattern = os.path.join(projects_dir, '*.json')
    files = sorted(glob(pattern))
    if not files:
        print('No project files found in', projects_dir, file=sys.stderr)
        return 1

    bundle = {}
    count = 0
    for f in files:
        try:
            proj = load_json(f)
        except Exception as e:
            print(f'Failed to load {f}: {e}', file=sys.stderr)
            continue

        # Determine language: filename suffix preferred, else inside file
        lang = infer_lang_from_filename(f)
        if not lang:
            if isinstance(proj, dict) and 'lang' in proj and isinstance(proj['lang'], str):
                lang = proj['lang']
        if not lang:
            print(f'Warning: could not determine language for {f}; skipping', file=sys.stderr)
            continue

        if lang not in bundle:
            bundle[lang] = {'projects': []}

        bundle[lang]['projects'].append(proj)
        count += 1

    if dry_run:
        print(f'[dry-run] would write {out_path} with {count} projects across {len(bundle)} languages')
        return 0

    write_json(out_path, bundle)
    print(f'Wrote {out_path} ({count} projects, {len(bundle)} languages)')
    return 0


def main():
    parser = argparse.ArgumentParser(description='Assemble per-project JSON files into data/projects.json')
    parser.add_argument('--projects-dir', '-p', default='data/projects', help='Directory with per-project JSON files')
    parser.add_argument('--out', '-o', default='data/projects.json', help='Output bundle path')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without writing')
    args = parser.parse_args()

    rc = assemble(args.projects_dir, args.out, dry_run=args.dry_run)
    sys.exit(rc)


if __name__ == '__main__':
    main()
