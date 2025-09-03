import openai
import json
import os

#调用GPT，根据三元组转换的一句话，标记情感和原因

# 设置API密钥
openai.api_key = ""
input_file = ""
output_file = ""
last_point_file = ""  #txt格式记录数字

# 定义处理函数
def process_dialogue(dialogue_data):
    cumulative_dialogue = dialogue_data["cumulative_dialogue"]
    sentence = dialogue_data["sentence"]
    dialogue=dialogue_data["dialogue"]

    # 提取原因和情感
    parts = sentence.split(".")
    if len(parts) < 2:
        return None  # 如果sentence格式不对，跳过该条数据
    cause = parts[0].strip()
    emotion = parts[1].strip()

    prompt = f"""
    Conversation content:{cumulative_dialogue}\n
    Emotional description:{sentence}\n
    Emotion:Please find the Conversation content that best fits the emotions or meaning conveyed by {emotion} in the original conversation, preferably in one sentence.\n
    Cause:Please find the Conversation content that best fits the situation or meaning expressed by {cause} in the original conversation, preferably in one sentence.\n
    
    Please directly return the Emotion and Cause found in Conversation content, and do not add any irrelevant text.
    
    Please provide your output in the following format:
    Emotion: emotion clause from the Conversation
    Cause: cause clause from the Conversation
    """

    try:
        # 使用GPT-4来提取情感子句和原因子句
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an assistant who can help identify emotional and causal clauses. You can read a complete conversation and understand its meaning."},
                {"role": "user", "content": prompt}
            ]
        )

        # 提取情感子句和原因子句原文
        result_text = response["choices"][0]["message"]["content"]
        # print("result: ", result_text)

        # 构建结果
        # dialogue_data["EC_summary"] = result_text
        dialogue_data["EC_pair_clause"] = result_text
        # dialogue_data["EC_pairclause"] = f"({emotion_clause}, {cause_clause})"
        print("\n")
        print("split_index: ", dialogue_data["split_index"])
        print("sentence: ", dialogue_data["sentence"])
        # print("EC_summary: ", dialogue_data["EC_summary"])
        print("EC_pair_clause: ", dialogue_data["EC_pair_clause"])
        return dialogue_data

    except (RuntimeError, openai.error.RateLimitError, openai.error.ServiceUnavailableError,
            openai.error.APIError, openai.error.APIConnectionError) as e:
        return None




# 读取上次处理到的行号
if os.path.exists(last_point_file):
    with open(last_point_file, 'r', encoding='utf-8') as lp_file:
        start_line = int(lp_file.read().strip())
else:
    start_line = 0  # 如果没有lastpoint.txt文件，则从头开始
    # 创建输出目录
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(last_point_file, 'w', encoding='utf-8') as lp_file:
        lp_file.write('0')

with (open(input_file, 'r', encoding='utf-8') as infile,
      open(output_file, 'a', encoding='utf-8') as outfile):
    # 跳过已处理的行
    for _ in range(start_line):
        next(infile)

    current_line = start_line

    for line in infile:
        dialogue_data = json.loads(line.strip())
        processed_data = process_dialogue(dialogue_data)

        # 仅当数据处理成功并且不为空时，才增加行号并写入文件
        if processed_data is not None:
            outfile.write(json.dumps(processed_data, ensure_ascii=False) + "\n")
            print("one data saved.\n")

            # 更新当前行号
            current_line += 1
            # 将当前行号写入lastpoint.txt文件
            with open(last_point_file, 'w', encoding='utf-8') as lp_file:
                lp_file.write(str(current_line))

    print("处理完成。")