#!/usr/bin/env -S conda run -n dissertation python
"""
Produces figures based on the data gathered from APWG reports.
"""
import csv

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from numpy import median

sns.set()
# APWG reports based figures
plt.figure(figsize=(6.8,4.5))
apwg_data = pd.read_csv(
    "source/apwg.csv",
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
plt.figure(figsize=(11, 5))
https_data = pd.read_csv(
    "source/apwg_https_usage.csv", names=["Quarter", "Percentage"], skiprows=1
)
colors = ["#81AECB" for x in https_data]
plot = sns.barplot(
    x="Quarter",
    y="Percentage",
    data=https_data,
    label="Emails",
    palette=colors,
)
locs, labels = plt.xticks()
plot.set_xticklabels(labels=labels, rotation=-30)
for p in plot.patches:
    plot.annotate("%.0f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),ha='center', va='center', fontsize=11, color='gray', xytext=(0, 15),textcoords='offset points')
_ = plot.set_ylim(0,100) #To make space for the annotations
plot.figure.savefig("images/apwg_https_usage.png")
