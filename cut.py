import fasttext
import re
import string
import unicodedata
import docx
import tkinter as tk
from tkinter import filedialog

MODEL = fasttext.load_model('lid.176.ftz')

def count_tokens(text):
    english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
    chinese_chars = len([char for char in text if 'CJK UNIFIED IDEOGRAPH' in unicodedata.name(char, '')])
    punctuation_marks = len([char for char in text if char in string.punctuation or char in [',', '“', '”', '‘', '’']])
    whitespace_chars = len(re.findall(r'\s', text))
    total_tokens = english_words + chinese_chars * 2 + punctuation_marks + whitespace_chars
    return total_tokens


def detect_language(text):
    lines = text.split('\n')
    predictions = [MODEL.predict(line, k=1) for line in lines]
    # 選擇出現最多次的語言作為整個文本的語言
    lang_counts = {}
    for prediction in predictions:
        lang = prediction[0][0].split('__label__')[-1]
        if lang in lang_counts:
            lang_counts[lang] += 1
        else:
            lang_counts[lang] = 1
    lang = max(lang_counts, key=lang_counts.get)
    return lang

def split_text(text, max_tokens=None):
    language = detect_language(text)
    if language == 'zh-cn' or language == 'zh-tw':
        max_tokens =  3050
        sentences = re.split(r'(?<=[。！？])\s*', text)
    elif language == 'en':
        max_tokens =  4000
        sentences = re.split(r'(?<=[.])\s+', text)
    else:
        max_tokens = 3050  # 預設情況下，將使用中文的 token 限制
        sentences = re.split(r'(?<=[。！？])\s*', text)

    result = []
    current_chunk = ""

    for sentence in sentences:
        if count_tokens(current_chunk + sentence) <= max_tokens:
            current_chunk += sentence
        else:
            if current_chunk:
                result.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        result.append(current_chunk.strip())

    return result

# 其他部分保持不變



def open_file():
    file_path = filedialog.askopenfilename()
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    else:
        text = ""
        print("Invalid file type")

    max_tokens = 3050
    split_result = split_text(text, max_tokens)

    for idx, part in enumerate(split_result):
        part_tokens = count_tokens(part)
        text_box.insert(tk.END, f"Part {idx + 1} :\n\n{part}\n\n")
        text_box.tag_configure(f"tag{idx + 1}", foreground="blue", underline=True)
        part_selection_menu['menu'].add_command(label=f"Part {idx + 1}", command=lambda idx=idx: jump_to_part(idx))

    print(f"Split the text into {len(split_result)} parts")  # 添加這一行
def jump_to_part(part_index):
    line_number = text_box.search(f"Part {part_index + 1} :", "1.0", tk.END)
    text_box.tag_remove("sel", "1.0", tk.END)
    text_box.tag_add("sel", line_number, f"{line_number}+1line")
    text_box.see(line_number)

root = tk.Tk()
root.title("Text Splitter")

open_button = tk.Button(root, text="Open File", command=open_file)
open_button.pack()

text_box = tk.Text(root)
text_box.pack()

part_selection_menu = tk.OptionMenu(root, tk.StringVar(), "")
part_selection_menu.pack()



root.mainloop()
