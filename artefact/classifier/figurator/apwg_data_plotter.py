#!/usr/bin/env -S conda run -n dissertation python
"""
Produces figures based on the data gathered from APWG reports.
"""
import csv

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from numpy import median


# APWG reports based figures
apwg_data = pd.read_csv(
    "apwg.csv",
    names=["Year", "Month", "Websites", "Emails", "Target Brands"],
    skiprows=1,
)
plot = sns.lineplot(
    x="Year", y="Emails", data=apwg_data, label="Emails", palette="pastel"
)
plot = sns.lineplot(
    x="Year", y="Websites", data=apwg_data, label="Websites", palette="pastel"
)
plot.legend()
plot.figure.savefig("images/apwg_attack_hist.png")

plot.get_figure().clf()
plot = sns.lineplot(
    x="Year", y="Target Brands", data=apwg_data, palette="pastel"
)
plot.figure.savefig("images/apwg_brands_hist.png")

plot.get_figure().clf()
https_data = pd.read_csv(
    "https_usage.csv", names=["Quarter", "Percentage"], skiprows=1
)
colors = ["#1F77B4" for x in https_data]
plot = sns.barplot(
    x="Quarter",
    y="Percentage",
    data=https_data,
    label="Emails",
    palette=colors,
)
locs, labels = plt.xticks()
plot.set_xticklabels(labels=labels, rotation=-30)
plot.figure.savefig("images/https_usage.png")
