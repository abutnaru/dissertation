#!/usr/bin/env conda run -n dissertation python
"""
The data preparer extracts a selected number of benign and malicious
URLs from the minxed450k.csv file and extrats their features
"""
import tldextract as tld
import csv, re
import argparse
import features_extractor as features


def get_input():
    parser = argparse.ArgumentParser(description="Data preparator for model training")
    parser.add_argument("--dataset", dest="dataset", help="Target dataset", type=str)
    parser.add_argument("--records", dest="records", help="Number of records", type=str)
    parser.add_argument("--out", dest="filename", help="Output destination", type=str)
    args = parser.parse_args()
    return (args.dataset, args.records, args.filename)


def run():
    target_dataset, target_records, outfile = get_input()
    reader = csv.reader(target_dataset)
    features_file = open(outfile + ".csv", "w")
    writer = csv.writer(features_file)
    malicious = 0
    benign = 0
    for row in reader:
        url, label = row[0], row[1]
        # Writing rows and keeping track of total
        # records written based on the label
        if label == "0" and benign <= (target_records / 2):
            f = features.extract(url, label)
            writer.writerow(f)
            benign += 1
        if label == "1" and malicious <= (target_records / 2):
            f = features.extract(url, label)
            writer.writerow(f)
            malicious += 1
        if (malicious + benign) % 1000 == 0:
            print("Records written: {}/{}".format(malicious + benign, target_records))


if __name__ == "__main__":
    run()
