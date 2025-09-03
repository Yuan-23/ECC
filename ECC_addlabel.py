import json
import os
import re

# 修改数据格式
# 1、添加轮次/情感原因等
# 2、删除对话中带（）的内容


# 定义输入和输出文件路径
input_file_path = ''
output_file_path = ''

# 确保输出目录存在
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

# 定义用于删除括号、星号及其内容的正则表达式

# parentheses_pattern = re.compile(r'[（(].*?[）)]')
parentheses_pattern = re.compile(r'[（(].*?[）)]|\*.*?\*')
def remove_parentheses(text):
    # 使用正则表达式的sub方法替换括号及其内容为空字符串
    return parentheses_pattern.sub('', text)



def process_dialogue(data, new_data):
    dialogue_lines = data.get("cumulative_dialogue", "").split('\n')
    speakers = data.get("cumulative_speakers", [""])  # 默认为空列表

    dialogue = []
    turn = 1
    for i, utterance in enumerate(dialogue_lines):
        speaker = speakers[i] if i < len(speakers) else ""

        # 去除utterance开头的"speaker:"，考虑了冒号后可能的空格
        pattern = re.compile(r'^' + re.escape(speaker) + r'\s*[:：]')
        match = pattern.match(utterance)
        if match:
            # 如果匹配成功，移除匹配的说话者名称和冒号，以及之后的任何额外空白字符
            utterance = utterance[match.end():].strip()
        else:
            # 如果不匹配，仅移除字符串两端的空白字符
            utterance = utterance.strip()
        # utterance = utterance[len(speaker) + 2:].strip() if utterance.startswith(f"{speaker}: ") else utterance.strip()

        dialogue.append({
            "turn": turn,
            "speaker": speaker,
            "utterance": utterance,
            "emotion": "",
        })
        turn += 1

    # 删除最后一个"speaker"为"Unknown"的对话轮次
    if dialogue and dialogue[-1]["speaker"] == "":
        dialogue.pop()

    new_data['dialogue'] = dialogue


# 打开输出文件准备写入
with open(output_file_path, 'w', encoding='utf-8') as outfile:
    # 读取原始数据
    with open(input_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:

                data = json.loads(line)

                # 删除cumulative_dialogue中的括号及其内容
                if 'cumulative_speakers' in data:
                    data['cumulative_speakers'] = [
                        remove_parentheses(utterance).strip() for utterance in data['cumulative_speakers']
                    ]

                if 'cumulative_dialogue' in data:
                    data['cumulative_dialogue'] = remove_parentheses(data['cumulative_dialogue']).strip()

                if 'cumulative_utterances' in data:
                    data['cumulative_utterances'] = [
                        remove_parentheses(utterance).strip() for utterance in data['cumulative_utterances']
                    ]

                new_data = {
                    "split_index": f"{data['split']}_{data['index']}",  # 合并index和split为id
                    # "cumulative_dialogue": data.get("cumulative_dialogue", ""),
                    "cumulative_dialogue": f"{data['cumulative_speakers'][0]}:{data['cumulative_dialogue']}",  #原数据最开始没有第一个说话人的名字，加上名字
                    "cumulative_speakers": data.get("cumulative_speakers", ""),
                    "cumulative_utterances": data.get("cumulative_utterances", ""),
                    "head": data.get("head", ""),
                    "tail": data.get("tail", ""),
                    "sentence": data.get("input_text", ""),  # 重命名input_text为sentence
                    "narrative": data.get("narrative", ""),
                }
                process_dialogue(data, new_data)

                outfile.write(json.dumps(new_data) + '\n')
            except json.JSONDecodeError as e:
                print(f"Error parsing line: {line.strip()}")
                print(f"JSONDecodeError: {e}")

print("数据处理完成，已保存到指定文件。")
