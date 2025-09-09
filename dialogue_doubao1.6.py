import pandas as pd
import csv
import time
from tqdm import tqdm
from openai import OpenAI
import os
from pathlib import Path



client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key='',
)
prompt = """
假设你是一位有着数十年行医经验的中医医生，精通中医的各个领域知识。请你对我接下来给出的病人基本状况描述给出相应的中西医诊断和药方，请注意你回答的专业性、客观性和安全性。以下是一个患者的例子：
“一般情况：    性别：女    年龄：16岁
初诊日期：2023年9月12日
主诉：睡眠欠佳半年。
现病史：患儿近半年出现睡眠差，难入睡，睡着后容易惊醒，时常做噩梦，心烦，不愿外出，会独自哭 泣，有厌学情绪，精总诊断抑郁症，现百忧解口服中，白天头晕头痛，昏沉欲睡，时觉乏力，脱发严重，怕冷 欲穿衣，手脚冰凉，无胸闷心慌，胃纳欠佳，纳呆不欲饮食，大便尚可，月经至，但经期较长，9-10天1次，周 期正常，偶有痛经，时伴腰膝酸软。为进一步诊疗于生长发育和心理门诊就诊。
刻诊：神情疲惫，不善言语，胃纳欠佳，二便尚调。
专科检查：36.9℃,神志清，精神可，形体正常，面色萎黄，五官端正，眼睑无充血，鼻腔内干净，咽不红， 两侧扁桃腺无肿大，语声低微，气息均匀，胸廓对称，呼吸运动正常，肋间隙无明显增宽，触觉语颤对称，无 胸膜摩擦感，两肺叩诊呈正常清音，听诊两肺呼吸音稍粗，两肺未闻及明显干湿罗音，语音传导对称存在， 未及胸膜摩擦音。心率：80次/分，律齐，第一心音有力，各瓣膜听诊区未及病理性杂音，腹平软，全腹无压 痛及反跳痛，肠鸣音正常，肝肾无叩击痛，双下肢无水肿，四肢肌力、肌张力均正常，翻手试验、指鼻试验、 点指试验均为阴性。”

你需要根据以上的病例描述，请逐项给出类似下面格式的诊断信息。如：中医诊断、西医诊断、辨证证型、治则、处方名（如有方名请写方名，可以加减；无方名可自拟）、成分与克数（按照主次顺序写成一行，中间用空格分隔）、付数、用法、医嘱（限制100字）等。
“中医诊断：不寐病
辨证证型：脾肾阳虚
西医诊断：睡眠障碍
治则：温肾潜阳，补益心脾，安神定志
处方名：自拟温潜安神方。
成分与克数：附子3g 黄连3g 首乌藤10g 桂枝6g 党参9g 茯苓9g 酸枣仁9g 郁金9g 淮小麦15g 紫贝齿15g 龙齿15g 珍珠母9g 磁石15g 远志6g 炙甘草3g 柴胡5g                                                                   付数：28剂
用法：以草药代煎每日早晚各一包餐后30分钟温服
医嘱：1.增加亲子之间交流和互动，家长做好聆听，鼓励孩子表达自己的情绪。
2.减少电子产品的使用，禁止睡前玩电子游戏和观看情节紧张的影视作品。
3.饮食应定时定量，养成良好的饮食习惯，食物宜清淡而富有营养，荤素搭配，不挑食不偏食，忌食冰 冷饮食、饮料、零食等含食物添加剂食品，尤其避免食用奶茶、巧克力、咖啡等会引起人体兴奋的食物。
4.作息应规律，注意劳逸结合，不要过多给孩子增添压力，使其造成紧张、焦虑、自卑情绪。
5.适当增加户外活动”

记住，成分与克数必须按照主次顺序写成一行， 医嘱绝对不能超过100字。除了需要你写的这几个字段之外，绝对不要在开头和结尾添加任何不必要的内容。

对以下病人基本状况描述给出相应的 中医诊断、西医诊断、辨证证型、治则、处方名、成分与克数、付数、用法、医嘱。

"""

for i in range(1, 7):
    input_file = 'dialogue/60dialogues.xlsx'
    output_file = f"dialogue/doubao/doubao_thinking_{i}.csv"

    df = pd.read_excel(input_file, dtype=str)

    # Track already processed IDs (to resume safely)
    processed_ids = set()
    if Path(output_file).exists():
        with open(output_file, mode="r", encoding="utf-8") as existing:
            reader = csv.DictReader(existing)
            processed_ids = {row["id"] for row in reader}

    with open(output_file, mode="a", newline='', encoding="utf-8") as outfile:
        writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)

        # Write header if file doesn't exist
        if not Path(output_file).exists() or os.stat(output_file).st_size == 0:
            writer.writerow(
                ["id", "response", "duration", 'input_token_count', 'output_token_count', 'total_token_count'])

        for _, row in tqdm(df.iterrows()):
            q_id = row["id"]
            question = row["question"]

            if q_id in processed_ids:
                continue  # Skip already processed

            # question = prompt + question
            try:
                start_time = time.time()

                response = client.chat.completions.create(
                    model="doubao-seed-1-6-thinking-250715",
                    messages=[{"role": "system", "content": prompt}, {"role": "user", "content": question}]
                )
                answer = response.choices[0].message.content.strip()

                input_token_count = response.usage.prompt_tokens
                output_token_count = response.usage.completion_tokens
                total_token_count = response.usage.total_tokens

                duration = round(time.time() - start_time, 2)
            except Exception as e:
                print(e)
                break

            writer.writerow([q_id, answer, duration, input_token_count, output_token_count, total_token_count])
            outfile.flush()  # Ensure data is written to disk
            time.sleep(2)