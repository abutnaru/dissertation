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

fin = open("processed_sets/mixed_450k.csv", "r")
rows = [l for l in csv.reader(fin)]
fin.close()

fout1 = open("processed_sets/mixed_dataset_phishing.csv", "w")
fout2 = open("processed_sets/mixed_dataset_benign.csv", "w")
phishes_file = csv.writer(fout1)
benign_file = csv.writer(fout2)

with tqdm(total=len(rows), file=sys.stdout) as progressbar:
    for row in rows:
        if row[1] == "0":
            benign_file.writerow(row)
        else:
            phishes_file.writerow(row)
        progressbar.update()

fout1.close()
fout2.close()
finish = time.perf_counter()
print(f"\nSeparation finished in {round(finish-start,2)} seconds")
