#!/usr/bin/env python
"""
The data preparer takes as input a CSV file with rows specification of <url>,
<label> where label is 1 for phishing and 0 for benign. It processes each url
concurrently and outputs a CSV file with the features extracted.
"""
import argparse
import concurrent.futures
import csv
import re
import sys
import time

import tldextract as tld
from tqdm import tqdm

import features_extractor as features


def get_input():
    parser = argparse.ArgumentParser(
        description="Decomposes input URLs into features for model training",
    )
    parser.add_argument(
        "-d",
        "--dataset",
        dest="dataset",
        help="Target dataset",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-r",
        "--records",
        dest="records",
        help="Number of records (benign + malicious)",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="filename",
        help="Output destination",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-m",
        dest="mixed_flag",
        help="Toggle mixed urls in target dataset",
        action="store_true",
    )
    args = parser.parse_args()
    return (args.dataset, int(args.records), args.mixed_flag, args.filename)


def main():
    target_dataset, target_records, mixed_flag, out_filename = get_input()
    record_limit = int(target_records / 2 if mixed_flag else target_records)

    infile = open("data/processed_sets/" + target_dataset + ".csv", "r")
    outfile = open(f"features/{out_filename}.csv", "w")
    writer = csv.writer(outfile)

    malicious = 0
    benign = 0
    results = []
    with tqdm(total=int(target_records), file=sys.stdout) as progressbar:
        with concurrent.futures.ProcessPoolExecutor() as e:
            for row in csv.reader(infile):
                # Writing rows and keeping track of total
                # records written based on the label
                if row[1] == "0" and benign < record_limit:
                    benign += 1
                    results.append(e.submit(features.extract, row[0], 0))
                if row[1] == "1" and malicious < record_limit:
                    malicious += 1
                    results.append(e.submit(features.extract, row[0], 1))
            for f in concurrent.futures.as_completed(results):
                writer.writerow(f.result())
                progressbar.update()
    infile.close()
    outfile.close()


if __name__ == "__main__":
    print("Data preparation started...\n")
    start = time.perf_counter()
    main()
    finish = time.perf_counter()
    print(f"\nFinished in {round(finish-start,2)} seconds")
