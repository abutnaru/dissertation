#!/usr/bin/env python
"""
Separates the benign and malicious URLs from the mixed source set.
"""
import csv
import sys
import time

from tqdm import tqdm


print("Initiating the splitting of mixed450k.csv\n")
start = time.perf_counter()

f_in = open("source/final_train_dataset.csv", "r")
rows = [l for l in csv.reader(f_in)]
f_in.close()

f_out1 = open("source/features_phishing.csv", "w")
f_out2 = open("source/features_benign.csv", "w")
phishes_file = csv.writer(f_out1)
benign_file = csv.writer(f_out2)

with tqdm(total=len(rows), file=sys.stdout) as progressbar:
    for row in rows:
        if row[0] == "1":
            phishes_file.writerow(row)
        else:
            benign_file.writerow(row)
        progressbar.update()

f_out1.close()
f_out2.close()
finish = time.perf_counter()
print(f"\nSeparation finished in {round(finish-start,2)} seconds")
