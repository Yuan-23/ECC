import openai
import jsonlines
import os
import time

# 调用GPT4评价情感原因对的标注是否合理


openai.api_key = ""
input_file = ''
output_file = ''
progress_file = ''

output_dir = os.path.dirname(output_file)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"输出目录 {output_dir} 不存在，已创建。")

if not os.path.exists(progress_file):
    with open(progress_file, 'w') as f:
        f.write("0")  # 从头开始

with open(progress_file, 'r') as f:
    last_processed_index = int(f.read().strip())  # 读取上次处理的数据条目数


# 合理性评分
def evaluate_ec_pair(cumulative_dialogue, sentence, ec_pair_clause):
    prompt = f"""
    The following is a dialogue, an emotion-cause pair (EC_pair_clause) and a sentence. The given sentence sets the emotions and reasons for the dialogue. Your task is to evaluate how reasonable the EC_pair_clause is based on five criteria:
    1. Does the emotion-cause in EC_pair_clause align with the emotion and the corresponding reason mentioned in the dialogue?
    2. Is the EC_pair_clause the most relevant representation of the emotion and cause for the dialogue as described in the sentence?
    3. If the emotion or reason in the dialogue are unreasonable, provide the most reasonable emotional or reason sentence. 
    4. If a more reasonable one cannot be selected from the original dialogue, rate the overall reasonableness of the EC_pair_clause on 5 points.
    5. Rate the overall reasonableness of the EC_pair_clause on a scale of 0-5 (0: completely unreasonable, 5: fully reasonable).

    Dialogue: {cumulative_dialogue}
    Sentence (emotion and cause): {sentence}
    EC_pair_clause: {ec_pair_clause}

    Please provide your output in the following format:
    Score: X
    The better Emotion：[emotional sentence from the dialogue]
    The better Reason：[reason sentence from the dialogue]
    Evaluation: [Your evaluation here]
    """

    max_retries = 20  # 设置重试次数
    retry_delay = 20  # 每次重试间隔20秒
    for i in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o1",
                messages=[
                    {"role": "system", "content": "You are an expert in dialogue and emotion-cause pair evaluation."},
                    {"role": "user", "content": prompt}
                ],
                # max_tokens=200,
                # temperature=0.7
            )



            output_text = response['choices'][0]['message']['content'].strip()
            # print(output_text)

            score = 0  # 默认分数为0
            betterEMO = ""
            betterREA = ""
            evaluation = ""
            try:
                score_line = [line for line in output_text.split("\n") if "Score:" in line]
                betterEMO_line = [line for line in output_text.split("\n") if "The better Emotion:" in line]
                betterREA_line = [line for line in output_text.split("\n") if "The better Reason:" in line]
                evaluation_line = [line for line in output_text.split("\n") if "Evaluation:" in line]

                # if score_line:
                #     score = int(score_line[0].split("Score:")[1].strip())
                if score_line: # Score四舍五入为整数
                    try:
                        score = round(float(score_line[0].split("Score:")[1].strip()))
                    except ValueError:
                        print("Score is not a valid number, defaulting to 0.")
                        score = 0
                if betterEMO_line:
                    betterEMO = betterEMO_line[0].split("The better Emotion:")[1].strip()
                if betterREA_line:
                    betterREA = betterREA_line[0].split("The better Reason:")[1].strip()
                if evaluation_line:
                    evaluation = evaluation_line[0].split("Evaluation:")[1].strip()
            except (IndexError,ValueError,ValueError, ValueError) as e:
                print(f"Error parsing score or evaluation: {e}")
                score = 0
                betterEMO="Error in parsing GPT response."
                betterREA="Error in parsing GPT response."
                evaluation = "Error in parsing GPT response."
            return score, betterEMO, betterREA, evaluation
        except openai.error.APIConnectionError as e:
            print(f"API connection error: {e}. Retrying {i + 1}/{max_retries}...")
            time.sleep(retry_delay)  # 等待20秒后重试
        except Exception as e:
            print(f"Error: {e}")
            break  # 如果是其他错误，跳出重试循环
    raise Exception("Failed to communicate with OpenAI API after several attempts")


with jsonlines.open(input_file) as reader, jsonlines.open(output_file, mode='a') as writer:
    for idx, obj in enumerate(reader):
        if idx < last_processed_index:  # 如果当前索引小于已处理的进度，跳过处理
            continue
        cumulative_dialogue = obj['cumulative_dialogue']
        sentence = obj['sentence']
        ec_pair_clause = obj['EC_pair_clause']

        score, betterEMO, betterREA, evaluation_text = evaluate_ec_pair(cumulative_dialogue, sentence, ec_pair_clause)

        obj['pair_score'] = score
        obj['betterEMO'] = betterEMO
        obj['betterREA'] = betterREA
        obj['evaluation_text'] = evaluation_text
        if betterEMO.strip() in ec_pair_clause and betterREA.strip() in ec_pair_clause:
            obj['pair_score']=5
            obj['betterEMO'] = None
            obj['betterREA'] = None

        print("\nsentence:",idx,sentence)
        print(ec_pair_clause)
        print("score:", score)
        print("betterEMO:", betterEMO)
        print("betterREA:", betterREA)
        print("evaluation_text:", evaluation_text)

        writer.write(obj)
        # 更新进度文件
        with open(progress_file, 'w') as f:
            f.write(str(idx + 1))

print(f"评估完成，结果已保存到 {output_file}，进度已更新到 {progress_file}。")
