import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
import os
import re
from scipy.stats import gmean
from pprint import pprint

decimal_with_parenthesis = r"([0-9\.\,]+) \([^)]*\)"
regex_dict = {
    "name": r"(\w+\[[^\]]*])",
    "min": decimal_with_parenthesis,
    "max": decimal_with_parenthesis,
    "mean": decimal_with_parenthesis,
    "stddev": decimal_with_parenthesis,
    "median": decimal_with_parenthesis,
    "iqr": None,
    "outliers": None,
    "ops": None,
    "rounds": None,
    "iterations": None,
    "spaces": r"\s+"
}


def to_float(string):
    return float(string.replace(",", ""))


def decode_name(name):
    operands = re.search(r"(binary|unary)", name).group(1)
    op = re.search(r"\[([a-z_A-Z]+)-", name).group(1)
    dtype = re.search(r"(dtype[0-9]+)", name).group(1)
    size = re.search(r"-([0-9]+)", name).group(1)
    engine = "open3d" if re.search(r"numpy", name) is None else "numpy"
    return operands, op, dtype, size, engine


if __name__ == "__main__":

    with open("benchmark_results.log", "r") as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
        spaces = r"\s+"
        line_regex = "".join([
            regex_dict["name"],
            spaces,
            regex_dict["min"],
            spaces,
            regex_dict["max"],
            spaces,
            regex_dict["mean"],
            spaces,
            regex_dict["stddev"],
            spaces,
            regex_dict["median"],
        ])
        entries = []
        for line in lines:
            match = re.search(line_regex, line)
            if match:
                entry = dict()
                entry["name"] = match.group(1).strip()
                entry["operands"], entry["op"], entry["dtype"], entry[
                    "size"], entry["engine"] = decode_name(entry["name"])
                entry["min"] = to_float(match.group(2).strip())
                entry["max"] = to_float(match.group(3).strip())
                entry["mean"] = to_float(match.group(4).strip())
                entry["stddev"] = to_float(match.group(5).strip())
                entry["median"] = to_float(match.group(6).strip())
                entries.append(entry)
        print(f"len(entries): {len(entries)}")

    # Compute geometirc mean
    all_times = dict()
    for operands in ["binary", "unary"]:
        ops = [
            entry["op"] for entry in entries if entry["operands"] == operands
        ]
        ops = sorted(list(set(ops)))

        all_times[operands] = dict()
        for binary_op in ops:
            open3d_times = [
                entry["mean"]
                for entry in entries
                if entry["op"] == binary_op and entry["engine"] == "open3d"
            ]
            numpy_times = [
                entry["mean"]
                for entry in entries
                if entry["op"] == binary_op and entry["engine"] == "numpy"
            ]
            all_times[operands][binary_op] = dict()
            all_times[operands][binary_op]["open3d"] = gmean(open3d_times)
            all_times[operands][binary_op]["numpy"] = gmean(numpy_times)

    pprint(all_times)

    # Plot