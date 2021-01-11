#!/usr/bin/env python
"""
Processes the source dataset eliminating every row item except the url and its
classification.
"""
import csv
import sys
import time

from tqdm import tqdm


print("Initiating the parsing of mixed450k_raw.csv\n")
start = time.perf_counter()

fin = open("unprocessed/mixed450k_raw.csv", "r")
lines = [l for l in csv.reader(fin)]
fin.close()
fout = open("processed/mixed450k_processed.csv", "w")
writer = csv.writer(fout)

with tqdm(total=len(lines), file=sys.stdout) as progressbar:
    for row in lines:
        label = 0
        # Iterating through row items to check if item is malicious or benign
        # due to the bad formatting of the source file
        for item in row:
            if item == "malicious":
                label = 1
        writer.writerow([row[1], label])
        progressbar.update()

fout.close()

finish = time.perf_counter()
print(f"\nParsing finished in {round(finish-start,2)} seconds")
