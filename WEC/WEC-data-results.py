import csv
import pandas as pd
from great_tables import GT
from tabulate import tabulate

def script_analysis():
    # Raw data read
    df = pd.read_csv("scripts.csv", index_col=False)
    total_pages = len(df)
    # Prune DF for further analysis
    has_scripts = df.query("google_analytics == 1 or meta_pixel == 1 or microsoftuet == 1 or hotjar == 1", inplace=False)
    # Total websites with scripts
    has_scripts_total = len(has_scripts)
    # Check frequency of number of scripts
    g_count = 0
    fb_count = 0
    ms_count = 0
    hj_count = 0
    script_count_freq = []
    for index, row in has_scripts.iterrows():
        script_count = 0
        if row.get("google_analytics") == 1:
            script_count += 1
            g_count += 1
        if row.get("meta_pixel") == 1:
            script_count += 1
            fb_count += 1
        if row.get("microsoftuet") == 1:
            script_count += 1
            ms_count += 1
        if row.get("hotjar") == 1:
            script_count += 1
            hj_count += 1
        script_count_freq.append(script_count)
    # 3rd scr vs no 3rd scr
    freq_script = has_scripts_total / total_pages * 100
    freq_no_script = 100 - freq_script
    # F vs no F table
    script_broad_frequency_dict = {'script': [freq_script], 'no_script': [freq_no_script]}
    script_broad_frequency = pd.DataFrame(script_broad_frequency_dict)
    script_broad_frequency.to_csv("Analysis-Results-Raw/script_broad_frequency.csv", float_format='%.2f', index=False)
    # Script frequency table
    script_number_frequency_dict = {'total': [has_scripts_total]}
    script_number_frequency = pd.DataFrame(script_number_frequency_dict)
    script_number_frequency.to_csv("Analysis-Results-Raw/script_number_frequency.csv", index=False)
    # Percentages of scripts per page
    g_per_page = g_count / has_scripts_total * 100
    fb_per_page = fb_count / has_scripts_total * 100
    ms_per_page = ms_count / has_scripts_total * 100
    hj_per_page = hj_count / has_scripts_total * 100
    # Script usage per page table
    script_percentages_per_page_dict = {'google_analytics': [g_per_page], 'meta_pixel': [fb_per_page], 'microsoftuet': [ms_per_page], 'hotjar': [hj_per_page]}
    script_percentages_per_page = pd.DataFrame(script_percentages_per_page_dict)
    script_percentages_per_page.to_csv("Analysis-Results-Raw/script_percentages_per_page.csv", float_format='%.2f', index=False)    
    # Percentages of scripts
    total_script_count = g_count + fb_count + ms_count + hj_count
    g_overall = g_count / total_script_count * 100
    fb_overall = fb_count / total_script_count * 100
    ms_overall = ms_count / total_script_count * 100
    hj_overall = hj_count / total_script_count * 100
    # Script usage table
    script_percentages_dict = {'google_analytics': [g_overall], 'meta_pixel': [fb_overall], 'microsoftuet': [ms_overall], 'hotjar': [hj_overall]}
    script_percentages = pd.DataFrame(script_percentages_dict)
    script_percentages.to_csv("Analysis-Results-Raw/script_percentages.csv", float_format='%.2f', index=False)

def cookies_analysis():
    # Raw data init
    df = pd.read_csv("cookies.csv", index_col=False)
    total_cookies = len(df)
    third_party = len(df.query("third_party == 1", inplace=False))
    third_party_per = (third_party / total_cookies) * 100
    first_party = len(df.query("first_party == 1", inplace=False))
    first_party_per = (first_party / total_cookies) * 100
    secure_fp = (len(df.query("first_party == 1 and secure == 1", inplace=False)) / first_party) * 100
    secure_tp = (len(df.query("third_party == 1 and secure == 1", inplace=False)) / third_party) * 100
    persistent_fp = (len(df.query("first_party == 1 and persistent == 1", inplace=False)) / first_party) * 100
    persistent_tp = (len(df.query("third_party == 1 and persistent == 1", inplace=False)) / third_party) * 100
    session_fp = (len(df.query("first_party == 1 and session == 1", inplace=False)) / first_party) * 100
    session_tp = (len(df.query("third_party == 1 and session == 1", inplace=False)) / third_party) * 100
    # Total cookies
    total_cookies_df = pd.DataFrame([total_cookies], columns=["total"])
    total_cookies_df.to_csv("Analysis-Results-Raw/total_cookies.csv", index=False)
    # Broad classification of cookies by Party
    broad_cookies_data = {'First-Party': [first_party_per], 'Third-Party': [third_party_per]}
    broad_cookies = pd.DataFrame(broad_cookies_data)
    broad_cookies.to_csv("Analysis-Results-Raw/broad_types_of_cookies.csv", index=False, float_format='%.2f')
    # Classification by origin and types
    type_cookies_data = {'First-Party': [session_fp, persistent_fp, secure_fp], 'Third-Party': [session_tp, persistent_tp, secure_tp]}
    type_cookies = pd.DataFrame(type_cookies_data)
    type_cookies = type_cookies.rename(index={0: "Sesión", 1: "Persistente", 2: "Segura"})
    type_cookies.to_csv("Analysis-Results-Raw/type_of_cookies.csv", float_format='%.2f')

def main():
    cookies_analysis()
    #script_analysis()

if __name__ == '__main__':
    main()