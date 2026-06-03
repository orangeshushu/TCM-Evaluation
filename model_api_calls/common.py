from __future__ import annotations

import argparse
import csv
import os
import re
import time
from pathlib import Path
from typing import Callable, Iterable

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable


PROMPT = """假设你是一位有着数十年行医经验的中医医生，精通中医的各个领域知识。请你对我接下来给出的病人基本状况描述给出相应的中西医诊断和药方，请注意你回答的专业性、客观性和安全性。以下是一个患者的例子：
“一般情况：    性别：女    年龄：16岁
初诊日期：2023年9月12日
主诉：睡眠欠佳半年。
现病史：患儿近半年出现睡眠差，难入睡，睡着后容易惊醒，时常做噩梦，心烦，不愿外出，会独自哭 泣，有厌学情绪，精总诊断抑郁症，现百忧解口服中，白天头晕头痛，昏沉欲睡，时觉乏力，脱发严重，怕冷 欲穿衣，手脚冰凉，无胸闷心慌，胃纳欠佳，纳呆不欲饮食，大便尚可，月经至，但经期较长，9-10天1次，周 期正常，偶有痛经，时伴腰膝酸软。为进一步诊疗于生长发育和心理门诊就诊。
刻诊：神情疲惫，不善言语，胃纳欠佳，二便尚调。
专科检查：36.9℃,神志清，精神可，形体正常，面色萎黄，五官端正，眼睑无充血，鼻腔内干净，咽不红， 两侧扁桃腺无肿大，语声低微，气息均匀，胸廓对称，呼吸运动正常，肋间隙无明显增宽，触觉语颤对称，无 胸膜摩擦感，两肺叩诊呈正常清音，听诊两肺呼吸音稍粗，两肺未闻及明显干湿罗音，语音传导对称存在， 未及胸膜摩擦音。心率：80次/分，律齐，第一心音有力，各瓣膜听诊区未及病理性杂音，腹平软，全腹无压 痛及反跳痛，肠鸣音正常，肝肾无叩击痛，双下肢无水肿，四肢肌力、肌张力均正常，翻手试验、指鼻试验、 点指试验均为阴性。”
你需要根据以上的病例描述，请逐项给出类似下面格式的诊断信息。如：中医诊断、西医诊断、辨证证型、治则、处方名（如有方名请写方名，可以加减；无方名可自拟）、成分与克数（写成一行，中间用空格分隔）、付数、用法、医嘱（限制100字）等。
“中医诊断：不寐病
辨证证型：脾肾阳虚
西医诊断：睡眠障碍
治则：温肾潜阳，补益心脾，安神定志
处方名：自拟温潜安神方。
成分与克数（按照主次顺序）：附子3g 黄连3g 首乌藤10g 桂枝6g 党参9g 茯苓9g 酸枣仁9g 郁金9g 淮小麦15g 紫贝齿15g 龙齿15g 珍珠母9g 磁石15g 远志6g 炙甘草3g 柴胡5g
付数：28剂
用法：以草药代煎每日早晚各一包餐后30分钟温服
医嘱：1.增加亲子之间交流和互动，家长做好聆听，鼓励孩子表达自己的情绪。
2.减少电子产品的使用，禁止睡前玩电子游戏和观看情节紧张的影视作品。
3.饮食应定时定量，养成良好的饮食习惯，食物宜清淡而富有营养，荤素搭配，不挑食不偏食，忌食冰 冷饮食、饮料、零食等含食物添加剂食品，尤其避免食用奶茶、巧克力、咖啡等会引起人体兴奋的食物。
4.作息应规律，注意劳逸结合，不要过多给孩子增添压力，使其造成紧张、焦虑、自卑情绪。
5.适当增加户外活动”
如果你明白了你要回答的内容和任务，请回答你准备好了，然后我会给你一个新的病例，你需要给出我类似以上的回答信息。

记住：成分与克数必须按照主次顺序写成一行，中间用空格分隔；医嘱绝对不能超过100字。除了需要你写的这九个字段之外，绝对不要在开头和结尾添加任何不必要的内容。
"""

OUTPUT_FIELDS = [
    "中医诊断",
    "辨证证型",
    "西医诊断",
    "治则",
    "处方名",
    "成分与克数",
    "付数",
    "用法",
    "医嘱",
]

CSV_FIELDS = [
    "id",
    *OUTPUT_FIELDS,
    "raw_response",
    "duration",
    "input_token_count",
    "output_token_count",
    "total_token_count",
]

CASE_COLUMN_CANDIDATES = [
    "case",
    "clinical_case",
    "question",
    "prompt",
    "题目",
    "病例",
    "病例描述",
    "患者情况",
]
ID_COLUMN_CANDIDATES = ["id", "case_id", "编号", "序号"]

FIELD_ALIASES = {
    "中医诊断": ["中医诊断"],
    "辨证证型": ["辨证证型", "辩证证型", "辨证证型（证型）", "证型"],
    "西医诊断": ["西医诊断"],
    "治则": ["治则", "治 则"],
    "处方名": ["处方名", "方名"],
    "成分与克数": ["成分与克数", "成分与克数（按照主次顺序）", "药物组成", "处方组成"],
    "付数": ["付数", "剂数"],
    "用法": ["用法"],
    "医嘱": ["医嘱"],
}


def build_parser(model_label: str, default_output: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"Run {model_label} on 60 clinical cases.")
    parser.add_argument(
        "--input",
        default="data/benchmark_cases/60_clinical_cases.csv",
        help="CSV file containing one clinical case per row.",
    )
    parser.add_argument(
        "--output",
        default=default_output,
        help="Output CSV path. Existing rows are used for resume.",
    )
    parser.add_argument("--case-column", default=None, help="Column containing the case text.")
    parser.add_argument("--id-column", default=None, help="Column containing the case id.")
    parser.add_argument("--limit", type=int, default=None, help="Optional maximum number of rows to process.")
    parser.add_argument("--sleep", type=float, default=1.0, help="Seconds to sleep between requests.")
    return parser


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def read_cases(input_path: str, case_column: str | None, id_column: str | None) -> list[dict[str, str]]:
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input CSV not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        return []

    columns = list(rows[0].keys())
    case_col = case_column or _first_existing(columns, CASE_COLUMN_CANDIDATES) or columns[-1]
    id_col = id_column or _first_existing(columns, ID_COLUMN_CANDIDATES)

    cases: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        case_id = row.get(id_col, "").strip() if id_col else str(index)
        case_text = row.get(case_col, "").strip()
        if not case_text:
            continue
        cases.append({"id": case_id or str(index), "case": case_text})
    return cases


def _first_existing(columns: Iterable[str], candidates: Iterable[str]) -> str | None:
    column_set = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate.lower() in column_set:
            return column_set[candidate.lower()]
    return None


def load_processed_ids(output_path: str) -> set[str]:
    path = Path(output_path)
    if not path.exists() or path.stat().st_size == 0:
        return set()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row["id"] for row in csv.DictReader(handle) if row.get("id")}


def append_result(output_path: str, row: dict[str, object]) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists() and path.stat().st_size > 0
    with path.open("a", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, quoting=csv.QUOTE_ALL)
        if not file_exists:
            writer.writeheader()
        writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def parse_response(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()

    for field, aliases in FIELD_ALIASES.items():
        alias_pattern = "|".join(re.escape(alias) for alias in aliases)
        next_aliases = [
            alias
            for next_field, next_field_aliases in FIELD_ALIASES.items()
            if next_field != field
            for alias in next_field_aliases
        ]
        next_pattern = "|".join(re.escape(alias) for alias in next_aliases)
        pattern = rf"(?:^|\n)\s*(?:{alias_pattern})\s*(?:[:：])\s*(.*?)(?=\n\s*(?:{next_pattern})\s*[:：]|\Z)"
        match = re.search(pattern, normalized, flags=re.S)
        parsed[field] = " ".join(match.group(1).split()) if match else ""

    return parsed


def make_messages(case_text: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": f"请对以下病例给出九个字段的诊断和处方信息：\n{case_text}"},
    ]


def make_user_text(case_text: str) -> str:
    return f"请对以下病例给出九个字段的诊断和处方信息：\n{case_text}"


def run_cases(
    model_label: str,
    default_output: str,
    call_model: Callable[[str], tuple[str, dict[str, object]]],
) -> None:
    args = build_parser(model_label, default_output).parse_args()
    cases = read_cases(args.input, args.case_column, args.id_column)
    if args.limit:
        cases = cases[: args.limit]

    processed_ids = load_processed_ids(args.output)
    for case in tqdm(cases, desc=model_label):
        case_id = case["id"]
        if case_id in processed_ids:
            continue

        start = time.time()
        answer, usage = call_model(case["case"])
        duration = round(time.time() - start, 2)
        fields = parse_response(answer)

        append_result(
            args.output,
            {
                "id": case_id,
                **fields,
                "raw_response": answer,
                "duration": duration,
                "input_token_count": usage.get("input_token_count", ""),
                "output_token_count": usage.get("output_token_count", ""),
                "total_token_count": usage.get("total_token_count", ""),
            },
        )
        processed_ids.add(case_id)
        if args.sleep:
            time.sleep(args.sleep)


def openai_chat_usage(response: object) -> dict[str, object]:
    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "prompt_tokens", "") if usage else ""
    output_tokens = getattr(usage, "completion_tokens", "") if usage else ""
    total_tokens = getattr(usage, "total_tokens", "") if usage else ""
    return {
        "input_token_count": input_tokens,
        "output_token_count": output_tokens,
        "total_token_count": total_tokens,
    }


def openai_response_text(response: object) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text.strip()

    chunks: list[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                chunks.append(text)
    return "\n".join(chunks).strip()


def openai_response_usage(response: object) -> dict[str, object]:
    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "input_tokens", "") if usage else ""
    output_tokens = getattr(usage, "output_tokens", "") if usage else ""
    total_tokens = getattr(usage, "total_tokens", "") if usage else ""
    return {
        "input_token_count": input_tokens,
        "output_token_count": output_tokens,
        "total_token_count": total_tokens,
    }
