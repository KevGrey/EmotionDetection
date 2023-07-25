import requests
import pandas as pd
import csv
import sys

# 设置文件路径
file_path = r"data\sentiment.csv"

# 创建一个空字典用于存储映射关系
mapping_dict = {}

# 打开文件并读取数据
with open(file_path, "r") as file:
    reader = csv.reader(file)
    next(reader)  # 跳过文件的第一行标题行
    for row in reader:
        sentiment = row[0]
        emotion = row[1]
        mapping_dict[emotion] = sentiment

# 定义待匹配的单词列表
words_to_check = ["happy", "grateful", "relaxed", "positive-other", "neutral", "anger", "sadness", "fear", "depress", "disgust", "astonished", "worried", "negative-other"]

prompt = '''从“happy, grateful, relaxed, positive-other, neutral, anger, sadness, fear, depress, disgust, astonished, worried, negative-other”中选择一个最能描述给定句子的情感的单词。 你选择，不要试图解释答案。 您一次只能回复一个字。

句子：
怎么了

回答：
astonished

句子：
他给多少

回答：
relaxed

句子：
你还没姓彭

回答：
depress

句子：
好好我错了

回答：
neutral

句子：
让我放心

回答：
worried

句子：
要不是我天生丽质兼的一手好厨艺

回答：
positive-other

句子：
你怎么这么久都不理我

回答：
negative-other

句子：
都是因为张薇薇了

回答：
anger

句子：
还是你最好了

回答：
happy

句子：
谢谢啊，苏总

回答：
grateful

句子：
我没事儿

回答：
sadness

句子：
'''

money = 0

# API接口地址
api_url = "https://api.chatuapi.com/chat/ask"

def main():
    ed = 0
    global money, words_to_check
    base = 115## 训练基数
    while True:## 一直循环这个"请输入问题"的代码
        if ed > 0:
            break
        choose = input("⽀持gpt-3.5, gpt-4.0, gpt-3.5-16k,请选择：").strip()
        text = ''
        print("请按【说话人: 说话内容】的格式输入对话：")
        lines = sys.stdin.readlines()
        text = '\n'.join(lines)
        ## >>>下面开始小追问
        train_dialogues = text
        ask = text + "\n\n请阅读这段对话，从尽可能消极或中性的角度分析其中的情感："
        # 请求参数
        params = {
            "accessToken": "PGBpd7X9e9V3miPX6AcVbvgCEuqEPu8YoFBS7LecVam",
            "prompt": ask,
            "model": choose
        }

        # 发送POST请求
        response = requests.post(api_url, json=params)

        # 解析响应
        if response.status_code == 200:
            data = response.json()
            if data["code"] == 0:
                answer = data["data"]["answer"]
                cost = data["data"]["token"]
                by = data["data"]["model"]
                session = data["data"]["conversationId"]## 相当于握手获得对话ID
                #print(session)
                print("回答: ", answer)
                #print("cost", cost/10000, "by", by)
                money += cost/10000
            else:
                error_message = data["message"]
                print("请求失败: ", error_message)
            ## >>>下面开始小追问
            # 初始化新的列表变量
            target = []
    
            # 按行拆分对话
            lines = train_dialogues.split('\n')
            lines = [line for line in lines if line.strip()]## 去除空的对象
    
            # 提取句子并添加到新的列表中
            for line in lines:
                if ':' in line:
                    sentence = line.split(':')[1].strip()
                    target.append(sentence)
            up = len(lines)## 一段话最多的句子数量
            i = 0
            j = 0
            j2 = 0
            while True:## 这里是内部连续追问小循环，注意不要搞错了
                if i == up:
                    print("cost", money, "by", by)
                    ed += 1
                    break## 这里退出小循环到外面大循环
                # 发送信息
                if target[i] != "":
                    send = prompt + target[i] + "\n\n回答："
                    #send = "“" + target[i] + "”这句话的情感是什么？"
                    # 请求参数
                    params = {
                        "accessToken": "PGBpd7X9e9V3miPX6AcVbvgCEuqEPu8YoFBS7LecVam",
                        "conversationId": session,
                        "prompt": send,
                        "model": choose
                    }
                    # 发送POST请求
                    response = requests.post(api_url, json=params)
                    # 解析响应
                    if response.status_code == 200:
                        data = response.json()
                        if data["code"] == 0:
                            i += 1
                            answer = data["data"]["answer"]
                            cost = data["data"]["token"]
                            by = data["data"]["model"]
                            print(target[i-1], "的情绪可能是", answer)
                            money += cost / 10000
                            
                            flag = 0
                            for word in words_to_check:
                                if word in answer:## 这段已经筛选出了所选择的情绪
                                    flag += 1## 选择的个数
                                    label = word
                                    
                            dont = True## 重新执行就不用输出了
                            if flag != 1:
                                i -= 1## 不在范围就重新回答
                                dont = False
                            
                            if dont:
                                if mapping_dict.get(label) == "negative":
                                    print(mapping_dict.get(label), "负向")
                                if mapping_dict.get(label) == "positive":
                                    print(mapping_dict.get(label), "正向")
                                if mapping_dict.get(label) == "neutral":
                                    print(mapping_dict.get(label), "中性")
                        else:
                            error_message = data["message"]
                            print("请求失败: ", error_message)
                    else:
                        print("请求失败:", response.status_code)## 内部小循环的接入失败 <<<小追问结束
        else:
            print("请求失败:", response.status_code)## 如果第一句话没问出去，仍然会执行下面的小对话
                    
if __name__ == '__main__':
    main()