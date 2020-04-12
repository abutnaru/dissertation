#!/usr/bin/env -S conda run -n dissertation python
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
    parser.add_argument("-d","--dataset", dest="dataset", help="Target dataset", type=str, required=True)
    parser.add_argument("-r","--records", dest="records", help="Number of records", type=str, required=True)
    parser.add_argument("-o","--output", dest="filename", help="Output destination", type=str, required=True)
    args = parser.parse_args()
    return (args.dataset, int(args.records), args.filename)


def run():
    target_dataset, target_records, outfile = get_input()
    reader = csv.reader(open("data/"+target_dataset+ ".csv", 'r'))
    writer = csv.writer(open(outfile + ".csv", "w"))
    malicious = 0
    benign = 0
    for row in reader:
        url, label = row[0], row[1]
        # Writing rows and keeping track of total
        # records written based on the label
        if label == "0" and benign <= (target_records / 2):
            f = features.extract(url, 0)
            writer.writerow(f)
            benign += 1
        if label == "1" and malicious <= (target_records / 2):
            f = features.extract(url, 1)
            writer.writerow(f)
            malicious += 1
        if (malicious + benign) % 1000 == 0:
            print("Records written: {}/{}".format(malicious + benign, target_records))


if __name__ == "__main__":
    run()
