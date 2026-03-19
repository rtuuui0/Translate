#!/usr/bin/env python3
"""Translate values in a key=value properties file.

This script preserves:
- comment lines (starting with #)
- empty lines
- keys and separators (the first '=' in the line)

It translates only the value portion (everything after the first '='), leaving the key unchanged.

Usage:
  python translate_properties.py \ 
    --input txt \ 
    --output txt.zh \ 
    --start 1 --end 500 \ 
    --src en --dest zh-cn

By default it prints output to stdout.
"""

import argparse
import io
import shutil
import sys

from deep_translator import GoogleTranslator


def translate_line(line: str, translator: GoogleTranslator, src: str, dest: str) -> str:
    # Keep comment & empty lines as-is
    if not line.strip() or line.lstrip().startswith("#"):
        return line

    if "=" not in line:
        return line

    key, val = line.split("=", 1)
    # If value is all whitespace, nothing to translate
    if not val.strip():
        return line

    try:
        # deep_translator returns a plain string
        translated = translator.translate(val)
        # Ensure the translated value stays on a single line
        translated = " ".join(translated.replace("\r", " ").split())
    except Exception as e:
        # Fallback: keep original if translation fails
        sys.stderr.write(f"WARNING: translation failed for line: {line!r}\n  error: {e}\n")
        translated = val

    return f"{key}={translated}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Translate values in a key=value file")
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", help="Output file path (default stdout)")
    parser.add_argument("--inplace", action="store_true", help="Overwrite the input file (backup created at <input>.bak)")
    parser.add_argument("--start", type=int, default=1, help="Start line number (1-indexed)")
    parser.add_argument("--end", type=int, default=None, help="End line number (inclusive)")
    parser.add_argument("--src", default="en", help="Source language (default: en)")
    parser.add_argument("--dest", default="zh-cn", help="Destination language (default: zh-cn)")

    args = parser.parse_args()

    # Use a moderate timeout to avoid long hangs on network issues
    # Use an HTTP-based translator (Google Translate web) that typically works without an API key
    translator = GoogleTranslator(source=args.src, target=args.dest)

    with io.open(args.input, "r", encoding="utf-8") as f:
        lines = f.readlines()

    start = max(1, args.start)
    end = args.end or len(lines)

    out_lines = []
    for idx, line in enumerate(lines, start=1):
        if start <= idx <= end:
            out_lines.append(translate_line(line.rstrip("\n"), translator, args.src, args.dest) + "\n")
        else:
            out_lines.append(line)

    output_path = None
    if args.inplace or (args.output and args.output == args.input):
        # Overwrite the input file (keep a backup)
        output_path = args.input
        backup_path = f"{args.input}.bak"
        shutil.copy2(args.input, backup_path)
        sys.stderr.write(f"Backed up original to {backup_path}\n")
    elif args.output:
        output_path = args.output

    if output_path:
        with io.open(output_path, "w", encoding="utf-8") as f:
            f.writelines(out_lines)
    else:
        sys.stdout.writelines(out_lines)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
