import json
from collections import defaultdict, Counter

input_file = ''
output_file = ''

# 定义同义词组
synonyms = {
    "happy": ["appreciated", "amused", "cheerful", "connected", "entertained", "friendly", "good", "grateful", "kind",
              "loved", "nice", "optimistic", "secure", "silly", "understood", "warm", "delighted", "hopeful", "safe",
              "joyful", "interested", "generous",
              "valued", "encouraged", "clever", "intelligent", "protective", "beautiful", "lucky", "enlightened",
              "okay", "welcomed", "close", "attractive",
              "rewarded", "accepting", "loving", "so happy", "protected", "welcome", "understanding", "romantic", "glad",
              "liked", "attracted", "hot", "alive",
              "agreeable", "tender", "forgiving", "relieved", "reborn"],
    "excited": ["adventurous", "amazed", "eager", "energized", "exhilarated", "inspired", "intrigued", "motivated",
                "passionate", "playful", "surprised", "curious", "creative", "enthusiastic", "energetic", "shocked",
                "elated", "ecstatic", "more adventurous",
                "ready to try something new", "brilliant", "crazy", "thrilled", "ready", "freed", "liberated"],
    "confident": ["brave", "courageous", "decisive", "determined", "empowered", "powerful", "strong", "respected",
                  "in control", "fearless", "knowledgeable", "organized"],
    "relaxed": ["at ease", "calm", "cool", "peaceful", "rested", "refreshed", "comfortable", "free", "nostalgic",
                "cared for", "comforted", "listened to", "caring", "at home", "at peace", "cared about"],
    "proud": ["accomplished", "successful", "victorious", "triumphant", "honored", "competent", "wise", "patriotic",
              "loyal"],
    "satisfied": ["content", "pleased", "full", "fulfilled", "grateful", "helpful", "responsible", "productive",
                  "useful", "thankful", "trusted", "supported", "supportive", "accepted", "mature", "awake"],
    "angry": ["annoyed", "irritated", "mad", "upset", "disgusted", "resentful", "apathetic", "betrayed", "deceitful",
              "ridiculous", "enraged", "insulted", "jealous", "entitled"],
    "frustrated": ["discouraged", "helpless", "hopeless", "overwhelmed", "confused", "embarrassed", "uncomfortable",
                   "exhausted", "trapped", "envious", "sick", "rejected", "powerless", "puzzled", "bored",
                   "sentimental", "less energetic", "inferior", "unlucky",
                   "uninterested", "bad", "ignored", "defeated", "unwanted"],
    "sad": ["blue", "disappointed", "lonely", "hurt", "miserable", "unhappy", "lost", "devastated", "compassionate",
            "depressed", "sympathetic", "alone", "touched", "moved", "in pain", "abandoned", "pain", "misunderstood",
            "painful", "sore"],
    "guilty": ["ashamed", "regretful", "remorseful", "sorry", "apologetic", "distracted", "punished"],
    "afraid": ["anxious", "nervous", "scared", "terrified", "worried", "concerned", "frightened", "stressed", "tense",
               "restless", "isolated", "apprehensive", "threatened", "exposed", "fearful", "horrified", "skeptical"],
    "neutral": ["challenged", "important", "thoughtful", "impressed", "unsure", "open", "special", "obligated",
                "focused", "included", "artistic", "stubborn", "attentive", "elegant", "self-righteous", "accountable",
                "serious", "cultured", "independent", "in need",
                "stylish", "cold", "tough", "patient", "alert", "rich", "noble", "mean", "sluggish", "uncertain",
                "logical", "poor", "seen", "in charge", "self-conscious",
                "committed", "rebellious", "resigned", "controlled", "paid", "sober", "weak", "taller", "awkward",
                "humble", "uneasy", "clean", "innocent",
                "involved", "damp", "wet", "unique", "grounded", "cramped", "dirty", "healthy", "smart", "hungry",
                "tired"]

}

# 创建逆向映射
reverse_synonyms = {}
for key, values in synonyms.items():
    for value in values:
        reverse_synonyms[value] = key

# 读取jsonl文件并统计tail的值出现次数
tail_counter = Counter()

with open(input_file, 'r', encoding='utf-8') as infile:
    for line in infile:
        data = json.loads(line.strip())
        tail_value = data.get('tail')
        if tail_value:
            if tail_value in reverse_synonyms:
                tail_value = reverse_synonyms[tail_value]
            tail_counter[tail_value] += 1

# 将统计结果按照词频由高到低排列
sorted_tail_counts = tail_counter.most_common()

# 将结果写入输出jsonl文件
with open(output_file, 'w', encoding='utf-8') as outfile:
    for tail, count in sorted_tail_counts:
        result = {'tail': tail, 'count': count}
        json.dump(result, outfile, ensure_ascii=False)
        outfile.write('\n')

print(f"合并并统计后的结果已保存到 {output_file}")
