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


def min_hamming(url, N):
    """
    Calculates the minimum value for the hamming distance
    between the top N domains and the URL's domain
    """
    subdomain, domain = tld.extract(url)[:2]
    # with open("data/benign_1M.csv") as benign_list:
    #     reader = csv.reader(benign_list)
    reader = csv.reader(open("data/benign_1M.csv"))
    min_dom_dist = 999
    min_sub_dist = 999
    index = 0
    for row in reader:
        index += 1
        if index == N:
            break
        b_domain = tld.extract(row[0]).domain
        hamdd = hamming_distance(domain, b_domain)
        if hamdd < min_dom_dist:
            min_dom_dist = hamdd
        # Splitting the subdomain to cover cases
        # similar to https://example-verification.amazon.domain.com/
        for component in subdomain.split("."):
            if "-" in component:
                for subcomp in component.split("-"):
                    hamsd = hamming_distance(subcomp, b_domain)
                    if hamsd < min_sub_dist:
                        min_sub_dist = hamsd
            else:
                hamsd = hamming_distance(component, b_domain)
                if hamsd < min_sub_dist:
                    min_sub_dist = hamsd
    # Test based on the assumption that two strings with levenstain
    # distance greater than 10 can be regarded as different. Otherwise
    # the target URL's domain and subdomain are considered similar to
    # one of the top N domains

    return 0 if min_dom_dist >= 3 else 1, 0 if min_sub_dist <= 5 else 1


def min_levenshtein(url, N):
    """
    Calculates the minimum value for the levenshtein distance
    between the top N domains and the URL's domain and subdomain
    """
    subdomain, domain = tld.extract(url)[:2]
    # with open("data/benign_1M.csv") as benign_list:
    #     reader = csv.reader(benign_list)
    reader = csv.reader(open("data/benign_1M.csv"))
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
            if "-" in component:
                for subcomp in component.split("-"):
                    levsd = hamming_distance(subcomp, b_domain)
                    if levsd < min_sub_dist:
                        min_sub_dist = levsd
            else:
                levsd = hamming_distance(component, b_domain)
                if levsd < min_sub_dist:
                    min_sub_dist = levsd
    # Test based on the assumption that two strings with levenstain
    # distance greater than 10 can be regarded as different. Otherwise
    # the target URL's domain and subdomain are considered similar to
    # one of the top N domains
    dom_dist = 1 if min_dom_dist <= 5 and min_dom_dist != 0 else 0
    sub_dist = (
        1
        if min_sub_dist <= 5
        and "www" not in subdomain
        and len(subdomain.split(".")) == 1
        else 0
    )

    return dom_dist, sub_dist


def get_occurences(words, target):
    for word in words:
        if word in target:
            return 1
    return 0

def has_domain(target_path, N):
    with open("data/benign_1M.csv") as benign_list:
        index = 0
        reader = csv.reader(benign_list)
        for row in reader:
            index +=1
            if len(row[0]) >=5 and row[0] in target_path:
                return 1
            if index == N:
                break
        return 0

def extract(url, label=-1):
    """
    Decomposes passed URL into the selected list of features
    """
    parsed_url = up.urlparse(url)

    # Feature 1: URL size
    url_size = len(url)

    proto = 0 if url.split(":")[0] == "https" else 1

    # Feature 3: Number of dots
    #netloc_dot_count = parsed_url.netloc.count(".")
    path_dot_count = parsed_url.path.count(".") + parsed_url.query.count(".")

    # Feature 2: Number of '@', '-' and '~' characters
    symbols_count = url.count("@") + url.count("~")
    domain_in_path = 0 if path_dot_count < 2 else 1
    hyphen_count = (
        parsed_url.netloc.count("-") if path_dot_count < 2 else url.count("-")
    )  # Popular in phishing domains
    # tilde_count = url.count("~")  # Should not be used https://www.ietf.org/rfc/rfc2396.txt

    # Feature 2: Number of '@', '-' and '~' characters
    #redirect = 0
    #redirect_cues = ["url", "redirect", "forward", "#btnI&q"]
    #for cue in redirect_cues:
    #    if cue in parsed_url.path:
    #        redirect = 1
    # Feature 4: Number of numerical characters
    digit_count = sum(c.isdigit() for c in parsed_url.netloc)

    # Feature 4: Size of the subdomain
    subdomain_components = (
        tld.extract(url).subdomain.count(".")
        + tld.extract(url).subdomain.count("-")
        + 1
    )
    long_subdomain = 1 if subdomain_components >= 3 else 0

    # Feature 5: Sensitive vocabulary
    sensitive_subdomains = [
        "paypal",
        "sites",
        "secure",
        "login",
        "runescape"
        "account",
        "service"
        "sign",
        "bank",
        "transfer",
        "user",
        "security",
    ]
    sensitive_domains = [
        "000webhost",  #  you can set up own domain on 000webhost
        "sharepoint",  # not recommended https://support.office.com/en-us/article/SharePoint-Online-Public-Websites-to-be-discontinued-e86bfd2f-5c7d-446f-a430-7cfcc0130916
        "customer"
        "service",
        "secure",
        "support",
    ]

    sensitive_paths = [
        "admin",
        "login",
        "account",
        "sign",
        "secure",
        "verification",
        "transfer",
        "validation",
        "bank",
        "verify",
    ]
    subdomain_occs = get_occurences(sensitive_subdomains, tld.extract(url).subdomain)
    domain_occs = get_occurences(sensitive_domains, tld.extract(url).domain)
    path_occs = get_occurences(sensitive_paths, parsed_url.path)
    if path_occs == 0:
        path_occs = 1 if has_domain(parsed_url.path,2500) or has_domain(parsed_url.query,2500) else 0
        
    # Feature 6: Presence of IP address in URL
    ip_presence = 1 if len(re.findall(r"[0-9]+(?:\.[0-9]+){3}", url)) != 0 else 0

    # Feature 7 and 8: Minimum distance between URL's domain and
    # subdomain and the top N benign domains
    dom_distance, subdom_distance = min_levenshtein(url, 25_000)

    if label < 0:
        return np.array(
            [
                url_size,
                proto,
                digit_count,
                symbols_count,
                domain_in_path,
                hyphen_count,
                long_subdomain,
                subdomain_occs,
                domain_occs,
                path_occs,
                ip_presence,
                dom_distance,
                subdom_distance,
            ]
        )
    else:
        return np.array(
            [
                label,
                url_size,
                proto,
                digit_count,
                symbols_count,
                domain_in_path,
                hyphen_count,
                long_subdomain,
                subdomain_occs,
                domain_occs,
                path_occs,
                ip_presence,
                dom_distance,
                subdom_distance,
            ]
        )
