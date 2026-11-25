"""统计量练习题的生成与练习纸 HTML 输出。"""

from __future__ import annotations

import html
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .stats import format_answer, mean, median, modes, range_value, variance

QUIZ_KINDS: Tuple[str, ...] = ("平均数", "中位数", "众数", "极差", "方差")
MAX_COUNT = 100

_STYLE = """
body { font-family: "PingFang SC", "Microsoft YaHei", sans-serif; margin: 32px auto; max-width: 780px; color: #222; line-height: 1.7; padding: 0 16px; }
h1 { font-size: 22px; border-bottom: 2px solid #4a6fa5; padding-bottom: 8px; }
.meta { color: #666; font-size: 14px; }
ol { padding-left: 24px; }
li { margin-bottom: 22px; }
.prompt { margin: 0 0 8px; font-weight: 600; }
table.data { border-collapse: collapse; margin-bottom: 8px; }
table.data th, table.data td { border: 1px solid #8899aa; padding: 4px 10px; text-align: center; }
table.data th { background: #eef2f7; font-weight: 600; }
details { margin-top: 6px; color: #1f5f3f; }
summary { cursor: pointer; color: #4a6fa5; }
"""


@dataclass(frozen=True)
class QuizItem:
    """一道统计量练习题。"""

    kind: str
    data: List[float]
    question: str
    answer: str


def _check_count(count: int) -> int:
    if isinstance(count, bool) or not isinstance(count, int):
        raise TypeError("题目数量必须是整数")
    if count < 1 or count > MAX_COUNT:
        raise ValueError("题目数量必须在 1 到 %d 之间" % MAX_COUNT)
    return count


def _check_seed(seed: Optional[int]) -> Optional[int]:
    if seed is None:
        return None
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("随机种子必须是整数")
    return seed


def _format_data_number(value: float) -> str:
    if value == int(value):
        return str(int(value))
    return format_answer(value)


def _required_variance(data: List[float]) -> float:
    result = variance(data, sample=False)
    if result is None:
        raise ValueError("总体方差不应为空")
    return result


def _answer_for(kind: str, data: List[float]) -> str:
    if kind == "平均数":
        return format_answer(mean(data))
    if kind == "中位数":
        return format_answer(median(data))
    if kind == "众数":
        found = modes(data)
        if not found:
            return "无"
        return "、".join(format_answer(value) for value in found)
    if kind == "极差":
        return format_answer(range_value(data))
    return format_answer(_required_variance(data))


def make_quiz(count: int = 5, seed: Optional[int] = None) -> List[QuizItem]:
    """生成随机练习题；相同 seed 结果完全一致，题型按五类循环覆盖。"""
    total = _check_count(count)
    actual_seed = _check_seed(seed)
    generator = random.Random(actual_seed)
    items: List[QuizItem] = []
    for index in range(total):
        kind = QUIZ_KINDS[index % len(QUIZ_KINDS)]
        size = generator.randint(5, 8)
        low = generator.choice([0, 1, 2, 5])
        high = low + generator.randint(5, 15)
        data = [float(generator.randint(low, high)) for _ in range(size)]
        data_text = "，".join(_format_data_number(value) for value in data)
        question = "已知一组数据：%s。求这组数据的%s。" % (data_text, kind)
        items.append(
            QuizItem(
                kind=kind,
                data=data,
                question=question,
                answer=_answer_for(kind, data),
            )
        )
    return items


def generate_worksheet(count: int = 10, seed: Optional[int] = None) -> str:
    """生成含数据表格、可折叠答案的练习纸 HTML。"""
    items = make_quiz(count, seed)
    parts: List[str] = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>统计量练习纸</title>",
        "<style>%s</style>" % _STYLE,
        "</head>",
        "<body>",
        "<h1>统计量练习纸</h1>",
        '<p class="meta">共 %d 题，请写出必要的计算过程。</p>' % len(items),
        "<ol>",
    ]
    for item in items:
        header_cells = "".join(
            "<th>%d</th>" % position for position in range(1, len(item.data) + 1)
        )
        value_cells = "".join(
            "<td>%s</td>" % html.escape(_format_data_number(value))
            for value in item.data
        )
        parts.append("<li>")
        parts.append(
            '<p class="prompt">求这组数据的%s。</p>' % html.escape(item.kind)
        )
        parts.append(
            '<table class="data"><thead><tr><th>序号</th>%s</tr></thead>'
            "<tbody><tr><th>数值</th>%s</tr></tbody></table>"
            % (header_cells, value_cells)
        )
        parts.append(
            "<details><summary>查看答案</summary><p>答案：%s</p></details>"
            % html.escape(item.answer)
        )
        parts.append("</li>")
    parts.extend(["</ol>", "</body>", "</html>"])
    return "\n".join(parts) + "\n"
