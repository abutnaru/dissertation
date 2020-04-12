"""
The features extractor decomposes each URL in the set
of selected features and saves the records in a CSV file
"""
import tldextract as tld
import re
import csv
import numpy as np
import subprocess
import editdistance as levenshtein


def hamming_distance(chaine1, chaine2):
    """
    Calculates hamming distance (for experimentation purposes)
    """
    return len(list(filter(lambda x: ord(x[0]) ^ ord(x[1]), zip(chaine1, chaine2))))

def min_hamming(url, N):
    """
    Calculates the minimum value for the hamming distance
    between the top N domains and the URL's domain
    """
    components = tld.extract(url)
    domain = components.domain

    f = open("data/benign_1M.csv")
    reader = csv.reader(f)
    min_distance = 9999
    index = 0

    for row in reader:
        index += 1
        if index == N:
            break
        record = tld.extract(row[0])
        levdd = levenshtein.eval(domain, record.domain)
        if levdd < min_distance:
            min_distance = levdd
    return min_distance


def min_levenshtein(url, N):
    """
    Calculates the minimum value for the levenshtein distance
    between the top N domains and the URL's domain and subdomain
    """
    components = tld.extract(url)
    subdomain = components.subdomain
    domain = components.domain

    f = open("data/benign_1M.csv")
    reader = csv.reader(f)
    min_distance = 9999
    min_sub_distance = 9999
    index = 0

    for row in reader:
        index += 1
        if index == N:
            break
        record = tld.extract(row[0])
        levdd = levenshtein.eval(domain, record.domain)
        if levdd < min_distance:
            min_distance = levdd
        # Splitting the subdomain to cover cases
        # similar to https://example.amazon.domain.com/
        for component in subdomain.split("."):
            levsd = levenshtein.eval(component, record.domain)
            if levsd < min_sub_distance:
                min_sub_distance = levsd
    # Test based on the assumption that two strings with levenstain
    # distance greater than 10 can be regarded as different. Otherwise
    # the target URL's domain and subdomain are considered similar to
    # one of the top N domains
    if min_distance > 10:
        min_distance = 0
    else:
        min_distance = 1
    if min_sub_distance > 10:
        min_sub_distance = 0
    else:
        min_sub_distance = 1

    return min_distance, min_sub_distance


def extract(url, label=-1):
    """
    Decomposes passed URL into the selected list of features
    """
    # Feature 1: URL size
    url_size = len(url)

    # Feature 2: Number of '@', '-' and '~' characters
    symbols_count = url.count("-") #+ url.count("@") + url.count("~")

    # Feature 3: Number of dots
    dot_count = url.count(".")

    # Feature 4: Number of numerical characters
    digit_count = sum(c.isdigit() for c in tld.extract(url).subdomain+tld.extract(url).domain)

    # Feature 5: Usage of HTTPS
    #proto = url.split(":")[0]
    #if proto == "https":
    #    proto = 1
    #else:
    #    proto = 0

    # Feature 6: Sensitive vocabulary
    #sensitive_vocabulary = [
    #    "signin",
    #    "login",
    #    "webscr",
    #    "ebayisapi",
    #    "secure",
    #    "banking",
    #    "account",
    #    "confirm",
    #]
    #sens_word_count = 0
    #for word in sensitive_vocabulary:
    #    if word in url:
    #        sens_word_count += 1

    # Feature 7: Presence of IP address in URL
    ip_presence = 0
    if len(re.findall(r"[0-9]+(?:\.[0-9]+){3}", url)) != 0:
        ip_presence = 1

    # Feature 8 and 9: Minimum distance between URL's domain and
    # subdomain and the top N benign domains
    dom_distance = min_hamming(url, 1000) # , subdom_distance

    if label < 0:
        return np.array(
            [
                url_size,
                symbols_count,
                dot_count,
                digit_count,
                #proto,
                #sens_word_count,
                ip_presence,
                #subdom_distance,
                dom_distance,
            ]
        )
    else:
        return np.array(
            [
                label,
                url_size,
                symbols_count,
                dot_count,
                digit_count,
                #proto,
                #sens_word_count,
                ip_presence,
                #subdom_distance,
                dom_distance,
            ]
        )
