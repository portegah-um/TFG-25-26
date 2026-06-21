import sqlite3
import pandas as pd
import tldextract

TOTAL_PAGES = 1000

def exec_query_fg(query):
    results = cur.execute(query).fetchall()
    for site in results:
        site = ''.join(map(str, site))
        if site in fingerprint_site_frequency:
            fingerprint_site_frequency[site] += 1
        else:
            fingerprint_site_frequency[site] = 1
    return len(results)

def getJSFingerprint():
    jsf_query_init = '''SELECT DISTINCT visit_id FROM javascript
    WHERE symbol LIKE 'window.navigator%'
        OR symbol LIKE 'window.screen%'
        OR symbol LIKE 'window.Intl.DateTimeFormat'
        OR symbol LIKE 'window.Intl.getCanonicalLocales'
    GROUP BY visit_id
    '''
    jsf_query_obj_enum = '''SELECT COUNT(DISTINCT symbol) FROM javascript
    WHERE visit_id == ?
    AND (symbol LIKE 'window.navigator%'
        OR symbol LIKE 'window.screen%'
        OR symbol LIKE 'window.Intl.DateTimeFormat'
        OR symbol LIKE 'window.Intl.getCanonicalLocales')'''
    jsf_visit_ids = cur.execute(jsf_query_init).fetchall()
    jsf_count = 0
    for site in jsf_visit_ids:
        num_objects = cur.execute(jsf_query_obj_enum, site).fetchone()
        num_objects = int(''.join(map(str, num_objects)))
        if num_objects > 13:
            jsf_count += 1
            site = ''.join(map(str, site))
            if site in fingerprint_site_frequency:
                fingerprint_site_frequency[site] += 1
            else:
                fingerprint_site_frequency[site] = 1 
    return jsf_count

def getWebRTC():
    wrtc_query = '''SELECT DISTINCT visit_id FROM javascript
    WHERE symbol == 'RTCPeerConnection.addIceCandidate'
    OR symbol == 'RTCPeerConnection.createDataChannel'
    OR symbol == 'RTCPeerConnection.createOffer'
    OR symbol == 'RTCPeerConnection.onicecandidate'
    '''
    return exec_query_fg(wrtc_query)

def getWebGL():
    webgl_query = '''WITH TargetVisits AS (
	SELECT DISTINCT visit_id FROM javascript
	WHERE (symbol == 'WebGLRenderingContext.getParameter'
		AND arguments LIKE '%3744_%')
		OR symbol == 'HTMLCanvasElement.get%Extension%'
		OR symbol == 'WebGLRenderingContext.getContextAttributes'
		OR symbol == 'readPixels'
    )
    SELECT DISTINCT visit_id
    FROM javascript
    WHERE visit_id IN (SELECT visit_id FROM TargetVisits)
    AND (symbol == 'HTMLCanvasElement.toDataURL'
    OR symbol == 'HTMLCanvasElement.toBlob'
    OR symbol == 'CanvasRenderingContext2D.getImageData')
    '''
    return exec_query_fg(webgl_query)

def getCanvasFont():
    cvf_query_init = '''SELECT DISTINCT visit_id FROM javascript
    WHERE symbol == 'CanvasRenderingContext2D.measureText'
    '''
    cvf_query_count = '''SELECT COUNT(*) FROM javascript
    WHERE visit_id = ?
    AND symbol == 'CanvasRenderingContext2D.measureText'
    '''
    cvf_visit_ids = cur.execute(cvf_query_init).fetchall()
    cvf_count = 0
    for site in cvf_visit_ids:
        measureText_count = cur.execute(cvf_query_count, site).fetchone()
        measureText_count = int(''.join(map(str, measureText_count)))
        if measureText_count >= 50:
            cvf_count += 1
            site = ''.join(map(str, site))
            if site in fingerprint_site_frequency:
                fingerprint_site_frequency[site] += 1
            else:
                fingerprint_site_frequency[site] = 1 
    return cvf_count

def getCanvas():
    canvas_query='''WITH TargetVisits AS (
	SELECT DISTINCT visit_id FROM javascript
	WHERE ((symbol == 'HTMLCanvasElement.width'
		AND CAST(value as int) < 16)
		OR (symbol == 'HTMLCanvasElement.height'
		AND CAST(value as int) < 16))
	OR (symbol == 'HTMLCanvasElement.setAttribute'
		AND arguments LIKE '%hidden%')
    )
    SELECT DISTINCT visit_id
    FROM javascript
    WHERE visit_id IN (SELECT visit_id FROM TargetVisits)
    AND symbol == 'HTMLCanvasElement.toDataURL'
    OR symbol == 'HTMLCanvasElement.toBlob'
    OR symbol == 'CanvasRenderingContext2D.getImageData'
    '''
    return exec_query_fg(canvas_query)

def getAudioContext():
    audiocontext_query = '''WITH TargetVisits AS (
        SELECT DISTINCT visit_id
        FROM javascript
        WHERE symbol LIKE '%AudioContext.create%'
        OR symbol LIKE '%AudioContext.audioWorklet'
    )
    SELECT DISTINCT visit_id
    FROM javascript
    WHERE visit_id IN (SELECT visit_id FROM TargetVisits)
    AND (symbol LIKE 'AudioBuffer%'
    OR symbol LIKE 'AnalyserNode.get%Data%'
    OR symbol LIKE '%.destination'
    OR symbol LIKE '%.listener')'''
    return exec_query_fg(audiocontext_query)

def fingerprinting():
    fp_counter = 0
    global fingerprint_site_frequency
    fingerprint_site_frequency = {}
    # Types of fingerprinters
    # AudioContext
    ac_counter = getAudioContext()
    # Canvas
    cv_counter = getCanvas()
    # Font
    cvf_counter = getCanvasFont()
    # WebGL
    wgl_counter = getWebGL()
    # WebRTC
    wrtc_counter = getWebRTC()
    # JS Fingerprint
    js_counter = getJSFingerprint()
    # Frequency counters
    fingerprint_frequency_values = list(fingerprint_site_frequency.values())
    one_time = fingerprint_frequency_values.count(1)
    two_times = fingerprint_frequency_values.count(2)
    three_times = fingerprint_frequency_values.count(3)
    four_times = fingerprint_frequency_values.count(4)
    five_times = fingerprint_frequency_values.count(5)
    six_times = fingerprint_frequency_values.count(6)
    has_fingerprint_total = one_time + two_times + three_times + four_times + five_times + six_times
    zero_times = total_pages_analysed - has_fingerprint_total
    # Fingerprint frequency table
    fingerprint_number_frequency_dict = {'0': [zero_times], '1': [one_time], '2': [two_times], '3': [three_times], '4': [four_times], '5': [five_times], '6': [six_times]}
    fingerprint_number_frequency = pd.DataFrame(fingerprint_number_frequency_dict)
    fingerprint_number_frequency.to_csv("Analysis-Results-Raw/fingerprint_number_frequency.csv", index=False)
    # Fingerprint vs no fingerprint
    print(has_fingerprint_total, total_pages_analysed)
    freq_fingerprint = has_fingerprint_total / total_pages_analysed * 100
    print(freq_fingerprint)
    freq_no_fingerprint = 100 - freq_fingerprint
    # F vs no F table
    fingerprint_broad_frequency_dict = {'Fingerprint': [freq_fingerprint], 'No Fingerprint': [freq_no_fingerprint]}
    fingerprint_broad_frequency = pd.DataFrame(fingerprint_broad_frequency_dict)
    fingerprint_broad_frequency.to_csv("Analysis-Results-Raw/fingerprint_broad_frequency.csv", float_format='%.2f', index=False)
    # Percentages of fingerprint in relation to pages
    ac_per_page = ac_counter / has_fingerprint_total * 100
    cv_per_page = cv_counter / has_fingerprint_total * 100
    cvf_per_page = cvf_counter / has_fingerprint_total * 100
    wgl_per_page = wgl_counter / has_fingerprint_total * 100
    wrtc_per_page = wrtc_counter / has_fingerprint_total * 100
    js_per_page = js_counter / has_fingerprint_total * 100
    # Fingerprint usage per page table
    fingerprint_percentages_total_dict = {'AudioContext': [ac_per_page], 'Canvas': [cv_per_page], 'Canvas Font': [cvf_per_page], 'WebGL': [wgl_per_page], 'WebRTC': [wrtc_per_page], 'JS Enumeration': [js_per_page]}
    fingerprint_percentages_total_page = pd.DataFrame(fingerprint_percentages_total_dict)
    fingerprint_percentages_total_page.to_csv("Analysis-Results-Raw/fingerprint_percentages_per_page.csv", float_format='%.2f', index=False)
    # Percentage of fingerprint usage in total
    total_fingerprint_count = ac_counter + cv_counter + cvf_counter + wgl_counter + wrtc_counter + js_counter
    ac_overall = ac_counter / total_fingerprint_count * 100
    cv_overall = cv_counter / total_fingerprint_count * 100
    cvf_overall = cvf_counter / total_fingerprint_count * 100
    wgl_overall = wgl_counter / total_fingerprint_count * 100
    wrtc_overall = wrtc_counter / total_fingerprint_count * 100
    js_overall = js_counter / total_fingerprint_count * 100
    # Fingerprint total usage table
    fingerprint_percentages_total_dict = {'AudioContext': [ac_overall], 'Canvas': [cv_overall], 'Canvas Font': [cvf_overall], 'WebGL': [wgl_overall], 'WebRTC': [wrtc_overall], 'JS Enumeration': [js_overall]}
    fingerprint_percentages_total = pd.DataFrame(fingerprint_percentages_total_dict)
    fingerprint_percentages_total.to_csv("Analysis-Results-Raw/fingerprint_percentages_total.csv", float_format='%.2f', index=False)

def scripts():
    count_queries = {
        "google": "SELECT COUNT(DISTINCT(visit_id)) FROM http_responses WHERE url LIKE \'%google-analytics%\' OR url LIKE \'%googleanalytics%\' OR url LIKE \'%googletagmanager%\' OR url LIKE \'%googletagservices%\' OR url LIKE \'%doubleclick%\' OR url LIKE \'%invitemedia%\' OR url LIKE \'%2mdn%\'",
        "facebook": "SELECT COUNT(DISTINCT(visit_id)) FROM http_responses WHERE url LIKE \'%facebook%\'",
        "microsoft": "SELECT COUNT(DISTINCT(visit_id)) FROM http_responses WHERE url LIKE \'%bing%\' OR url LIKE \'%clarity%\'",
        "hotjar": "SELECT COUNT(DISTINCT(visit_id)) FROM http_responses WHERE url LIKE \'%hotjar%\'",
    }
    distinct_queries = {
        "google": "SELECT DISTINCT(visit_id) FROM http_responses WHERE url LIKE \'%google-analytics%\' OR url LIKE \'%googleanalytics%\' OR url LIKE \'%googletagmanager%\' OR url LIKE \'%googletagservices%\' OR url LIKE \'%doubleclick%\' OR url LIKE \'%invitemedia%\' OR url LIKE \'%2mdn%\'",
        "facebook": "SELECT DISTINCT(visit_id) FROM http_responses WHERE url LIKE \'%facebook%\'",
        "microsoft": "SELECT DISTINCT(visit_id) FROM http_responses WHERE url LIKE \'%bing%\' OR url LIKE \'%clarity%\'",
        "hotjar": "SELECT DISTINCT(visit_id) FROM http_responses WHERE url LIKE \'%hotjar%\'",
    }
    g_count = 0
    fb_count = 0
    ms_count = 0
    hj_count = 0
    script_site_frequency = {}
    for type, query in count_queries.items():
        res = cur.execute(query)
        if res:
            match type:
                # First to execute, will also initialise the dictionary
                case "google":
                    g_count = int(''.join(map(str, res.fetchall()[0])))
                    sites = cur.execute(distinct_queries.get("google")).fetchall()
                    for site in sites:
                        site = ''.join(map(str, site))
                        script_site_frequency[site] = 1
                case "facebook":
                    fb_count = int(''.join(map(str, res.fetchall()[0])))
                    sites = cur.execute(distinct_queries.get("facebook")).fetchall()
                    for site in sites:
                        site = ''.join(map(str, site))
                        if site in script_site_frequency:
                            script_site_frequency[site] += 1
                        else:
                            script_site_frequency[site] = 1
                case "microsoft":
                    ms_count = int(''.join(map(str, res.fetchall()[0])))
                    sites = cur.execute(distinct_queries.get("microsoft")).fetchall()
                    for site in sites:
                        site = ''.join(map(str, site))
                        if site in script_site_frequency:
                            script_site_frequency[site] += 1
                        else:
                            script_site_frequency[site] = 1
                case "hotjar":
                    hj_count = int(''.join(map(str, res.fetchall()[0])))
                    sites = cur.execute(distinct_queries.get("hotjar")).fetchall()
                    for site in sites:
                        site = ''.join(map(str, site))
                        if site in script_site_frequency:
                            script_site_frequency[site] += 1
                        else:
                            script_site_frequency[site] = 1
    # Counters
    site_frequency_values = list(script_site_frequency.values())
    one_time = site_frequency_values.count(1)
    two_times = site_frequency_values.count(2)
    three_times = site_frequency_values.count(3)
    four_times = site_frequency_values.count(4)
    has_scripts_total = one_time + two_times + three_times + four_times
    # Script frequency table
    script_number_frequency_dict = {'total': [has_scripts_total]}
    script_number_frequency = pd.DataFrame(script_number_frequency_dict)
    script_number_frequency.to_csv("Analysis-Results-Raw/script_number_frequency.csv", index=False)
    # Scr vs no Scr
    freq_script = has_scripts_total / total_pages_analysed * 100
    freq_no_script = 100 - freq_script
    # F vs no F table
    script_broad_frequency_dict = {'Script': [freq_script], 'No Script': [freq_no_script]}
    script_broad_frequency = pd.DataFrame(script_broad_frequency_dict)
    script_broad_frequency.to_csv("Analysis-Results-Raw/script_broad_frequency.csv", float_format='%.2f', index=False)
    # Percentages of scripts per page
    g_per_page = g_count / has_scripts_total * 100
    fb_per_page = fb_count / has_scripts_total * 100
    ms_per_page = ms_count / has_scripts_total * 100
    hj_per_page = hj_count / has_scripts_total * 100
    # Script usage per page table
    script_percentages_per_page_dict = {'Google Analytics': [g_per_page], 'Meta Pixel': [fb_per_page], 'MicrosoftUET': [ms_per_page], 'Hotjar': [hj_per_page]}
    script_percentages_per_page = pd.DataFrame(script_percentages_per_page_dict)
    script_percentages_per_page.to_csv("Analysis-Results-Raw/script_percentages_per_page.csv", float_format='%.2f', index=False)    
    # Percentages of scripts
    total_script_count = g_count + fb_count + ms_count + hj_count
    g_overall = g_count / total_script_count * 100
    fb_overall = fb_count / total_script_count * 100
    ms_overall = ms_count / total_script_count * 100
    hj_overall = hj_count / total_script_count * 100
    # Script usage table
    script_percentages_dict = {'Google Analytics': [g_overall], 'Meta Pixel': [fb_overall], 'MicrosoftUET': [ms_overall], 'Hotjar': [hj_overall]}
    script_percentages = pd.DataFrame(script_percentages_dict)
    script_percentages.to_csv("Analysis-Results-Raw/script_percentages.csv", float_format='%.2f', index=False)

def cookies():
    cookies_query = '''
                SELECT javascript_cookies.visit_id, site_visits.site_url, javascript_cookies.host,
                        javascript_cookies.is_host_only, javascript_cookies.is_secure, javascript_cookies.is_session
                FROM javascript_cookies
				JOIN site_visits
				ON javascript_cookies.visit_id = site_visits.visit_id
                GROUP BY javascript_cookies.visit_id, javascript_cookies.host, javascript_cookies.name
                ORDER BY javascript_cookies.visit_id, javascript_cookies.host, javascript_cookies.event_ordinal ASC
    '''
    cookies_only_visit_ids_query = '''
                SELECT COUNT(DISTINCT javascript_cookies.visit_id) FROM javascript_cookies
                GROUP BY javascript_cookies.visit_id
				ORDER BY javascript_cookies.visit_id
				ASC'''
    total_sites_with_cookies = len(cur.execute(cookies_only_visit_ids_query).fetchall())
    tp_cookies_counter = 0
    fp_cookies_counter = 0
    session_cookies_counter = 0
    persistent_cookies_counter = 0
    host_only_cookies_counter = 0
    secure_cookies_counter = 0
    all_cookies = cur.execute(cookies_query).fetchall()
    '''
    Tuple format:
        0 --> visit_id
        1 --> site_url
        2 --> host_url
        3, 4, 5 --> cookie_options
            3 --> host_only
            4 --> secure
            5 --> session
    '''
    # Local array to get combinations of options + type
    total_cookie_columns = ["first_party", "third_party", "host_only", "secure", "session"]
    total_cookie_array = []
    for cookie in all_cookies:
        cookies_row = [0,0,0,0,0]
        # First/Third Party
        if tldextract.extract(cookie[1]).top_domain_under_public_suffix in cookie[2]:
            fp_cookies_counter += 1
            cookies_row[0] = 1
        else:
            tp_cookies_counter += 1
            cookies_row[1] = 1
        # Host-Only
        if cookie[3] == 1:
            host_only_cookies_counter += 1
            cookies_row[2] = 1
        # Secure
        if cookie[4] == 1:
            secure_cookies_counter += 1
            cookies_row[3] = 1
        # Session/Persistent
        if cookie[5] == 1:
            session_cookies_counter += 1
            cookies_row[4] = 1
        else:
            persistent_cookies_counter += 1
        total_cookie_array.append(cookies_row)
    # Cookies with several options
    total_cookies_df = pd.DataFrame(total_cookie_array, columns=total_cookie_columns)
    sort_host_only = total_cookies_df.query("host_only == 1", inplace=False)
    fp_hostonly = len(sort_host_only.query("first_party == 1", inplace=False)) / fp_cookies_counter * 100
    tp_hostonly = len(sort_host_only.query("third_party == 1", inplace=False)) / tp_cookies_counter * 100
    sort_secure = total_cookies_df.query("secure == 1", inplace=False)
    fp_secure = len(sort_secure.query("first_party == 1", inplace=False)) / fp_cookies_counter * 100
    tp_secure = len(sort_secure.query("third_party == 1", inplace=False)) / tp_cookies_counter * 100
    sort_session = total_cookies_df.query("session == 1", inplace=False)
    fp_session = len(sort_session.query("first_party == 1", inplace=False)) / fp_cookies_counter * 100
    tp_session = len(sort_session.query("third_party == 1", inplace=False)) / tp_cookies_counter * 100
    fp_persistent = 100 - fp_session
    tp_persistent = 100 - tp_session
    # Total cookies
    total_cookies_count = tp_cookies_counter + fp_cookies_counter
    total_cookies_dict = {'total': [total_cookies_count]}
    total_cookies = pd.DataFrame(total_cookies_dict)
    total_cookies.to_csv("Analysis-Results-Raw/total_cookies.csv", index=False)
    # Cookies vs no cookies
    print(total_sites_with_cookies, total_pages_analysed)
    freq_cookies = total_sites_with_cookies / total_pages_analysed * 100
    print(freq_cookies)
    freq_no_cookies = 100 - freq_cookies
    # Cookie frequency table
    cookies_frequency_dict = {'cookies': [freq_cookies], 'no_cookies': [freq_no_cookies]}
    cookies_frequency = pd.DataFrame(cookies_frequency_dict)
    cookies_frequency.to_csv("Analysis-Results-Raw/cookies_frequency.csv", float_format='%.2f', index=False)
    # Distribution FP vs TP
    freq_fp_cookies = fp_cookies_counter / total_cookies_count * 100
    freq_tp_cookies = tp_cookies_counter / total_cookies_count * 100
    # Dist. table
    freq_fp_tp_dict = {'first_party': [freq_fp_cookies], 'third_party': [freq_tp_cookies]}
    freq_fp_tp = pd.DataFrame(freq_fp_tp_dict)
    freq_fp_tp.to_csv("Analysis-Results-Raw/fp_tp_frequency.csv", float_format='%.2f', index=False)
    # Classification by origin and types
    type_cookies_data = {'first_party': [fp_hostonly, fp_secure, fp_session, fp_persistent], 'third_party': [tp_hostonly, tp_secure, tp_session, tp_persistent]}
    type_cookies = pd.DataFrame(type_cookies_data)
    type_cookies = type_cookies.rename(index={0: "host_only", 1: "secure", 2: "session", 3: "persistent"})
    type_cookies.to_csv("Analysis-Results-Raw/type_of_cookies.csv", float_format='%.2f')

def main():
    con = sqlite3.connect("crawl-data.sqlite")
    global cur
    cur = con.cursor()
    # Number of valid tests
    global total_pages_analysed
    total_pages_analysed = cur.execute("SELECT COUNT(*) FROM incomplete_visits")
    total_pages_analysed = int(''.join(map(str, total_pages_analysed.fetchall()[0])))
    total_pages_analysed = TOTAL_PAGES - total_pages_analysed
    print(total_pages_analysed)
    # Analysis
    cookies()
    #scripts()
    #fingerprinting()
    con.close()

if __name__=="__main__":
    main()