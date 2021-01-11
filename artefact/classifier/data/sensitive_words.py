#!/usr/bin/env python
"""
Calculates the frequencies of words used in the target URL set. The search is
performed on all the areas of the URL using the URL format of
<subdomain>.<domain>/<path>?<query>.
"""
import argparse
import csv
import re
import time
import urllib.parse as url
from collections import Counter

import tldextract as tld
import wordninja
from tqdm import tqdm


def get_argument():
    parser = argparse.ArgumentParser(
        description="Outputs word usage frequencies in all areas of the URL"
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        dest="filename",
        help="URL list to be processed",
        required=True,
    )
    return parser.parse_args()


def extract_words(string):
    """
    Takes as input a string and returns all the words found in it by
    probabilistically splitting concatenated words using NLP based on English
    Wikipedia unigram frequencies. 
    """
    x = re.compile(r"[A-Za-z]\w+")
    finds = x.findall(string)
    chars_filter = "_0123456789"
    words_filter = ["www"]
    for word in finds:
        # Filtering out the numerical characters and underscores
        fw = wordninja.split("".join(c for c in word if c not in chars_filter))

    # Returning only words longer than three characters to avoid noise
    return [w for w in fw if len(w) > 3 and w not in words_filter]


def save_frequencies(word_list, filename):
    """
    Counts and saves word frequencies
    """
    c = Counter(word_list)
    with open(f"sensitive_words/{filename}", "w") as outfile:
        for k, v in c.most_common():
            outfile.write(f"{k},{v}\n")


def main():
    fin = open(get_argument().filename)
    lines = [l for l in fin]
    fin.close()

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

    save_frequencies(subdomain_words, f"{fin[:-4]}_subdomain.csv")
    save_frequencies(domain_words, f"{fin[:-4]}_domain.csv")
    save_frequencies(path_words, f"{fin[:-4]}_path.csv")
    save_frequencies(query_words, f"{fin[:-4]}_query.csv")


if __name__ == "__main__":
    print("Word frequency calculation started...\n")
    start = time.perf_counter()
    main()
    finish = time.perf_counter()
    print(
        f"\nFinished in {round(finish-start,2)} seconds \n\
            Files saved in the sensitive_words folder"
    )
