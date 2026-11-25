"""statstools 命令行入口。"""

from __future__ import annotations

import argparse
import math
import sys
from typing import List, Optional, Sequence

from .stats import MAX_ABS_VALUE, MAX_VALUES, Summary, summarize
from .worksheet import MAX_COUNT, QuizItem, generate_worksheet, make_quiz


def _ensure_utf8_console() -> None:
    """尽量把标准输出与标准错误切换为 UTF-8，失败时静默跳过。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if not callable(reconfigure):
            continue
        try:
            reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            continue


def parse_data(text: str) -> List[float]:
    """把逗号、空格、制表符或换行分隔的数据解析为浮点数列表。"""
    if isinstance(text, bool) or not isinstance(text, str):
        raise TypeError("数据必须是字符串")
    tokens = text.replace(",", " ").split()
    if not tokens:
        raise ValueError("数据不能为空")
    values: List[float] = []
    for token in tokens:
        try:
            number = float(token)
        except ValueError:
            raise ValueError("不是合法数字：%s" % token) from None
        if not math.isfinite(number):
            raise ValueError("不是合法数字：%s" % token)
        if abs(number) > MAX_ABS_VALUE:
            raise ValueError("数字超出范围（绝对值不能超过 1e9）：%s" % token)
        values.append(number)
        if len(values) > MAX_VALUES:
            raise ValueError("数据个数不能超过 %d 个" % MAX_VALUES)
    return values


def _read_text(path: str) -> str:
    """读取 UTF-8 文本文件，失败时转换为中文 ValueError。"""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except FileNotFoundError as exc:
        raise ValueError("读取文件失败：%s（文件不存在）" % path) from exc
    except IsADirectoryError as exc:
        raise ValueError("读取文件失败：%s（这是一个目录，不是文件）" % path) from exc
    except PermissionError as exc:
        raise ValueError("读取文件失败：%s（没有读取权限）" % path) from exc
    except UnicodeDecodeError as exc:
        raise ValueError("读取文件失败：%s（不是 UTF-8 编码的文本）" % path) from exc
    except OSError as exc:
        raise ValueError(
            "读取文件失败：%s（%s）" % (path, exc.strerror or exc)
        ) from exc


def _write_text(path: str, content: str) -> None:
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
    except OSError as exc:
        raise ValueError("写入文件失败：{0}（{1}）".format(path, exc.strerror or exc)) from exc


def _format_value(value: Optional[float]) -> str:
    if value is None:
        return "—"
    rounded = round(float(value), 2)
    if rounded == 0:
        rounded = 0.0
    return "%.2f" % rounded


def _format_modes(values: Sequence[float]) -> str:
    if not values:
        return "无"
    return "、".join(_format_value(value) for value in values)


def _describe_lines(summary: Summary) -> List[str]:
    return [
        "个数：%d" % summary.count,
        "总和：%s" % _format_value(summary.total),
        "平均数：%s" % _format_value(summary.mean),
        "中位数：%s" % _format_value(summary.median),
        "众数：%s" % _format_modes(summary.modes),
        "极差：%s" % _format_value(summary.range_value),
        "总体方差：%s" % _format_value(summary.population_variance),
        "总体标准差：%s" % _format_value(summary.population_stdev),
        "样本方差：%s" % _format_value(summary.sample_variance),
        "样本标准差：%s" % _format_value(summary.sample_stdev),
    ]


def _count_type(text: str) -> int:
    try:
        value = int(text)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError("题目数量必须是整数：%s" % text) from None
    if value < 1 or value > MAX_COUNT:
        raise argparse.ArgumentTypeError(
            "题目数量必须在 1 到 %d 之间：%s" % (MAX_COUNT, text)
        )
    return value


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="statstools",
        description="初中数学统计量计算与练习纸生成工具",
    )
    subparsers = parser.add_subparsers(
        dest="command", metavar="COMMAND", required=True, help="可用的子命令"
    )

    describe_parser = subparsers.add_parser(
        "describe", help="计算一组数据的平均数、中位数、众数、极差、方差等"
    )
    describe_parser.add_argument(
        "--data", metavar="DATA", help="逗号、空格或换行分隔的数据，例如 85,90,78"
    )
    describe_parser.add_argument(
        "--file", metavar="FILE", help="从 UTF-8 文本文件读取数据"
    )

    quiz_parser = subparsers.add_parser(
        "quiz", help="随机生成平均数、中位数、众数、极差、方差练习题"
    )
    quiz_parser.add_argument(
        "--count", type=_count_type, default=5, metavar="N", help="题目数量（默认 5）"
    )
    quiz_parser.add_argument(
        "--seed", type=int, default=None, metavar="SEED", help="随机种子，相同种子可复现"
    )

    worksheet_parser = subparsers.add_parser(
        "worksheet", help="生成带数据表格与折叠答案的 HTML 练习纸"
    )
    worksheet_parser.add_argument(
        "--count", type=_count_type, default=10, metavar="N", help="题目数量（默认 10）"
    )
    worksheet_parser.add_argument(
        "--seed", type=int, default=None, metavar="SEED", help="随机种子，相同种子可复现"
    )
    worksheet_parser.add_argument(
        "--out", required=True, metavar="PATH", help="输出 HTML 文件路径"
    )

    subparsers.add_parser("demo", help="演示统计量计算与三道示例题")
    return parser


def _describe_command(args: argparse.Namespace) -> int:
    data_text = getattr(args, "data", None)
    file_path = getattr(args, "file", None)
    if data_text is not None and file_path is not None:
        raise ValueError("--data 与 --file 不能同时使用")
    if data_text is None and file_path is None:
        raise ValueError("请通过 --data 或 --file 提供数据")
    if isinstance(data_text, str):
        values = parse_data(data_text)
    else:
        values = parse_data(_read_text(file_path))
    summary = summarize(values)
    print("\n".join(_describe_lines(summary)))
    return 0


def _quiz_command(args: argparse.Namespace) -> int:
    items = make_quiz(args.count, args.seed)
    lines: List[str] = []
    for index, item in enumerate(items, start=1):
        lines.append("第 %d 题（%s）" % (index, item.kind))
        lines.append(item.question)
        lines.append("")
    lines.append("答案：")
    for index, item in enumerate(items, start=1):
        lines.append("%d. %s" % (index, item.answer))
    print("\n".join(lines))
    return 0


def _worksheet_command(args: argparse.Namespace) -> int:
    content = generate_worksheet(args.count, args.seed)
    _write_text(args.out, content)
    print("已生成练习纸：%s（共 %d 题）" % (args.out, args.count))
    return 0


def _demo_command() -> int:
    sample = [85.0, 90.0, 78.0, 92.0, 88.0]
    print("示例数据：85, 90, 78, 92, 88")
    print("\n".join(_describe_lines(summarize(sample))))
    print("")
    items = make_quiz(3, 2026)
    print("示例题目：")
    for index, item in enumerate(items, start=1):
        print("第 %d 题（%s）%s" % (index, item.kind, item.question))
    print("")
    answers = "；".join(
        "%d. %s" % (index, item.answer)
        for index, item in enumerate(items, start=1)
    )
    print("答案：%s" % answers)
    return 0


def _run(args: argparse.Namespace) -> int:
    command = args.command
    if command == "describe":
        return _describe_command(args)
    if command == "quiz":
        return _quiz_command(args)
    if command == "worksheet":
        return _worksheet_command(args)
    if command == "demo":
        return _demo_command()
    raise ValueError("未知子命令：%s" % command)


def _normalize_argv(argv: Optional[Sequence[str]]) -> Optional[List[str]]:
    """把 --data 后的负数数据改写为 --data=... 形式，避免被当成选项。"""
    if argv is None:
        return None
    tokens = list(argv)
    result: List[str] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == "--data" and index + 1 < len(tokens):
            candidate = tokens[index + 1]
            if candidate.startswith("-") and not candidate.startswith("--"):
                result.append("--data=" + candidate)
                index += 2
                continue
        result.append(token)
        index += 1
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    _ensure_utf8_console()
    parser = build_parser()
    args = parser.parse_args(_normalize_argv(argv))
    try:
        return _run(args)
    except (TypeError, ValueError) as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
