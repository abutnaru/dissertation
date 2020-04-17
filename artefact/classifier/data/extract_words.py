#!/usr/bin/env -S conda run -n dissertation python
import time
from tqdm import tqdm
import argparse
import urllib.parse as url
import csv
import re
import wordninja
import tldextract as tld
from collections import Counter


def get_URL_list():
    parser = argparse.ArgumentParser(description="Outputs word usage frequencies")
    parser.add_argument(
        "-f", "--file", type=str, dest="url_list", help="The URL list to be processed",
    )
    args = parser.parse_args()
    return args.url_list


def extract_words(string):
    x = re.compile(r"[A-Za-z]\w+")
    finds = x.findall(string)
    unwanted_chars = "_0123456789"
    unwanted_words = ["www"]
    results = []
    for word in finds:
        # For some reason the regex lets numerical characters and underscores slip
        cleaned_words = wordninja.split(
            "".join(c for c in word if c not in unwanted_chars)
        )
        results += [w for w in cleaned_words if len(w) > 3 and w not in unwanted_words]
    return results


def save_top(word_list, filename):
    c = Counter(word_list)
    with open(filename, "w") as outfile:
        for k, v in c.most_common():
            outfile.write(f"{k},{v}\n")


def run():
    url_file = get_URL_list()
    with open(url_file) as url_list:
        lines = [l for l in url_list]
        # delimiters = "0123456789-._~:/?#[]@!$&'()*+,;="
        subdomain_words, domain_words, path_words, query_words = [], [], [], []
        for row in tqdm(csv.reader(lines), total=len(lines)):
            netloc, path, params, query = url.urlparse(
                row[0].lower(), allow_fragments=False
            )[1:-1]
            subdomain_words += extract_words(tld.extract(netloc).subdomain)
            domain_words += extract_words(tld.extract(netloc).domain)
            path_words += extract_words(path)
            query_words += extract_words(params)
            query_words += extract_words(query)
        save_top(subdomain_words, f"sensitive_words/{url_file[:-4]}_subdomain.csv")
        save_top(domain_words, f"sensitive_words/{url_file[:-4]}_domain.csv")
        save_top(path_words, f"sensitive_words/{url_file[:-4]}_path.csv")
        save_top(query_words, f"sensitive_words/{url_file[:-4]}_query.csv")


if __name__ == "__main__":
    run()
