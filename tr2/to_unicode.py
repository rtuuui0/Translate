import os
import re

# 配置路径
INPUT_FILE = 'new-huawei-keys_DONE.txt'  
OUTPUT_DIR = 'unicode_output'            
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'new-huawei-keys_unicode.txt') 

def text_to_unicode(text):
    # 将文本中的每一个字符（中英文、数字、空格）全部转换为 Unicode 编码。
    # 彻底移除了注释中的敏感转义字符，避免 Python 语法报错。
    res = []
    for char in text:
        # 转换为 16 进制并补齐 4 位
        res.append(f"\\u{ord(char):04x}")
    return "".join(res)

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 找不到输入文件: {INPUT_FILE} - to_unicode.py:20")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 已创建新文件夹: {OUTPUT_DIR} - to_unicode.py:25")

    print(f"📖 正在读取文件: {INPUT_FILE}... - to_unicode.py:27")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print("⚙️ 正在将 Value 中的全部内容转换为 Unicode 格式... - to_unicode.py:31")
    print("(HTML 网页标签将被自动跳过并原样保留) - to_unicode.py:32")
    
    unicode_lines = []
    for line in lines:
        content = line.rstrip('\n\r')
        newline = line[len(content):]
        
        if '=' in content and not content.startswith('#'):
            key, val = content.split('=', 1)
            
            parts = re.split(r'(<[^>]+>)', val)
            unicode_val_parts = []
            
            for p in parts:
                if re.match(r'<[^>]+>', p):
                    unicode_val_parts.append(p)
                else:
                    unicode_val_parts.append(text_to_unicode(p))
            
            unicode_lines.append(f"{key}={''.join(unicode_val_parts)}{newline}")
        else:
            unicode_lines.append(line)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.writelines(unicode_lines)

    print(f"✅ 完美转换完成！ - to_unicode.py:58")
    print(f"🎉 请前往 {OUTPUT_DIR} 文件夹下查看新生成的: newhuaweikeys_unicode.txt - to_unicode.py:59")

if __name__ == "__main__":
    main()