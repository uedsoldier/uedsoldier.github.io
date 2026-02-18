#!/usr/bin/env python3
"""
Split language sections from a bundle JSON into per-language files.

Example: given `data/education.json` with structure {
  "es": { "education": [...] },
  "en": { "education": [...] }
}

This script will write `data/es/education.json` and `data/en/education.json` containing
the corresponding section (keeps key name, e.g. {"education": [...]}).

Usage:
  python3 scripts/split_data.py --input data/education.json

It is intentionally generic so you can use it later for other bundle files.
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


def split_bundle(input_path, out_root='data', dry_run=False):
    data = load_json(input_path)
    if not isinstance(data, dict):
        print(f'Expected top-level object in {input_path}', file=sys.stderr)
        return 1

    written = []
    for lang, content in data.items():
        if not isinstance(content, dict):
            print(f'Skipping language "{lang}": expected object, got {type(content).__name__}')
            continue
        lang_dir = os.path.join(out_root, lang)
        if dry_run:
            print(f'[dry-run] would ensure directory: {lang_dir}')
        else:
            os.makedirs(lang_dir, exist_ok=True)

        for section_key, section_value in content.items():
            out_path = os.path.join(lang_dir, f"{section_key}.json")
            payload = {section_key: section_value}
            if dry_run:
                print(f'[dry-run] would write: {out_path}')
            else:
                write_json(out_path, payload)
                written.append(out_path)

    print(f'Done. Files written: {len(written)}')
    for p in written:
        print(' -', p)
    return 0


def main():
    parser = argparse.ArgumentParser(description='Split bundled language JSON into per-language files')
    parser.add_argument('--input', '-i', default='data/education.json', help='Input bundle JSON path')
    parser.add_argument('--out-root', '-o', default='data', help='Output root directory (default: data)')
    parser.add_argument('--dry-run', action='store_true', help='Show actions without writing files')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f'Input file not found: {args.input}', file=sys.stderr)
        sys.exit(2)

    code = split_bundle(args.input, out_root=args.out_root, dry_run=args.dry_run)
    sys.exit(code)


if __name__ == '__main__':
    main()
