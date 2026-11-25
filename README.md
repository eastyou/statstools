# statstools
[![CI](https://github.com/eastyou/statstools/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/statstools/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](pyproject.toml)

纯标准库实现的初中数学统计量计算与练习纸生成工具，命令行即可完成计算、出题与打印练习纸。

## 项目简介

statstools 面向初中数学课堂与课后练习，把一组数据的个数、总和、平均数、中位数、众数、极差、总体方差、总体标准差、样本方差和样本标准差一次算清，并明确区分总体方差（除以 n）与样本方差（除以 n-1）。

所有功能只依赖 Python 标准库，安装体积小、运行速度快；数据既可以在命令行用 `--data` 直接给出，也可以从逗号、空格或换行分隔的文本文件中读取。题库与练习纸使用固定随机种子即可复现，方便教师批量准备同一套题目。

## 特性

- 纯标准库实现，无第三方依赖，兼容 Python 3.9 及以上
- 一次输出个数、总和、平均数、中位数、众数、极差、总体方差、总体标准差、样本方差、样本标准差
- 支持逗号、空格、制表符、换行混合分隔，支持 `--data` 与 `--file` 两种数据来源
- 平均数、中位数、众数、极差、方差五类题型随机生成，相同种子结果完全可复现
- 生成包含数据表格、`<details>` 折叠答案的 HTML 练习纸，可直接打印
- 完整类型注解与输入校验，非法数据与文件错误均给出中文提示，退出码规范

## 安装

需要 Python 3.9 或更高版本，无需安装任何第三方依赖。

```bash
pip install -e .
```

也可以不安装，直接在项目目录中运行：

```bash
python -m statstools --help
```

## 使用

### describe

计算一组数据的全部统计量。`--data` 与 `--file` 必须且只能提供一个。

```bash
statstools describe --data "85,90,78,92,88"
```

```text
个数：5
总和：433.00
平均数：86.60
中位数：88.00
众数：无
极差：14.00
总体方差：23.84
总体标准差：4.88
样本方差：29.80
样本标准差：5.46
```

从文件读取时写法为 `statstools describe --file scores.txt`，文件中的逗号、空格、制表符与换行都可以作为分隔符。方差说明：总体方差除以 n，样本方差除以 n-1；只有 1 个数据时样本方差与样本标准差无法计算，输出 `—`。

### quiz

随机生成五类练习题，题目在前，答案集中列在末尾。相同 `--seed` 输出完全一致。

```bash
statstools quiz --count 5 --seed 2026
```

```text
第 1 题（平均数）
已知一组数据：10，12，15，3，5。求这组数据的平均数。

第 2 题（中位数）
已知一组数据：12，8，5，14，6，6，9，18。求这组数据的中位数。

第 3 题（众数）
已知一组数据：10，8，10，7，6。求这组数据的众数。

第 4 题（极差）
已知一组数据：7，8，10，12，3，7，3，10。求这组数据的极差。

第 5 题（方差）
已知一组数据：4，12，13，13，11，6，2。求这组数据的方差。

答案：
1. 9
2. 8.5
3. 10
4. 9
5. 18.2
```

### worksheet

生成 HTML 练习纸，每题带数据表格，答案放在 `<details>` 中折叠。

```bash
statstools worksheet --count 10 --seed 2026 --out worksheet.html
```

```text
已生成练习纸：worksheet.html（共 10 题）
```

生成的 `worksheet.html` 以 `<!DOCTYPE html>` 开头，包含 `<title>` 与 `<style>`，浏览器打开后展开“查看答案”即可核对。

### demo

输出一组样例数据的统计量与三道示例题，用于快速体验。

```bash
statstools demo
```

```text
示例数据：85, 90, 78, 92, 88
个数：5
总和：433.00
平均数：86.60
中位数：88.00
众数：无
极差：14.00
总体方差：23.84
总体标准差：4.88
样本方差：29.80
样本标准差：5.46

示例题目：
第 1 题（平均数）已知一组数据：10，12，15，3，5。求这组数据的平均数。
第 2 题（中位数）已知一组数据：12，8，5，14，6，6，9，18。求这组数据的中位数。
第 3 题（众数）已知一组数据：10，8，10，7，6。求这组数据的众数。

答案：1. 9；2. 8.5；3. 10
```

### 参数

| 子命令 | 参数 | 说明 |
| --- | --- | --- |
| `describe` | `--data DATA` | 逗号、空格或换行分隔的数据，例如 `"85,90,78,92,88"` |
| `describe` | `--file FILE` | 从 UTF-8 文本文件读取数据，分隔符可为逗号、空白或换行 |
| `quiz` | `--count N` | 题目数量，1 到 100，默认 5 |
| `quiz` | `--seed SEED` | 随机种子，相同种子结果可复现 |
| `worksheet` | `--count N` | 题目数量，1 到 100，默认 10 |
| `worksheet` | `--seed SEED` | 随机种子，相同种子结果可复现 |
| `worksheet` | `--out PATH` | 输出 HTML 文件路径，必填 |
| `demo` | 无 | 直接输出样例统计量与三道示例题 |

### 退出码

| 退出码 | 含义 |
| --- | --- |
| 0 | 命令执行成功 |
| 2 | 参数或数据错误，包括非数字、NaN、数据为空、`--data` 与 `--file` 同时使用、文件读取或写入失败等 |

## 作为库使用

```python
from statstools import make_quiz, summarize

summary = summarize([2, 4, 4, 4, 5, 5, 7, 9])
print(summary.mean, summary.median, summary.modes)
# 5.0 4.5 (4.0,)
print(summary.population_variance, summary.sample_variance)
# 4.0 4.571428571428571
print(round(summary.sample_stdev, 4))
# 2.1381

item = make_quiz(1, 2026)[0]
print(item.question)
# 已知一组数据：10，12，15，3，5。求这组数据的平均数。
print(item.answer)
# 9
```

## 开发与测试

项目共 88 个单元测试用例，覆盖统计量计算、输入校验、题库复现、练习纸生成与命令行退出码。

```bash
python -m unittest discover -s tests -v
```

CI 在 Ubuntu 上使用 Python 3.9、3.10、3.11、3.12、3.13 运行测试，并执行 `python -m statstools --help` 做命令行冒烟检查。

## License

[MIT](LICENSE) © 2026 eastyou
