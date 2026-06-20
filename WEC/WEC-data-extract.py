import json
import re
import pandas as pd
import tldextract
import sys

def scripts():
    google = [
        "googleanalytics.com",
        "google-analytics.com",
        "googletagmanager.com",
        "googletagservices.com",
        "doubleclick.net",
        "invitemedia.com",
        "2mdn.net",
    ]
    facebook = [
        "facebook.com",
        "facebook.net",
    ]
    microsoft = [
        "bing.net",
        "bing.com",
        "clarity.ms",
    ]
    hotjar = "hotjar.com"
    g_flag = False
    ms_flag = False
    fb_flag = False
    hj_flag = False
    tp_scripts_columns = ["google_analytics", "meta_pixel", "microsoftuet", "hotjar"]
    tp_scripts_rows = []
    tp_scripts_data = [0,0,0,0]
    for tp_hosts in data["hosts"]["requests"]["thirdParty"]:
        domain = tldextract.extract(tp_hosts).top_domain_under_public_suffix
        if domain:
            if g_flag == False and domain in google:
                g_flag = True
                tp_scripts_data[0] = 1
            if fb_flag == False and domain in facebook:
                fb_flag = True
                tp_scripts_data[1] = 1
            if ms_flag == False and domain in microsoft:
                ms_flag = True
                tp_scripts_data[2] = 1
            if hj_flag == False and domain in hotjar:
                hj_flag = True
                tp_scripts_data[3] = 1
    tp_scripts_rows.append(tp_scripts_data)
    scripts_df = pd.DataFrame(tp_scripts_rows, columns=tp_scripts_columns)
    scripts_df.to_csv("scripts.csv", index=False, mode="a", header=False)

def cookies():
    # Definition of the dataset
    fields = ["first_party", "third_party", "session", "persistent", "secure"]
    rows = []
    # Several counters for analytics
    cookie_count = 0
    tp_cookies = 0
    # Counts how many of the pages analysed used Third-Party cookies
    fp_cookies = 0
    # Different types of cookies
    session_cookies = 0
    persistent_cookies = 0
    secure_cookies = 0
    for cookie in data["cookies"]:
        cookie_data = []
        cookie_count += 1
        # 1st or 3rd party cookies
        if cookie.get("firstPartyStorage") == True:
            fp_cookies += 1
            cookie_data.append(1)
            cookie_data.append(0)
        else:
            tp_cookies += 1
            cookie_data.append(0)
            cookie_data.append(1)
        # Session cookies
        if cookie.get("session") == True:
            session_cookies += 1
            cookie_data.append(1)
            # append 0 persistent
            cookie_data.append(0)
        else:
            cookie_data.append(0)
            persistent_cookies += 1
            cookie_data.append(1)
        # Secure cookies
        if cookie.get("secure") == True:
            secure_cookies += 1
            cookie_data.append(1)
        else:
            cookie_data.append(0)
        rows.append(cookie_data)
    cookies_df = pd.DataFrame(rows, columns=fields)
    cookies_df.to_csv("cookies.csv", index=False, mode="a", header=False)
def main():
    global data
    with open(sys.argv[1], 'r', encoding="utf8") as raw:
        data = json.load(raw)
    global host
    host = data["host"]
    uri_dest = tldextract.extract(data["uri_dest"])
    global uri_dest_stripped
    uri_dest_stripped = uri_dest.top_domain_under_public_suffix
    print(uri_dest_stripped)
    print("Analysis of host: %s" % host)
    cookies()
    scripts()

if __name__ == "__main__":
    main()