import openai
import json
import os


#调用GPT标记情感和原因


# 设置API密钥
openai.api_key = ""
input_file = ""
output_file = ""
last_point_file = ""  #txt格式记录数字


def analyze_emotion(utterances):
    prompt = (
        "Please analyze the emotions of each sentence in the conversation and generate emotion and reason labels according to the following requirements:"
        "1. Emotional words are limited to: (HAPPY, EXCITED, CONFIDENT,RELAXED,PROUD,SATISFIED,ANGRY,FRUSTRATED,SAD,GUILTY,AFRAID,NEUTRAL), Choose one of the most appropriate words to describe the emotions of the current sentence;"
        "2. If it is difficult to determine the emotion of the current sentence or if there is no emotion, it defaults to NEUTRAL,and the reason clause is empty;"
        "3. If the emotion in the current sentence is not NEUTRAL, please identify the clause that triggers the emotion in the previous historical dialogue;"
        "4. The reason clause should be the original dialogue text at the clause level."
        "5. The reason clause should be found in this round of dialogue and all historical dialogues prior to this round of dialogue."
        "6. Before 'speaker:',mark the emotional word with '()' and the reason clause that triggers the emotion with '[]'. "
        "7. If a sentence is difficult to determine emotions and reasons, it can be marked '(NEUTRAL)'."
        # "The reason should be the original dialogue. The format is as follows: \ n"
        # f"(emotion) 【cause】 utterance\n\n"#
        f"{utterances}\n\n"
        "Please return the result in the specified format."
    )

    try:
        # print("输出",api[api_count])
        response = openai.ChatCompletion.create(
            # model="gpt-3.5-turbo",
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        # 获取API的返回内容
        response_content = response['choices'][0]['message']['content']
        print("API Response Content:", response_content)  # 调试输出

        return response_content

    except (RuntimeError, openai.error.RateLimitError, openai.error.ServiceUnavailableError,
            openai.error.APIError, openai.error.APIConnectionError) as e:
        return None



# 读取上次处理到的行号
if os.path.exists(last_point_file):
    with open(last_point_file, 'r', encoding='utf-8') as lp_file:
        start_line = int(lp_file.read().strip())
else:
    start_line = 0  # 如果没有lastpoint.txt文件，则从头开始
    with open(last_point_file, 'w', encoding='utf-8') as lp_file:
        lp_file.write('0')
 

# 将 cumulative_utterances 拼接成一个字符串，并通过 GPT-3.5 进行情感分析。
# 将分析结果按行拆分，并与原始对话逐一对应，将格式化后的结果保存到 cumulative_utterances 字段中。           
with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'a', encoding='utf-8') as outfile:
    # 上一次到start_line了
    for _ in range(start_line):
        next(infile)

    current_line = start_line

    for line in infile:
        #记录运行到哪一行了
        current_line += 1
        data = json.loads(line)
        utterances = "\n".join(data.get('cumulative_utterances', []))

        if utterances:
            analysis_result = analyze_emotion(utterances)
            
            if analysis_result:
                try:
                    # 分割分析结果为每个句子的情感标注
                    analyzed_lines = analysis_result.strip().split('\n')
                    formatted_utterances = []

                    for original, analyzed in zip(data['cumulative_utterances'], analyzed_lines):
                        formatted_utterances.append(f"{analyzed.strip()} {original.strip()}")

                    data['cumulative_utterances'] = formatted_utterances
                    outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
                except Exception as e:
                    print(f"Unexpected error: {e}")
            else:
                print("Analysis result is None, skipping this line.")
        else:
            print("No cumulative_dialogue found in this line, skipping.")

        # 将当前行号写入lastpoint.txt文件
        with open(last_point_file, 'w', encoding='utf-8') as lp_file:
            lp_file.write(str(current_line))
