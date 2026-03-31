import re
import argparse
import sys

def get_translator():
    try:
        from deep_translator import GoogleTranslator
        return lambda t: GoogleTranslator(source='auto', target='zh-CN').translate(t)
    except Exception:
        try:
            from googletrans import Translator
            tr = Translator()
            return lambda t: tr.translate(t, dest='zh-cn').text
        except Exception:
            return None


def should_skip_token(tok: str) -> bool:
    # skip tokens that look like HTML tags or are short/all-caps abbreviations
    if not tok or tok.strip() == '':
        return True
    if re.fullmatch(r"[A-Z0-9_\-]{1,6}", tok.strip()):
        return True
    return False


def translate_value(value: str, translator) -> str:
    # split by tags like <...> and keep tags unchanged
    parts = re.split(r'(<[^>]*>)', value)
    out_parts = []
    for p in parts:
        if p.startswith('<') and p.endswith('>'):
            out_parts.append(p)
            continue
        # translate non-tag segment, but preserve surrounding spaces
        leading = re.match(r'^\s*', p).group(0)
        trailing = re.match(r'.*?(\s*)$', p).group(1)
        core = p.strip()
        if core == '':
            out_parts.append(p)
            continue
        if should_skip_token(core):
            out_parts.append(p)
            continue
        if translator is None:
            # no translator available; leave as-is
            out_parts.append(p)
            continue
        try:
            translated = translator(core)
            if translated is None:
                translated = core
            else:
                translated = str(translated)
        except Exception:
            translated = core
        out_parts.append(leading + translated + trailing)
    return ''.join(out_parts)


def looks_english(s: str) -> bool:
    return bool(re.search(r'[A-Za-z]{4,}', s))


def process_file(input_path: str, output_path: str):
    translator = get_translator()
    suspect_lines = []
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    out_lines = []
    for i, line in enumerate(lines, 1):
        if '=' in line:
            key, val = line.split('=', 1)
            new_val = translate_value(val.rstrip('\n'), translator)
            # simple check: if result still contains long English words, retry once
            if looks_english(new_val) and translator is not None:
                try:
                    retry = translate_value(val.rstrip('\n'), translator)
                    if not looks_english(retry):
                        new_val = retry
                    else:
                        suspect_lines.append((i, key.strip(), val.strip(), new_val))
                except Exception:
                    suspect_lines.append((i, key.strip(), val.strip(), new_val))
            out_lines.append(f"{key}={new_val}\n")
        else:
            out_lines.append(line)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(out_lines)

    print(f"Wrote {len(out_lines)} lines to {output_path}")
    if suspect_lines:
        print("Suspect translations found (line, key):")
        for ln, k, orig, trans in suspect_lines:
            print(f"{ln}: {k} -> {trans}")
    else:
        print("No suspect lines detected.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input', default='to_translate.properties')
    ap.add_argument('-o', '--output', default='to_translate.zh.properties')
    args = ap.parse_args()
    process_file(args.input, args.output)


if __name__ == '__main__':
    main()
