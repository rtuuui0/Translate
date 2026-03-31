from pathlib import Path

p = Path('new-huawei-keys-CN.cleaned.txt')
lines = p.read_text(encoding='utf-8').splitlines()
bad = [(i+1, l) for i, l in enumerate(lines) if '  ' in l]
print('lines with two spaces:', len(bad))
for i, l in bad[:20]:
    print(i, repr(l))
