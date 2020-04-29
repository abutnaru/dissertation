#!/usr/bin/env -S conda run -n dissertation python
"""
Produces figures based on the data gathered from APWG reports.
"""
import csv

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import math


# APWG reports based figures
# APWG reports based figures
def plot_feature_correlation():
    df = pd.read_csv(
        "source/MIXED80k.csv",
        names=[
            "label",
            "f1",
            "f2",
            "f3",
            "f4",
            "f5",
            "f6",
            "f7",
            "f8",
            "f9",
            "f10",
            "f11",
            "f12",
            "f13",
        ],
    )

    g = sns.heatmap(
        df.corr(),
        vmax=0.45,
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.5},
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        linecolor="white",
    )
    sns.despine()
    g.figure.set_size_inches(12, 9)
    g.figure.savefig("Totrain.png")


def percentile(N, P):
    return N[int(round(P * len(N) + 0.5)) - 1]


def calc_stats_f(n):
    b_size, p_size = 0, 0
    b_series, p_series = [], []
    for row in csv.reader(open("source/final_train_dataset.csv")):
        if int(row[0]) == 0:
            b_series.append(int(row[n]))
            b_size += int(row[n])
        else:
            p_series.append(int(row[n]))
            p_size += int(row[n])
    b_series.sort()
    p_series.sort()
    print(
        f"Average benign URL size: \t\t{b_size/len(b_series)}\nAverage phishing URL size: \t\t{p_size/len(p_series)}"
    )
    print("----------------------------------------------------------")
    print(
        f"Median benign URL size: \t\t{percentile(b_series, 0.5)}\nMedian phishing URL size: \t\t{percentile(p_series, 0.5)}"
    )
    print("----------------------------------------------------------")
    print(
        f"90th percentile benign URL size: \t{percentile(b_series, 0.90)}\n90th percentile phishing URL size: \t{percentile(p_series, 0.90)}"
    )
    print("----------------------------------------------------------")
    print(
        f"95th percentile benign URL size: \t{percentile(b_series, 0.95)}\n95th percentile phishing URL size: \t{percentile(p_series, 0.95)}"
    )
    print("----------------------------------------------------------")
    print(
        f"99th percentile benign URL size: \t{percentile(b_series, 0.99)}\n99th percentile phishing URL size: \t{percentile(p_series, 0.99)}"
    )


calc_stats_f(10)
