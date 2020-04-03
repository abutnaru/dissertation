import csv
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from numpy import median


# APWG reports based figures
apwg_data = pd.read_csv('apwg.csv', names=['Year', 'Month','Websites', 'Emails', 'Target Brands'], skiprows=1)
plot = sns.lineplot(x="Year", y="Emails", data=apwg_data,label="Emails", palette="pastel")
plot = sns.lineplot(x="Year", y="Websites", data=apwg_data, label="Websites", palette="pastel")
plot.legend()
plot.figure.savefig("images/apwg_attack_hist.png")

plot.get_figure().clf()
plot = sns.lineplot(x="Year", y="Target Brands", data=apwg_data, palette="pastel")
plot.figure.savefig("images/apwg_brands_hist.png")

plot.get_figure().clf()
https_data = pd.read_csv('https_usage.csv', names=['Quarter','Percentage'], skiprows=1)
colors = ['#1F77B4' for x in https_data ]
plot = sns.barplot(x="Quarter", y="Percentage", data=https_data,label="Emails", palette=colors)
locs, labels = plt.xticks()
plot.set_xticklabels(labels=labels,rotation=-30)
plot.figure.savefig("images/https_usage.png")

# Features based figures
plot.get_figure().clf()
benign_data = pd.read_csv('benign.csv', names=['Size','Hyphens', 'Dots', 'Digits', 'IP', 'Hamming'])
plot = sns.distplot(benign_data["Hyphens"], hist=True, kde=False)
plot.figure.savefig("images/size_benign.png")

# Features based figures
plot.get_figure().clf()
malicious_data = pd.read_csv('features.csv', names=['Label','Size','Hyphens', 'Dots', 'Digits', 'IP', 'Hamming'])
plot = sns.scatterplot(y="Size", x="Hamming", hue="Label",data=malicious_data)
plot.figure.savefig("images/size_phishing.png")