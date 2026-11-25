"""statstools：初中数学统计量计算与出题工具。"""

from __future__ import annotations

from .stats import (
    Summary,
    mean,
    median,
    modes,
    range_value,
    std_dev,
    summarize,
    variance,
)
from .worksheet import generate_worksheet, make_quiz

__version__ = "0.1.0"

__all__ = [
    "Summary",
    "summarize",
    "mean",
    "median",
    "modes",
    "range_value",
    "variance",
    "std_dev",
    "make_quiz",
    "generate_worksheet",
    "__version__",
]
