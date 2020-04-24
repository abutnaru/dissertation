#!/usr/bin/env -S conda run -n dissertation python
"""
The classifier is the main and final interface with the artefact. It 
uses the model selected through evaluation and experimentation in the 
report.
"""
import argparse
import csv
import pickle

import numpy as np
import tldextract as tld

import features_extractor as features


def get_input():
    parser = argparse.ArgumentParser(description="URL classifier")
    parser.add_argument("--url", help="Input", type=str)
    args = parser.parse_args()
    return args.url


def is_whitelisted(url):
    d = tld.extract(url).domain
    f = open("data/benign1M.csv")
    reader = csv.reader(f)
    for row in reader:
        if d == tld.extract(row[0]).domain:
            return True
    return False


def classify(url):
    model = pickle.load(open("models/62k_mixed_pt/NNmodel.sav", "rb"))
    f = features.extract(url)
    prediction = model.predict(f.reshape(1, -1))
    return prediction[0]


def run():
    url = get_input()
    if is_whitelisted(url):
        print("URL is whitelisted")
    else:
        print("The ML prediction is: {}".format(classify(url)))


if __name__ == "__main__":
    run()
