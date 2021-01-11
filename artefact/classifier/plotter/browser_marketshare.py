#!/usr/bin/env python
"""
Produces figures based on the data gathered from APWG reports.
"""
import csv

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from numpy import median


sns.set()
plt.figure(figsize=(11, 5))
https_data = pd.read_csv(
    "source/browser_marketshare.csv", names=["Name", "Percentage"], skiprows=1
)

plotdata = pd.DataFrame(
    {
        "Browsers": [
            "Other",
            "Android",
            "IE",
            "Opera",
            "Edge",
            "UC",
            "Samsung",
            "Firefox",
            "Safari",
            "Chrome",
        ],
        "Percentage": [
            1.68,
            0.71,
            1.96,
            2.15,
            2.3,
            2.87,
            3.42,
            4.54,
            16.68,
            63.69,
        ],
    },
)

colors = ["#81AECB" for x in https_data]
plot = sns.barplot(
    x="Browsers",
    y="Percentage",
    data=plotdata,
    palette=colors,
)
locs, labels = plt.xticks()
plot.set_xticklabels(labels=labels)
for p in plot.patches:
    plot.annotate(
        "%.2f" % p.get_height(),
        (p.get_x() + p.get_width() / 2.0, p.get_height()),
        ha="center",
        va="center",
        fontsize=11,
        color="gray",
        xytext=(0, 20),
        textcoords="offset points",
    )
_ = plot.set_ylim(0, 100)  # To make space for the annotations
plot.figure.savefig("images/browser_marketshare.png")
