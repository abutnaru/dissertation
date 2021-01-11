#!/usr/bin/env python
"""
Processes the target phishtank JSON dataset eliminating every attribute except
the url and its classification.
"""
import argparse
import csv
import json
import sys
import time

from tqdm import tqdm


print("Data preparation started...\n")
start = time.perf_counter()

parser = argparse.ArgumentParser(description="Phishtank data preprocessor")
parser.add_argument(
    "-d",
    "--dataset",
    dest="dataset",
    type=str,
    help="Target phishtank dataset",
    required=True,
)
dataset_filename = parser.parse_args().dataset
fin = open(f"unprocessed/{dataset_filename}.json", "r")
phish_lines = [l for l in json.load(fin)]
fin.close()

date = "".join([c if c.isdigit() == True else "" for c in dataset_filename])
fout = open(f"phishtank_{date}_processed.csv", "w")
writer = csv.writer(fout)

with tqdm(total=len(phish_lines), file=sys.stdout) as progressbar:
    for phish in phish_lines:
        writer.writerow([phish["url"], 1])
        progressbar.update()

fout.close()

finish = time.perf_counter()
print(f"\nFinished in {round(finish-start,2)} seconds")
