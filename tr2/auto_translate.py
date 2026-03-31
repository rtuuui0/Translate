import re
import time
import sys
import os
from deep_translator import GoogleTranslator

# 配置
INPUT_FILE = 'new-huawei-keys.txt' 
OUTPUT_FILE = 'new-huawei-keys_DONE.txt'

def translate_text(text):
    # 如果只有空格或换行，直接返回
    if not text.strip() or len(text.strip()) < 1: 
        return text
    try:
        # 翻译时去掉前后的空白，避免插件乱加空格
        res = GoogleTranslator(source='en', target='zh-CN').translate(text.strip())
        return res if res else text
    except:
        return text

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"找不到源文件: {INPUT_FILE} - auto_translate.py:24")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total = len(lines)
    print(f"已读取 {total} 行，正在全力翻译中（已开启换行符保护）... - auto_translate.py:31")

    # 先清空旧的输出文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("")

    with open(OUTPUT_FILE, 'a', encoding='utf-8') as out_f:
        for i, line in enumerate(lines):
            display_name = "跳过(注释/空行)"
            
            # 1. 提取换行符：保留原始的 \n 或 \r\n
            content = line.rstrip('\n\r')
            newline = line[len(content):]
            
            if '=' in content and not content.startswith('#'):
                key, val = content.split('=', 1)
                display_name = key
                
                # 处理 HTML 标签
                parts = re.split(r'(<[^>]+>)', val)
                translated_parts = []
                for p in parts:
                    if re.match(r'<[^>]+>', p):
                        translated_parts.append(p)
                    else:
                        # 翻译文本并拼回它原本可能带有的前后空格
                        translated_parts.append(translate_text(p))
                
                # 2. 拼接：Key + '=' + 翻译后的Value + 原始换行符
                out_f.write(f"{key}={''.join(translated_parts)}{newline}")
            else:
                # 注释行或纯空行，直接原样写入（自带换行）
                out_f.write(line)
            
            # 进度显示
            if i % 2 == 0:
                sys.stdout.write(f"\r进度: {i+1}/{total} | 正在处理: {display_name[:30]}...")
                sys.stdout.flush()
            
            time.sleep(0.1)

    print(f"\n\n任务完美完成！请查看: {OUTPUT_FILE} - auto_translate.py:72")

if __name__ == "__main__":
    main()