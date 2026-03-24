import sys

def unicode_escape(s):
    result = []
    for c in s:
        if ord(c) > 127:  # non-ASCII, assume Chinese
            result.append(f'\\u{ord(c):04x}')
        else:
            result.append(c)
    return ''.join(result)

print("Starting conversion")

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Read {len(lines)} lines")

new_lines = []
for i, line in enumerate(lines):
    if '=' in line:
        key, value = line.split('=', 1)
        value = value.strip()
        escaped = unicode_escape(value)
        new_line = f"{key}={escaped}\n"
        print(f"Line {i+1}: converted")
    else:
        new_line = line
    new_lines.append(new_line)

print(f"Writing {len(new_lines)} lines to {sys.argv[1]}.new")

with open(sys.argv[1] + '.new', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Conversion done")