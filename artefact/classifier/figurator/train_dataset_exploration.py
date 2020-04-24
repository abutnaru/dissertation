#!/usr/bin/env -S conda run -n dissertation python
"""
Produces figures based on training dataset exploration.
"""
import csv

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Features based figures
benign_data = pd.read_csv('benign.csv', names=['Size','Hyphens', 'Dots', 'Digits', 'IP', 'Hamming'])
plot = sns.distplot(benign_data["Hyphens"], hist=True, kde=False)
plot.figure.savefig("images/size_benign.png")

# Features based figures
plot.get_figure().clf()
malicious_data = pd.read_csv('features.csv', names=['Label','Size','Hyphens', 'Dots', 'Digits', 'IP', 'Hamming'])
plot = sns.scatterplot(y="Size", x="Hamming", hue="Label",data=malicious_data)
plot.figure.savefig("images/size_phishing.png")
