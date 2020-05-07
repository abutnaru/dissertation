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
        "source/1_final_train_nolongsub_noip.csv",
        names=[
            "Label",
            "F1",
            "F2",
            "F3",
            "F4",
            "F5",
            "F6",
            "F7",
            "F8",
            "F9",
            "F10",
            "F11",
        ],
    )
    grid_kws = {"height_ratios": (.9, .05), "hspace": .2}
    f, (ax, cbar_ax) = plt.subplots(2, gridspec_kw=grid_kws)
    g = sns.heatmap(
        df.corr(),
        ax=ax,
        vmax=0.40,
        center=0,
        cbar_ax=cbar_ax,
        cbar_kws={"shrink": 0.5, "orientation": "horizontal"},
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
    )
    sns.despine()
    g.figure.set_size_inches(12, 9)
    g.figure.savefig("correl.png")


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


plot_feature_correlation()