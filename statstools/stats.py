"""统计量计算：平均数、中位数、众数、极差、方差与标准差。"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

MAX_VALUES = 10000
MAX_ABS_VALUE = 1e9


@dataclass(frozen=True)
class Summary:
    """一组数据的完整描述性统计结果。"""

    count: int
    total: float
    mean: float
    median: float
    modes: Tuple[float, ...]
    range_value: float
    population_variance: float
    population_stdev: float
    sample_variance: Optional[float]
    sample_stdev: Optional[float]


def _normalize(values: Iterable[float]) -> List[float]:
    """校验外部数据并转为浮点数列表。

    规则：不能为空、不能是布尔值、必须是有限数值、绝对值不超过 1e9、
    数据个数不超过 10000。
    """
    if isinstance(values, (str, bytes)):
        raise TypeError("数据必须是数字序列")
    data: List[float] = []
    for value in values:
        if isinstance(value, bool):
            raise TypeError("数据不能包含布尔值")
        if not isinstance(value, (int, float)):
            raise TypeError("数据必须是数字：%r" % (value,))
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("数据必须是有限数值：%r" % (value,))
        if abs(number) > MAX_ABS_VALUE:
            raise ValueError("数据绝对值不能超过 1e9：%r" % (value,))
        data.append(number)
        if len(data) > MAX_VALUES:
            raise ValueError("数据个数不能超过 %d 个" % MAX_VALUES)
    if not data:
        raise ValueError("至少需要 1 个数据")
    return data


def mean(values: Iterable[float]) -> float:
    """算术平均数。"""
    data = _normalize(values)
    return math.fsum(data) / len(data)


def median(values: Iterable[float]) -> float:
    """中位数；偶数个数据时取中间两个数的平均值。"""
    data = sorted(_normalize(values))
    size = len(data)
    middle = size // 2
    if size % 2 == 1:
        return data[middle]
    return math.fsum([data[middle - 1], data[middle]]) / 2.0


def modes(values: Iterable[float]) -> Tuple[float, ...]:
    """众数；并列时全部返回并按升序排列，没有重复值时返回空元组。"""
    data = _normalize(values)
    counts: Dict[float, int] = {}
    for value in data:
        counts[value] = counts.get(value, 0) + 1
    highest = max(counts.values())
    if highest <= 1:
        return ()
    return tuple(sorted(value for value, count in counts.items() if count == highest))


def range_value(values: Iterable[float]) -> float:
    """极差（最大值减最小值）。"""
    data = _normalize(values)
    return max(data) - min(data)


def variance(values: Iterable[float], sample: bool = False) -> Optional[float]:
    """方差；默认总体方差（除以 n），sample 为真时返回样本方差（除以 n-1）。

    样本方差在数据少于 2 个时无法计算，返回 None。
    """
    data = _normalize(values)
    size = len(data)
    if sample and size < 2:
        return None
    average = math.fsum(data) / size
    squares = math.fsum((value - average) ** 2 for value in data)
    if sample:
        return squares / (size - 1)
    return squares / size


def std_dev(values: Iterable[float], sample: bool = False) -> Optional[float]:
    """标准差；与方差对应，样本标准差在数据少于 2 个时返回 None。"""
    result = variance(values, sample=sample)
    if result is None:
        return None
    return math.sqrt(result)


def summarize(values: Iterable[float]) -> Summary:
    """一次计算个数、总和、平均数、中位数、众数、极差、方差与标准差。"""
    data = _normalize(values)
    count = len(data)
    total = math.fsum(data)
    average = total / count

    ordered = sorted(data)
    middle = count // 2
    if count % 2 == 1:
        middle_value = ordered[middle]
    else:
        middle_value = math.fsum([ordered[middle - 1], ordered[middle]]) / 2.0

    counts: Dict[float, int] = {}
    for value in data:
        counts[value] = counts.get(value, 0) + 1
    highest = max(counts.values())
    if highest <= 1:
        mode_values: Tuple[float, ...] = ()
    else:
        mode_values = tuple(
            sorted(value for value, times in counts.items() if times == highest)
        )

    squares = math.fsum((value - average) ** 2 for value in data)
    population_variance = squares / count
    if count >= 2:
        sample_variance: Optional[float] = squares / (count - 1)
        sample_stdev: Optional[float] = math.sqrt(sample_variance)
    else:
        sample_variance = None
        sample_stdev = None

    return Summary(
        count=count,
        total=total,
        mean=average,
        median=middle_value,
        modes=mode_values,
        range_value=max(data) - min(data),
        population_variance=population_variance,
        population_stdev=math.sqrt(population_variance),
        sample_variance=sample_variance,
        sample_stdev=sample_stdev,
    )


def format_answer(value: float) -> str:
    """把数值格式化为最多 2 位小数并去掉多余的 0，用于题目答案。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("答案必须是数字")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("答案必须是有限数值")
    text = ("%.2f" % number).rstrip("0").rstrip(".")
    if text in ("", "-0"):
        text = "0"
    return text
