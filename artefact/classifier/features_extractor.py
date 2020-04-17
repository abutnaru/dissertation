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
import urllib.parse as up


def hamming_distance(chaine1, chaine2):
    """
    Calculates hamming distance (for experimentation purposes)
    """
    return len(list(filter(lambda x: ord(x[0]) ^ ord(x[1]), zip(chaine1, chaine2))))


def max_hamming(url, N):
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
    subdomain, domain = tld.extract(url)[:2]
    with open("data/benign_1M.csv") as benign_list:
        reader = csv.reader(benign_list)
    min_dom_dist = 999
    min_sub_dist = 999
    index = 0
    for row in reader:
        index += 1
        if index == N:
            break
        b_domain = tld.extract(row[0]).domain
        levdd = levenshtein.eval(domain, b_domain)
        if levdd < min_dom_dist:
            min_dom_dist = levdd
        # Splitting the subdomain to cover cases
        # similar to https://example.amazon.domain.com/
        for component in subdomain.split("."):
            levsd = levenshtein.eval(component, b_domain)
            if levsd < min_sub_dist:
                min_sub_dist = levsd
    # Test based on the assumption that two strings with levenstain
    # distance greater than 10 can be regarded as different. Otherwise
    # the target URL's domain and subdomain are considered similar to
    # one of the top N domains
    min_dom_dist = 0 if min_dom_dist > 10 else 1
    min_sub_dist = 0 if min_sub_dist > 10 else 1

    return min_dom_dist, min_sub_dist


def extract(url, label=-1):
    """
    Decomposes passed URL into the selected list of features
    """
    parsed_url = up.urlparse(url)

    # Feature 1: URL size
    url_size = len(url)

    # Feature 3: Number of dots
    netloc_dot_count = parsed_url.netloc.count(".")
    path_dot_count = parsed_url.path.count(".") + parsed_url.query.count(".")

    # Feature 2: Number of '@', '-' and '~' characters
    at_count = url.count("@")
    hyphen_count = (
        parsed_url.netloc.count("-") if path_dot_count < 2 else url.count("-")
    )  # Popular in phishing domains
    tilde_count = url.count(
        "~"
    )  # Should not be used https://www.ietf.org/rfc/rfc2396.txt

    # Feature 2: Number of '@', '-' and '~' characters
    redirect_cues = ["url?", "redirect", "forward", "#btnI&q"]

    at_count = url.count("@")
    # Feature 4: Number of numerical characters
    digit_count = sum(c.isdigit() for c in parsed_url.netloc)

    # Feature 5: Sensitive vocabulary
    sensitive_vocabulary = [
        "signin",
        "login",
        "webscr",
        "ebayisapi",
        "secure",
        "banking",
        "account",
        "confirm",
    ]
    sens_word_count = 0
    for word in sensitive_vocabulary:
        if word in url:
            sens_word_count += 1

    # Feature 6: Presence of IP address in URL
    ip_presence = 1 if len(re.findall(r"[0-9]+(?:\.[0-9]+){3}", url)) != 0 else 0

    # Feature 7 and 8: Minimum distance between URL's domain and
    # subdomain and the top N benign domains
    dom_distance, subdom_distance = min_levenshtein(url, 2500)

    if label < 0:
        return np.array(
            [
                url_size,
                symbols_count,
                dot_count,
                digit_count,
                sens_word_count,
                ip_presence,
                subdom_distance,
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
                sens_word_count,
                ip_presence,
                subdom_distance,
                dom_distance,
            ]
        )
