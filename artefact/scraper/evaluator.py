#!/usr/bin/env -S conda run -n dissertation python
"""
The evaluator calculates Google Safe Browsing's rate
of success in correctly classifying phishing websites
"""
from selenium import webdriver
import json, csv
import os, time
import httplib2

with open("online-valid.json", "r") as domains_list:
    phishes = json.load(domains_list)

CURRENT_DIR = os.getcwd()
results = []
summary = {
    "totalTested": 0,
    "malicious": 0,
    "benign": 0,
    "exceptions": 0,
    "rateOfSuccess": 0,
}


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


def test_firefox(url):
    profile = webdriver.FirefoxProfile(
        "/home/osboxes/.mozilla/firefox/5prbp52d.default-release-1581000949023"
    )
    profile.set_preference("browser.safebrowsing.blockedURIs.enabled", True)
    profile.set_preference("browser.safebrowsing.downloads.enabled", True)
    profile.set_preference("browser.safebrowsing.enabled", True)
    profile.set_preference("browser.safebrowsing.forbiddenURIs.enabled", True)
    profile.set_preference("browser.safebrowsing.malware.enabled", True)
    profile.set_preference("browser.safebrowsing.phishing.enabled", True)
    profile.set_preference("browser.safebrowsing.downloads.remote.enabled", True)
    profile.set_preference("browser.safebrowsing.provider.google.nextupdatetime", 1)
    profile.set_preference("browser.safebrowsing.provider.mozilla.nextupdatetime", 1)

    opts = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=opts, firefox_profile=profile)
    driver.set_page_load_timeout(35)
    try:
        time.sleep(5)
        driver.get(url)
        source = driver.page_source
        driver.close()
        if "Deceptive" in source or "is blocked" in source:
            return True
        return False
    except Exception as e:
        print(e)
        return e


def test(url, browsers):
    if "chrome" in browsers:
        result = test_chrome(url)
        if isinstance(result, bool):
            record_result("chrome", url, result, None)
        else:
            record_result("chrome", url, None, result)

    if "firefox" in browsers:
        result = test_firefox(url)
        if isinstance(result, bool):
            record_result("firefox", url, result, None)
        else:
            record_result("firefox", url, None, result)
    
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


def main():
    for phish in phishes:
        if is_online(phish["url"]):
            test(phish["url"], ("android"))


if __name__ == "__main__":
    main()
