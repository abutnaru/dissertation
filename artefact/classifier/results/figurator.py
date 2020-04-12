import csv
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from numpy import median

df = pd.DataFrame(
	[['Precision', 0.225, 0.229, 0.234, 0.224,0.231],
	['Sensitivity', 0.800,0.978,0.980,0.929,1],
	['F-Measure', 0.351,0.372,0.378,0.361,0.376],
	['Accuracy', 0.314,0.234,0.252,0.239,0.231]],
	columns=['Metric', 'NB', 'DT', 'RF', 'SVM','MLP'])

print(df)

data = df.melt('Metric')

print(data)
plot = sns.catplot(y='value',x="variable",hue='Metric',data=data, palette="pastel", kind="bar")
plot.savefig("apwg_attack_hist.png")
