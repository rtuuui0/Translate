import argparse
import re
from pathlib import Path

CJK = r"\u4e00-\u9fff"


def clean_text_fragment(fragment: str) -> str:
    # Collapse spaces/tabs to single space first.
    text = re.sub(r"[ \t]+", " ", fragment)

    # Remove spaces between CJK characters and also around CJK-ASCII boundaries.
    text = re.sub(rf"([{CJK}])\s+([{CJK}])", r"\1\2", text)
    text = re.sub(rf"([{CJK}])\s+([A-Za-z0-9])", r"\1\2", text)
    text = re.sub(rf"([A-Za-z0-9])\s+([{CJK}])", r"\1\2", text)

    # Remove spaces around common punctuation.
    text = re.sub(r"\s+([,\.\!\?\u3002\uFF01\uFF1F\uFF0C\uFF1B\uFF1A;:])", r"\1", text)
    text = re.sub(r"([\(\[\{<\uFF08\u300C\u300E])\s+", r"\1", text)
    text = re.sub(r"\s+([\)\]\}>\uFF09\u300D\u300F])", r"\1", text)

    # Normalize spaces again after punctuation cleanup.
    text = re.sub(r"[ \t]+", " ", text)

    # Drop repeated spaces that may happen from special conditions.
    text = re.sub(r" {2,}", " ", text)

    return text.strip()


def clean_value(value: str) -> str:
    # Preserve HTML tags, only clean text segments outside tags.
    parts = re.split(r"(<[^>]+>)", value)
    cleaned_parts = []
    for part in parts:
        if part == "":
            continue
        if re.match(r"^<[^>]+>$", part):
            cleaned_parts.append(part)
        else:
            cleaned_parts.append(clean_text_fragment(part))
    return "".join(cleaned_parts)


def cleanup_file(input_path: Path, output_path: Path, preview: bool = False):
    with input_path.open("r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    cleaned_lines = []
    for lineno, line in enumerate(lines, start=1):
        raw = line.rstrip("\n\r")
        if raw.strip() == "" or raw.strip().startswith("#") or "=" not in raw:
            cleaned_lines.append(raw.strip() + "\n")
            continue

        key, value = raw.split("=", 1)
        key = key.strip()
        cleaned_value = clean_value(value)
        cleaned_line = f"{key}={cleaned_value}\n"

        if preview and cleaned_line != raw + "\n":
            print(f"Line {lineno}:\n  before: {raw}\n  after:  {cleaned_line.rstrip()}\n")

        cleaned_lines.append(cleaned_line)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.writelines(cleaned_lines)

    return cleaned_lines


def main():
    parser = argparse.ArgumentParser(description="逐行清理属性文件中的无用空格（Unicode 兼容），保留 HTML 标签结构。")
    parser.add_argument("input", help="输入文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径，默认同目录加 .cleaned", default=None)
    parser.add_argument("--preview", action="store_true", help="打印每行变化预览")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    output_path = Path(args.output) if args.output else input_path.with_suffix(input_path.suffix + ".cleaned")
    cleaned_lines = cleanup_file(input_path, output_path, preview=args.preview)
    print(f"已完成: {input_path} -> {output_path} (共 {len(cleaned_lines)} 行)")


if __name__ == "__main__":
    main()
