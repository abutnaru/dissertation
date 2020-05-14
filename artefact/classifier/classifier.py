#!/usr/bin/env -S conda run -n dissertation python
"""
The classifier delivers predictions on whether an URL is malicious or
benign. The prediction is based on the best performing machine learning
model trained throughout the experimentation phase of this project.
"""
import argparse
import csv
import pickle
import time

import numpy as np
import tldextract as tld

import features_extractor as features


def get_input():
    parser = argparse.ArgumentParser(description="URL classifier")
    parser.add_argument("--url", help="Input", type=str)
    args = parser.parse_args()
    return args.url


def is_whitelisted(url):
    f_in = open("data/processed_sets/benign_1M.csv")
    rows = [r for r in csv.reader(f_in)]
    f_in.close()
    for row in rows:
        if tld.extract(url).domain == tld.extract(row[0]).domain:
            return True
    return False


def deliver_classification(url):
    model = pickle.load(
        open("models/calibrated_random_forest/random_forest.sav", "rb")
    )
    return model.predict(features.extract(url).reshape(1, -1))[0]


def main():
    url = get_input()
    if is_whitelisted(url):
        print(f'The URL "{url}" is whitelisted')
    else:
        prediction = "PHISHING" if deliver_classification(url) else "BENIGN"
        print(f"The URL is classified as being {prediction}")


if __name__ == "__main__":
    print("Classification started...\n")
    start = time.perf_counter()
    main()
    finish = time.perf_counter()
    print(f"\nFinished in {round(finish-start,2)} seconds")
