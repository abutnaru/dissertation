"""
The features extractor decomposes each URL in the set of selected 
features and saves the records in a CSV file. Selected features are: URL
size, protocol used (HTTP/HTTPS), domain and subdomain digit count,
symbols count ('@', '~'), presence
"""
import csv
import re
import subprocess
import urllib.parse as urllib

import editdistance as levenshtein
import numpy as np
import tldextract as tld


def hamming_distance(s1, s2):
    return len(list(filter(lambda x: ord(x[0]) ^ ord(x[1]), zip(s1, s2))))


def min_distances(url, N):
    """
    Calculates the minimum value for the levenshtein distance between
    the top N domains and the URL's domain and the hamming distance
    between the top N domains and URL's subdomain. To ensure precision,
    the subdomain is split on "." and "-" and then fed into the hamming
    distance calculation.
    """
    subdomain, domain = tld.extract(url)[:2]
    f_benign_1M = open("data/processed_sets/benign_1M.csv")

    min_dd, min_sd = 100, 100
    index = 1
    for row in csv.reader(f_benign_1M):
        b_domain = tld.extract(row[0]).domain
        levdd = levenshtein.eval(domain, b_domain)
        if levdd < min_dd:
            min_dd = levdd

        # Splitting the subdomain to cover cases similar to
        # https://target-brand.customer-service.signin.example.com/
        for component in subdomain.split("."):
            if "-" in component:
                for subcomp in component.split("-"):
                    hamsd = hamming_distance(subcomp, b_domain)
                    if hamsd < min_sd:
                        min_sd = hamsd
            else:
                hamsd = hamming_distance(component, b_domain)
                if hamsd < min_sd:
                    min_sd = hamsd
        index += 1
        if index == N:
            break

    # Test based on the assumption that two strings with levenstain
    # distance greater than 10 can be regarded as different. Otherwise
    # the target URL's domain and subdomain are considered similar to
    # one of the top N domains
    min_subdomain_distance = (
        1
        if min_sd <= 5
        and "www" not in subdomain
        and len(subdomain.split(".")) == 1
        else 0
    )

    min_domain_distance = 1 if min_dd <= 5 and min_dd != 0 else 0

    return min_subdomain_distance, min_domain_distance


def has_domain(url, N):
    f_benign_list = open("data/processed_sets/benign_1M.csv")
    index = 1

    for row in csv.reader(f_benign_list):
        # Testing first if the length of the domain is greater or equal
        # to 5 to reduce false positives produced by domains like t.com
        if len(row[0]) >= 5 and (row[0] in url.path or row[0] in url.query):
            return True
        index += 1
        if index == N:
            break

    f_benign_list.close()
    return False


def contains(words, target, check_domains=False):
    if check_domains:
        for word in words:
            if word in target:
                return 1
        return 1 if has_domain(target, 2500) else 0
    else:
        for word in words:
            if word in target:
                return 1
        return 0


def extract(raw_url, label=-1):
    """
    Decomposes passed URL into the selected list of features
    """
    parsed_url = urllib.urlparse(raw_url)
    netloc = tld.extract(raw_url)
    path_dot_count = parsed_url.path.count(".") + parsed_url.query.count(".")

    ### Feature 1: URL size
    # Reasoning: The literature shows a clear discrepancy between the
    # average benign URL size and average phishing URL size.
    url_size = len(raw_url)

    ### Feature 2: Protocol used (HTTP/HTTPS)
    # Reasoning: Although the number of phishing websites has risen
    # significantly in recent years, serving a website through HTTP is
    # still an indicator of maliciousness in most cases.
    tls_usage = 1 if raw_url.split(":")[0] == "http" else 0

    ### Feature 3: Number of numerical characters
    # Reasoning: It is highly uncommon for benign domains and subdomains
    # to contain any numerical characters.
    digit_count = sum(c.isdigit() for c in parsed_url.netloc)

    ### Feature 4: Number of '@' and '~' characters
    # Reasoning: Like numerical characters, it is uncommon for an URL to
    # contain any '~' characters. The '@' character produces unexpected
    # behaviour in the browser. It could either redirect to an email
    # address or get the browser to ignore everything after it.
    symbols_count = raw_url.count("@") + raw_url.count("~")

    # Feature 5: Domain presence in the url path segment
    # Reasoning: This feature determines whether the path contains a
    # domain. This practice is often found in redirects and domains
    # hosted on places like firebase or storage.googleapis.com.
    domain_in_path = 1 if path_dot_count >= 2 else 0

    ### Feature 6: Number of hyphens
    # Reasoning: It is uncommon for benign domains and subdomains to use
    # hyphens to separate words while it is common for phishing URLs to
    # use them. If a domain is detected in path, the number of hyphens
    # is counted over the entire URL
    dash_count = (
        parsed_url.netloc.count("-")
        if path_dot_count < 2
        else raw_url.count("-")
    )

    # Feature 7: Size of the subdomain
    # Reasoning: The literature shows that there is a strong correlation
    # between a logn subdomain and phishing webpages. In this feature
    # the length of the subdomain is based on its components rather than
    # character count as past experiments proved it more effective
    components = netloc.subdomain.count(".") + netloc.subdomain.count("-") + 1
    _long_subdomain = 1 if components >= 3 else 0

    # Features 8,9 and 10: Presence of sensitive vocabulary and of
    # benign domains in URL's subdomain
    # Reasoning: The sensitive words shown below are a curated selection
    # from the output of a word frequency algorithm and are an indicator
    # of suspiciousness. Because it is a common practice for phishing
    # URLs to inlcude the target brand in their subdomain, the sensitive
    # subdomain words check the presence of top N benign domains as well
    sensitive_subdomains = [
        "paypal",
        "sites",
        "secure",
        "login",
        "runescape",
        "account",
        "service",
        "sign",
        "bank",
        "transfer",
        "user",
        "security",
    ]
    sensitive_domains = [
        "000webhost",
        "sharepoint",
        "customer",
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
    subdomain_sw = contains(sensitive_subdomains, netloc.subdomain)
    domain_sw = contains(sensitive_domains, netloc.domain)
    path_sw = contains(sensitive_paths, parsed_url, check_domains=True)

    # Feature 11: Presence of IP address in URL
    # Reasoning: Usage of IP address instead of a domain name is tighyly
    # related to phishing/malicious intent.
    ip_presence = (
        1 if len(re.findall(r"[0-9]+(?:\.[0-9]+){3}", raw_url)) != 0 else 0
    )

    # Feature 12 and 13: Minimum distance between URL's domain and
    # subdomain and the top N benign domains
    # Reasoning: It is a common practice for phishing URLs to use a
    # variation of the targeted domain either in their domain or
    # subdomain to create the illusion of the legit website.
    suspicious_domain, suspicious_subdomain = min_distances(raw_url, 25_000)

    if label >= 0:
        return np.array(
            [
                label,
                url_size,
                tls_usage,
                digit_count,
                symbols_count,
                domain_in_path,
                dash_count,
                # long_subdomain,
                subdomain_sw,
                domain_sw,
                path_sw,
                ip_presence,
                suspicious_domain,
                suspicious_subdomain,
            ]
        )
    return np.array(
        [
            url_size,
            tls_usage,
            digit_count,
            symbols_count,
            domain_in_path,
            dash_count,
            # long_subdomain,
            subdomain_sw,
            domain_sw,
            path_sw,
            ip_presence,
            suspicious_domain,
            suspicious_subdomain,
        ]
    )
