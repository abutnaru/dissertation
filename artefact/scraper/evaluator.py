#!/usr/bin/env -S conda run -n dissertation python
"""
The evaluator calculates Google Safe Browsing's rate
of success in correctly classifying phishing websites
"""
from selenium import webdriver
import json, csv
import os, time
import httplib2, urllib
import json
import argparse


CURRENT_DIR = os.getcwd()
results = []
summary = {
    "totalTested": 0,
    "malicious": 0,
    "benign": 0,
    "exceptions": 0,
    "rateOfSuccess": 0,
}


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Google Safe Browsing classification evaluator"
    )
    parser.add_argument(
        "-i",
        "--infile",
        dest="phishes_file",
        type=str,
        help="URLs to be checked",
        required=True,
    )
    parser.add_argument(
        "-a",
        "--api",
        dest="api_testing",
        help="Toggle mixed urls in target dataset",
        action="store_true",
    )

    args = parser.parse_args()
    return args.phishes_file, "api" if args.api_testing else "browser"


def update_summary_file(summary):
    record_evolution(summary["rateOfSuccess"])
    s = open("summary.json", "w")
    json.dump(summary, s)
    s.close()


def record_evolution(rate_of_success):
    f = open("success.csv", "a")
    writer = csv.writer(f)
    writer.writerow([rate_of_success])


def update_records_file(results):
    r = open("results.json", "w")
    json.dump(results, r)
    r.close()


def record_result(browser, url, detected, exception):
    res = {
        "browser": browser,
        "url": url,
        "detected": "",
        "exception": "",
    }
    if detected:
        res["deteted"] = True
        update_summary("new_malicious")
        res["exception"] = None
        print("{} \t\t\tMalicious".format(url))
    elif not detected:
        res["detected"] = False
        update_summary("new_benign")
        res["exception"] = None
        print("{} \t\t\tBenign".format(url))
    else:
        res["exception"] = str(exception)
        update_summary("new_exception")
        res["detected"] = None
        print("{} \t\t\tException".format(url))
    results.append(res)
    update_records_file(results)


def update_summary(updateItem):
    if updateItem == "new_malicious":
        summary["malicious"] += 1
    elif updateItem == "new_benign":
        summary["benign"] += 1
    else:
        summary["exceptions"] += 1

    if summary["malicious"] == 0:
        summary["rateOfSuccess"] = 0
    else:
        summary["rateOfSuccess"] = (
            summary["malicious"] / (summary["malicious"] + summary["benign"])
        ) * 100
    summary["totalTested"] = (
        summary["malicious"] + summary["benign"] + summary["exceptions"]
    )

    update_summary_file(summary)


def test_android(url):
    try:
        driver = webdriver.Remote(
            desired_capabilities=webdriver.DesiredCapabilities.ANDROID
        )
        driver.set_page_load_timeout(25)
        # Testing without this
        # except Exception as e:
        #    return e
        # try:
        driver.get(url)
        title = driver.title
        button = driver.find_element_by_tag_name("button")
        src = driver.page_source
        print(title, button, src)
        driver.save_screenshot("chrome/" + url.replace("/", "__") + ".png")
        driver.quit()
        if title == "Security error":
            return True
        return False
    except Exception as e:
        print(e)
        return e


def test_chrome(url):
    opts = webdriver.ChromeOptions()
    opts.add_argument("--user-data-dir=/home/osboxes/.config/google-chrome")
    opts.add_argument("--profile-directory=Default")
    opts.add_argument("--ignore-certificate-errors")
    try:
        driver = webdriver.Chrome(options=opts)
        driver.set_page_load_timeout(25)
        # Testing without this
        # except Exception as e:
        #    return e
        # try:
        driver.get(url)
        source = driver.page_source
        # driver.save_screenshot("chrome/" + url.replace("/", "__") + ".png")
        driver.quit()
        google_stamp = """<!-- Copyright 2015 The Chromium Authors. All rights reserved.
     Use of this source code is governed by a BSD-style license that can be
     found in the LICENSE file. -->"""
        if google_stamp in source:
            return True
        return False
    except Exception as e:
        print(e)
        return e


def browser_check(url, browsers):
    if "chrome" in browsers:
        result = test_chrome(url)
        if isinstance(result, bool):
            record_result("chrome", url, result, None)
        else:
            record_result("chrome", url, None, result)

    if "android" in browsers:
        result = test_android(url)
        if isinstance(result, bool):
            record_result("firefox", url, result, None)
        else:
            record_result("firefox", url, None, result)


# Not really working
def is_online(url):
    try:
        h = httplib2.Http(timeout=10, disable_ssl_certificate_validation=True)
        resp = h.request(url, "HEAD")
        if int(resp[0]["status"]) < 400:
            print(int(resp[0]["status"]))
            return True
        print(int(resp[0]["status"]))
        return False
    except:
        return False


def read_in_chunks(f_in, chunk_size=500):
    """Lazy function (generator) to read a file piece by piece."""
    phishes = json.load(f_in)
    index = 0
    while True:
        records = phishes[index:index+500]
        index += 500
        if not records:
            break
        yield records


def api_check(phishes_file):
    APIKEY = "AIzaSyDeefzwH7Fspz2D4AazFEZVYPQ07U1zt5w"
    true_positives = 0
    total_urls = 0
    parsed_phishes = list()
    for phishes in read_in_chunks(phishes_file):
        #if total_urls == 1500:
        #   break
        total_urls+=len(phishes)
        parsed_phishes = [{"url": phish["url"]} for phish in phishes]

        body = {
            "client": {"clientId": "dissertation", "clientVersion": "1.5.2"},
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
                "platformTypes": ["WINDOWS"],
                "threatEntryTypes": ["URL"],
                "threatEntries": parsed_phishes,
            },
        }
        response = httplib2.Http().request(
            f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={APIKEY}",
            method="POST",
            headers={"Content-type": "application/json"},
            body=json.dumps(body),
        )[1]
        matches = [obj for obj in json.loads(response.decode())['matches']]
        c = 0
        for m in matches:
            c = sum([1 if m['threat']['url'] == phish['url'] else 0 for phish in phishes])
            true_positives += c
    print(f"True positives: {true_positives}\nTotal URLs: {total_urls}\nSuccess rate: {(true_positives/total_urls)*100}%")


def main():
    target_filename, api_flag = parse_arguments()
    f_in=  open(f"{target_filename}.json", "r")
    if api_flag:
        api_check(f_in)
    else:
        for phish in json.load(f_in):
            if is_online(phish["url"]):
                browser_check(phish["url"], ("chrome"))


if __name__ == "__main__":
    print("Initiating Google safe-browsing evaluation...\n")
    start = time.perf_counter()
    main()
    finish = time.perf_counter()
    print(f"\nEvaluation f_inished in {round(finish-start,2)} seconds")
