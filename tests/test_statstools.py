"""statstools 单元测试。"""

from __future__ import annotations

import io
import math
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from typing import List, Tuple
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from statstools import (  # noqa: E402
    Summary,
    generate_worksheet,
    make_quiz,
    mean,
    median,
    modes,
    range_value,
    std_dev,
    summarize,
    variance,
)
from statstools import cli  # noqa: E402
from statstools.stats import MAX_VALUES, format_answer  # noqa: E402


def run_cli(argv: List[str]) -> Tuple[int, str, str]:
    """运行 CLI 并捕获退出码、标准输出与标准错误。"""
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = cli.main(argv)
    return code, stdout.getvalue(), stderr.getvalue()


class TestMean(unittest.TestCase):
    def test_mean_integers(self) -> None:
        self.assertEqual(mean([1, 2, 3, 4]), 2.5)

    def test_mean_single_value(self) -> None:
        self.assertEqual(mean([7]), 7.0)

    def test_mean_negative_numbers(self) -> None:
        self.assertEqual(mean([-2, -4]), -3.0)

    def test_mean_decimals(self) -> None:
        self.assertEqual(mean([1.5, 2.5]), 2.0)

    def test_mean_large_values(self) -> None:
        self.assertEqual(mean([1e9, 1e9]), 1e9)


class TestMedian(unittest.TestCase):
    def test_median_odd(self) -> None:
        self.assertEqual(median([3, 1, 2]), 2.0)

    def test_median_even(self) -> None:
        self.assertEqual(median([4, 1, 3, 2]), 2.5)

    def test_median_single(self) -> None:
        self.assertEqual(median([5]), 5.0)

    def test_median_negative_decimals(self) -> None:
        self.assertEqual(median([-3.5, -1.0, -2.0]), -2.0)

    def test_median_does_not_mutate_input(self) -> None:
        data = [3, 1, 2]
        median(data)
        self.assertEqual(data, [3, 1, 2])


class TestModes(unittest.TestCase):
    def test_single_mode(self) -> None:
        self.assertEqual(modes([2, 4, 4, 4, 5, 5, 7, 9]), (4.0,))

    def test_multiple_modes_sorted(self) -> None:
        self.assertEqual(modes([3, 3, 1, 1, 2]), (1.0, 3.0))

    def test_no_mode_returns_empty_tuple(self) -> None:
        self.assertEqual(modes([1, 2, 3]), ())

    def test_all_same_values(self) -> None:
        self.assertEqual(modes([5, 5, 5]), (5.0,))

    def test_modes_returns_tuple(self) -> None:
        self.assertIsInstance(modes([1, 1, 2]), tuple)


class TestRange(unittest.TestCase):
    def test_range_basic(self) -> None:
        self.assertEqual(range_value([2, 4, 4, 4, 5, 5, 7, 9]), 7.0)

    def test_range_single_value_is_zero(self) -> None:
        self.assertEqual(range_value([3]), 0.0)

    def test_range_negative_numbers(self) -> None:
        self.assertEqual(range_value([-5, -1, -3]), 4.0)


class TestVariance(unittest.TestCase):
    def test_population_variance_known(self) -> None:
        self.assertEqual(variance([2, 4, 4, 4, 5, 5, 7, 9]), 4.0)

    def test_population_stdev_known(self) -> None:
        self.assertEqual(std_dev([2, 4, 4, 4, 5, 5, 7, 9]), 2.0)

    def test_sample_variance_known(self) -> None:
        result = variance([2, 4, 4, 4, 5, 5, 7, 9], sample=True)
        self.assertAlmostEqual(result, 32.0 / 7.0, places=12)

    def test_sample_stdev_known(self) -> None:
        result = std_dev([2, 4, 4, 4, 5, 5, 7, 9], sample=True)
        self.assertAlmostEqual(result, math.sqrt(32.0 / 7.0), places=12)

    def test_population_variance_single_is_zero(self) -> None:
        self.assertEqual(variance([7]), 0.0)

    def test_sample_variance_single_is_none(self) -> None:
        self.assertIsNone(variance([7], sample=True))

    def test_sample_stdev_single_is_none(self) -> None:
        self.assertIsNone(std_dev([7], sample=True))

    def test_variance_two_values(self) -> None:
        self.assertEqual(variance([2, 4]), 1.0)
        self.assertEqual(variance([2, 4], sample=True), 2.0)

    def test_variance_negative_decimals(self) -> None:
        self.assertEqual(variance([-1.5, 0.5]), 1.0)
        self.assertEqual(variance([-1.5, 0.5], sample=True), 2.0)


class TestSummarize(unittest.TestCase):
    def test_summary_basic_fields(self) -> None:
        summary = summarize([2, 4, 4, 4, 5, 5, 7, 9])
        self.assertEqual(summary.count, 8)
        self.assertEqual(summary.total, 40.0)
        self.assertEqual(summary.mean, 5.0)
        self.assertEqual(summary.median, 4.5)
        self.assertEqual(summary.modes, (4.0,))
        self.assertEqual(summary.range_value, 7.0)

    def test_summary_variance_fields(self) -> None:
        summary = summarize([2, 4, 4, 4, 5, 5, 7, 9])
        self.assertEqual(summary.population_variance, 4.0)
        self.assertEqual(summary.population_stdev, 2.0)
        self.assertAlmostEqual(summary.sample_variance, 32.0 / 7.0, places=12)
        self.assertAlmostEqual(
            summary.sample_stdev, math.sqrt(32.0 / 7.0), places=12
        )

    def test_summary_single_value(self) -> None:
        summary = summarize([7])
        self.assertIsInstance(summary, Summary)
        self.assertEqual(summary.modes, ())
        self.assertEqual(summary.range_value, 0.0)
        self.assertIsNone(summary.sample_variance)
        self.assertIsNone(summary.sample_stdev)


class TestValidation(unittest.TestCase):
    def test_empty_data_mean_raises(self) -> None:
        with self.assertRaises(ValueError):
            mean([])

    def test_empty_data_summarize_raises(self) -> None:
        with self.assertRaises(ValueError):
            summarize([])

    def test_empty_data_other_functions_raise(self) -> None:
        for function in (median, modes, range_value, variance, std_dev):
            with self.assertRaises(ValueError):
                function([])

    def test_nan_rejected(self) -> None:
        with self.assertRaises(ValueError):
            mean([1.0, float("nan")])

    def test_positive_inf_rejected(self) -> None:
        with self.assertRaises(ValueError):
            variance([float("inf")])

    def test_negative_inf_rejected(self) -> None:
        with self.assertRaises(ValueError):
            std_dev([float("-inf")])

    def test_bool_in_data_rejected(self) -> None:
        with self.assertRaises(TypeError):
            mean([True, 2])

    def test_bool_only_data_rejected(self) -> None:
        with self.assertRaises(TypeError):
            summarize([True])

    def test_string_in_data_rejected(self) -> None:
        with self.assertRaises(TypeError):
            median(["1", "2"])

    def test_too_many_values_rejected(self) -> None:
        with self.assertRaises(ValueError):
            summarize(range(MAX_VALUES + 1))

    def test_max_values_allowed(self) -> None:
        self.assertEqual(mean(range(MAX_VALUES)), (MAX_VALUES - 1) / 2.0)

    def test_absolute_limit_allowed(self) -> None:
        self.assertEqual(mean([1e9]), 1e9)

    def test_above_absolute_limit_rejected(self) -> None:
        with self.assertRaises(ValueError):
            mean([1e9 + 1])


class TestParseData(unittest.TestCase):
    def test_comma_separated(self) -> None:
        self.assertEqual(cli.parse_data("85,90,78"), [85.0, 90.0, 78.0])

    def test_whitespace_separated(self) -> None:
        self.assertEqual(cli.parse_data("1 2\t3\n4"), [1.0, 2.0, 3.0, 4.0])

    def test_mixed_separators(self) -> None:
        self.assertEqual(cli.parse_data("1, 2\n3\t4,5"), [1.0, 2.0, 3.0, 4.0, 5.0])

    def test_negative_decimals(self) -> None:
        self.assertEqual(cli.parse_data("-1.5, +2.5"), [-1.5, 2.5])

    def test_empty_raises(self) -> None:
        with self.assertRaises(ValueError):
            cli.parse_data("")

    def test_whitespace_only_raises(self) -> None:
        with self.assertRaises(ValueError):
            cli.parse_data("   \n\t ")

    def test_non_numeric_raises(self) -> None:
        with self.assertRaises(ValueError):
            cli.parse_data("1,abc")

    def test_nan_raises(self) -> None:
        with self.assertRaises(ValueError):
            cli.parse_data("1,nan")

    def test_inf_raises(self) -> None:
        with self.assertRaises(ValueError):
            cli.parse_data("inf")

    def test_wrong_type_raises(self) -> None:
        with self.assertRaises(TypeError):
            cli.parse_data(True)


class TestQuiz(unittest.TestCase):
    def test_quiz_reproducible(self) -> None:
        first = make_quiz(5, 2026)
        second = make_quiz(5, 2026)
        self.assertEqual(
            [item.question for item in first],
            [item.question for item in second],
        )
        self.assertEqual(
            [item.answer for item in first],
            [item.answer for item in second],
        )

    def test_quiz_five_kinds(self) -> None:
        items = make_quiz(5, 2026)
        self.assertEqual(
            [item.kind for item in items],
            ["平均数", "中位数", "众数", "极差", "方差"],
        )

    def test_quiz_count(self) -> None:
        self.assertEqual(len(make_quiz(12, 2026)), 12)

    def test_quiz_mean_answer_correct(self) -> None:
        item = make_quiz(5, 2026)[0]
        self.assertEqual(item.kind, "平均数")
        self.assertEqual(item.answer, format_answer(mean(item.data)))

    def test_quiz_answers_not_empty(self) -> None:
        for item in make_quiz(10, 7):
            self.assertTrue(item.answer)

    def test_quiz_invalid_count_raises(self) -> None:
        with self.assertRaises(ValueError):
            make_quiz(0, 2026)
        with self.assertRaises(ValueError):
            make_quiz(101, 2026)

    def test_quiz_bool_count_raises(self) -> None:
        with self.assertRaises(TypeError):
            make_quiz(True, 2026)  # type: ignore[arg-type]

    def test_quiz_bool_seed_raises(self) -> None:
        with self.assertRaises(TypeError):
            make_quiz(3, True)  # type: ignore[arg-type]


class TestWorksheet(unittest.TestCase):
    def test_starts_with_doctype(self) -> None:
        page = generate_worksheet(10, 2026)
        self.assertTrue(page.startswith("<!DOCTYPE html>"))

    def test_contains_title_and_style(self) -> None:
        page = generate_worksheet(10, 2026)
        self.assertIn("<title>", page)
        self.assertIn("</title>", page)
        self.assertIn("<style>", page)

    def test_details_count_matches(self) -> None:
        page = generate_worksheet(10, 2026)
        self.assertEqual(page.count("<details>"), 10)

    def test_question_count_matches(self) -> None:
        page = generate_worksheet(7, 2026)
        self.assertIn("共 7 题", page)
        self.assertEqual(page.count("<li>"), 7)
        self.assertIn("<table", page)

    def test_worksheet_reproducible(self) -> None:
        self.assertEqual(generate_worksheet(10, 2026), generate_worksheet(10, 2026))

    def test_invalid_count_raises(self) -> None:
        with self.assertRaises(ValueError):
            generate_worksheet(0, 2026)


class TestCli(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)

    def _write(self, name: str, content: str) -> str:
        path = os.path.join(self.tempdir.name, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return path

    def test_help_exit_zero(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as context:
                cli.main(["--help"])
        self.assertEqual(context.exception.code, 0)
        output = stdout.getvalue()
        for command in ("describe", "quiz", "worksheet", "demo"):
            self.assertIn(command, output)

    def test_describe_data_success(self) -> None:
        code, output, error = run_cli(["describe", "--data", "85,90,78,92,88"])
        self.assertEqual(code, 0)
        self.assertEqual(error, "")
        self.assertIn("平均数：86.60", output)

    def test_describe_all_labels(self) -> None:
        code, output, _ = run_cli(["describe", "--data", "1,2,3"])
        self.assertEqual(code, 0)
        for label in (
            "个数",
            "总和",
            "平均数",
            "中位数",
            "众数",
            "极差",
            "总体方差",
            "总体标准差",
            "样本方差",
            "样本标准差",
        ):
            self.assertIn(label, output)

    def test_describe_file_success(self) -> None:
        path = self._write("scores.txt", "85, 90\n78 92\t88\n")
        code, output, _ = run_cli(["describe", "--file", path])
        self.assertEqual(code, 0)
        self.assertIn("平均数：86.60", output)
        self.assertIn("样本方差：29.80", output)

    def test_describe_single_value_dash(self) -> None:
        code, output, _ = run_cli(["describe", "--data", "7"])
        self.assertEqual(code, 0)
        self.assertIn("样本方差：—", output)
        self.assertIn("样本标准差：—", output)

    def test_describe_negative_data(self) -> None:
        code, output, _ = run_cli(["describe", "--data", "-3,-1,2"])
        self.assertEqual(code, 0)
        self.assertIn("平均数：-0.67", output)

    def test_describe_both_sources_error(self) -> None:
        code, _, error = run_cli(
            ["describe", "--data", "1,2", "--file", "scores.txt"]
        )
        self.assertEqual(code, 2)
        self.assertIn("不能同时使用", error)

    def test_describe_no_source_error(self) -> None:
        code, _, error = run_cli(["describe"])
        self.assertEqual(code, 2)
        self.assertIn("请通过", error)

    def test_describe_non_numeric_error(self) -> None:
        code, _, error = run_cli(["describe", "--data", "1,abc"])
        self.assertEqual(code, 2)
        self.assertIn("不是合法数字", error)

    def test_describe_nan_error(self) -> None:
        code, _, error = run_cli(["describe", "--data", "1,nan"])
        self.assertEqual(code, 2)
        self.assertIn("不是合法数字", error)

    def test_describe_missing_file_error(self) -> None:
        path = os.path.join(self.tempdir.name, "missing.txt")
        code, _, error = run_cli(["describe", "--file", path])
        self.assertEqual(code, 2)
        self.assertIn("文件不存在", error)

    def test_describe_directory_error(self) -> None:
        code, _, error = run_cli(["describe", "--file", self.tempdir.name])
        self.assertEqual(code, 2)
        self.assertIn("目录", error)

    def test_describe_permission_error(self) -> None:
        with mock.patch("builtins.open", side_effect=PermissionError("denied")):
            code, _, error = run_cli(["describe", "--file", "secret.txt"])
        self.assertEqual(code, 2)
        self.assertIn("权限", error)

    def test_describe_invalid_utf8_error(self) -> None:
        path = os.path.join(self.tempdir.name, "bad.txt")
        with open(path, "wb") as handle:
            handle.write(b"\xff\xfe\x80")
        code, _, error = run_cli(["describe", "--file", path])
        self.assertEqual(code, 2)
        self.assertIn("UTF-8", error)

    def test_quiz_success(self) -> None:
        code, output, _ = run_cli(["quiz", "--count", "5", "--seed", "2026"])
        self.assertEqual(code, 0)
        for kind in ("平均数", "中位数", "众数", "极差", "方差"):
            self.assertIn("（%s）" % kind, output)
        self.assertIn("答案：", output)

    def test_quiz_reproducible(self) -> None:
        first = run_cli(["quiz", "--count", "5", "--seed", "2026"])[1]
        second = run_cli(["quiz", "--count", "5", "--seed", "2026"])[1]
        self.assertEqual(first, second)

    def test_quiz_invalid_count_exits_two(self) -> None:
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as context:
                cli.main(["quiz", "--count", "0"])
        self.assertEqual(context.exception.code, 2)

    def test_worksheet_success(self) -> None:
        path = os.path.join(self.tempdir.name, "worksheet.html")
        code, output, _ = run_cli(
            ["worksheet", "--count", "10", "--seed", "2026", "--out", path]
        )
        self.assertEqual(code, 0)
        self.assertIn("已生成练习纸", output)
        with open(path, "r", encoding="utf-8") as handle:
            content = handle.read()
        self.assertTrue(content.startswith("<!DOCTYPE html>"))
        self.assertEqual(content.count("<details>"), 10)

    def test_worksheet_write_error(self) -> None:
        code, _, error = run_cli(
            ["worksheet", "--count", "3", "--out", self.tempdir.name]
        )
        self.assertEqual(code, 2)
        self.assertIn("写入文件失败", error)

    def test_demo_success(self) -> None:
        code, output, _ = run_cli(["demo"])
        self.assertEqual(code, 0)
        self.assertIn("示例数据：85, 90, 78, 92, 88", output)
        self.assertIn("答案：", output)

    def test_unknown_command_exits_two(self) -> None:
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as context:
                cli.main(["unknown"])
        self.assertEqual(context.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
