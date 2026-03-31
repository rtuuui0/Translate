import re

def check_untranslated(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    untranslated_values = set()
    for i, line in enumerate(lines, 1):
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            value = value.strip()
            # Check if value contains English letters and no Chinese
            if re.search(r'[a-zA-Z]', value) and not re.search(r'[\u4e00-\u9fff]', value):
                untranslated_values.add(value)
    
    return sorted(untranslated_values)

if __name__ == "__main__":
    input_file = r"d:\Zoho\vscode\Translate\translated_output.txt"
    untranslated = check_untranslated(input_file)
    if untranslated:
        print("Untranslated values:")
        for val in untranslated:
            print(f"'{val}': '',")
    else:
        print("All lines are translated.")