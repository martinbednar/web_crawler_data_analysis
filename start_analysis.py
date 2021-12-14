import sqlite3
import csv
import argparse
import json
import os

from support_files import csv_2_xlsx
from support_files import js_endpoint


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dbs", help="path to folder, where SQLite databases containing javascript calls crawled are stored", type=str, required=True)
    parser.add_argument("--dbs_p", help="path to folder, where SQLite databases containing javascript calls crawled with privacy extension are stored", type=str, required=True)
    
    args = parser.parse_args()
    dbs = getattr(args, 'dbs')
    dbs_p = getattr(args, 'dbs_p')
    
    return (dbs, dbs_p)


def export_results(results, output_file_path, csv_header):
    with open(output_file_path, mode='w', newline='') as output_file:
        csv_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(csv_header)
        for row in results:
            csv_writer.writerow(row)


def endpoints_and_apis_count(curs, curs_p, apis):
    sql_query = "SELECT func_name, COUNT(*) as calls_count, operation FROM javascript GROUP BY func_name ORDER BY calls_count DESC"
    
    endpoints_calls_count = {}
    endpoints_calls_count_p = {}
    
    dbs_count_s = str(len(curs) + len(curs_p))
    i = 1
    
    for cur in curs:
        print("Executing SQL query in db " + str(i) + "/" + dbs_count_s)
        i += 1
        cur.execute(sql_query)
        for endpoint_calls_count in cur.fetchall():
            if endpoint_calls_count[0] in endpoints_calls_count:
                endpoints_calls_count[endpoint_calls_count[0]] += endpoint_calls_count[1]
            else:
                endpoints_calls_count[endpoint_calls_count[0]] = endpoint_calls_count[1]
    for cur_p in curs_p:
        print("Executing SQL query in db " + str(i) + "/" + dbs_count_s)
        i += 1
        cur_p.execute(sql_query)
        for endpoint_calls_count in cur_p.fetchall():
            if endpoint_calls_count[0] in endpoints_calls_count_p:
                endpoints_calls_count_p[endpoint_calls_count[0]] += endpoint_calls_count[1]
            else:
                endpoints_calls_count_p[endpoint_calls_count[0]] = endpoint_calls_count[1]

    endpoints_calls_count_compare = {}
    
    api_calls_count_compare = {}
    
    print("Data agregation started.")
    
    for endpoint_calls_count_key, endpoint_calls_count_value in endpoints_calls_count.items():
        endpoints_calls_count_compare[endpoint_calls_count_key] = []
        endpoints_calls_count_compare[endpoint_calls_count_key].append(endpoint_calls_count_value)
        
        endpoint_api = js_endpoint.get_api(endpoint_calls_count_key, apis)
        if not endpoint_api in api_calls_count_compare:
            api_calls_count_compare[endpoint_api] = []
            api_calls_count_compare[endpoint_api].append(0)
        api_calls_count_compare[endpoint_api][0] += endpoint_calls_count_value

    for endpoint_calls_count_key, endpoint_calls_count_value in endpoints_calls_count_p.items():
        if endpoint_calls_count_key in endpoints_calls_count_compare:
            endpoints_calls_count_compare[endpoint_calls_count_key].append(endpoint_calls_count_value)
        
        endpoint_api = js_endpoint.get_api(endpoint_calls_count_key, apis)
        if endpoint_api in api_calls_count_compare:
            if len(api_calls_count_compare[endpoint_api]) < 2:
                api_calls_count_compare[endpoint_api].append(0)
            api_calls_count_compare[endpoint_api][1] += endpoint_calls_count_value
    
    print("Export to csv started.")
    
    results = []
    
    for key, value in endpoints_calls_count_compare.items():
            if len(value) == 2:
                endpoint_api = js_endpoint.get_api(key, apis)
                # We have data for both - casual and privacy crawling too.
                results.append([key, endpoint_api, value[0], value[1], value[0] - value[1], (value[0] - value[1])/value[0]])
    
    results_sorted = sorted(results, key=lambda tup: tup[5], reverse=True)
    
    export_results(results_sorted, 'results/endpoint_calls_count.csv', ['Endpoint', 'API', 'Calls without uBlock', 'Calls with uBlock', 'Difference', 'Difference [%]'])
    
    results = []
    
    for key, value in api_calls_count_compare.items():
            if len(value) == 2:
                # We have data for both - casual and privacy crawling too.
                results.append([key, value[0], value[1], value[0] - value[1], (value[0] - value[1])/value[0]])
    
    results_sorted = sorted(results, key=lambda tup: tup[4], reverse=True)
    
    export_results(results_sorted, 'results/api_calls_count.csv', ['API', 'Calls without uBlock', 'Calls with uBlock', 'Difference', 'Difference [%]'])
    

def func_count_on_website(curs, curs_p, apis):
    sql_query = "SELECT top_level_url, func_name, COUNT(*) as webpage_func_calls_count FROM javascript GROUP BY top_level_url, func_name ORDER BY top_level_url, webpage_func_calls_count DESC"
    
    func_count_on_website = []
    func_count_on_website_p = []
    
    websites = []
    websites_p = []
    
    for cur in curs:
        cur.execute(sql_query)
        website_funcs = cur.fetchall()
        func_count_on_website.extend(website_funcs)
        for website_func in website_funcs:
         if not website_func[0] in websites:
            websites.append(website_func[0])
    
    for cur_p in curs_p:
        cur_p.execute(sql_query)
        website_funcs = cur_p.fetchall()
        func_count_on_website_p.extend(website_funcs)
        for website_func in website_funcs:
         if not website_func[0] in websites_p:
            websites_p.append(website_func[0])
    
    func_count_on_website_compare = {}
    used_apis = {}
    apis_on_websites = {}
    
    for web_func_calls_count in func_count_on_website:
        if not web_func_calls_count[0] in func_count_on_website_compare:
            func_count_on_website_compare[web_func_calls_count[0]] = {}
        func_count_on_website_compare[web_func_calls_count[0]][web_func_calls_count[1]] = []
        func_count_on_website_compare[web_func_calls_count[0]][web_func_calls_count[1]].append(web_func_calls_count[2])
        
        endpoint_api = js_endpoint.get_api(web_func_calls_count[1], apis)
        
        if not web_func_calls_count[0] in used_apis:
            used_apis[web_func_calls_count[0]] = []
        if len(used_apis[web_func_calls_count[0]]) == 0:
            used_apis[web_func_calls_count[0]].append([])
        if not endpoint_api in used_apis[web_func_calls_count[0]][0]:
            used_apis[web_func_calls_count[0]][0].append(endpoint_api)
        
        if not endpoint_api in apis_on_websites:
            apis_on_websites[endpoint_api] = []
        if len(apis_on_websites[endpoint_api]) == 0:
            apis_on_websites[endpoint_api].append([])
        if not web_func_calls_count[0] in apis_on_websites[endpoint_api][0]:
            apis_on_websites[endpoint_api][0].append(web_func_calls_count[0])
    
    for web_func_calls_count in func_count_on_website_p:
        if web_func_calls_count[0] in func_count_on_website_compare:
            if web_func_calls_count[1] in func_count_on_website_compare[web_func_calls_count[0]]:
                func_count_on_website_compare[web_func_calls_count[0]][web_func_calls_count[1]].append(web_func_calls_count[2])
        
        endpoint_api = js_endpoint.get_api(web_func_calls_count[1], apis)
        
        if web_func_calls_count[0] in used_apis:
            if len(used_apis[web_func_calls_count[0]]) < 2:
                used_apis[web_func_calls_count[0]].append([])
            if not endpoint_api in used_apis[web_func_calls_count[0]][1]:
                used_apis[web_func_calls_count[0]][1].append(endpoint_api)
        
        if endpoint_api in apis_on_websites:
            if len(apis_on_websites[endpoint_api]) < 2:
                apis_on_websites[endpoint_api].append([])
            if not web_func_calls_count[0] in apis_on_websites[endpoint_api][1]:
                apis_on_websites[endpoint_api][1].append(web_func_calls_count[0])
    
    results = []
    
    for key0, value0 in func_count_on_website_compare.items():
        for key1, value1 in value0.items():
            if len(value1) == 2:
                # We have data for both - casual and privacy crawling too.
                results.append([key0, key1, value1[0], value1[1], value1[0] - value1[1], (value1[0] - value1[1])/value1[0]])
    
    results_sorted = sorted(results, key=lambda tup: tup[5], reverse=True)
    
    export_results(results_sorted, 'results/func_count_on_website.csv', ['Website', 'Endpoint', 'Calls without uBlock', 'Calls with uBlock', 'Difference', 'Difference [%]'])
    
    results = []
    
    for key, value in used_apis.items():
        if len(value) == 2:
            # We have data for both - casual and privacy crawling too.
            number_of_apis = len(value[0])
            number_of_apis_p = len(value[1])
            results.append([key, number_of_apis, number_of_apis_p, number_of_apis - number_of_apis_p, (number_of_apis - number_of_apis_p)/number_of_apis])
    
    results_sorted = sorted(results, key=lambda tup: tup[4], reverse=True)
    
    export_results(results_sorted, 'results/apis_count_on_website.csv', ['Website', 'APIs without uBlock', 'APIs with uBlock', 'Difference', 'Difference [%]'])
    
    results = []
    websites_count = len(websites)
    websites_p_count = len(websites_p)
    
    for key, value in apis_on_websites.items():
        if len(value) == 2:
            # We have data for both - casual and privacy crawling too.
            number_of_websites = len(value[0])
            number_of_websites_p = len(value[1])
            results.append([key, number_of_websites/websites_count, number_of_websites_p/websites_p_count, (number_of_websites - number_of_websites_p)/max(websites_count, websites_p_count), number_of_websites, number_of_websites_p, number_of_websites - number_of_websites_p])
    
    results_sorted = sorted(results, key=lambda tup: tup[3], reverse=True)
    
    export_results(results_sorted, 'results/websites_count_using_api.csv', ['API', 'Websites without uBlock [%]', 'Websites with uBlock [%]', 'Difference [%]', 'Websites without uBlock', 'Websites with uBlock', 'Difference'])


def webpage_calls_count(curs, curs_p):
    sql_query = "SELECT top_level_url, COUNT(*) as calls_count FROM javascript GROUP BY top_level_url ORDER BY calls_count DESC"

    webs_calls_count = []
    webs_calls_count_p = []

    for cur in curs:
        cur.execute(sql_query)
        webs_calls_count.extend(cur.fetchall())
    for cur_p in curs_p:
        cur_p.execute(sql_query)
        webs_calls_count_p.extend(cur_p.fetchall())

    webs_calls_count_compare = {}

    for web_calls_count in webs_calls_count:
        webs_calls_count_compare[web_calls_count[0]] = []
        webs_calls_count_compare[web_calls_count[0]].append(web_calls_count[1])

    for web_calls_count in webs_calls_count_p:
        if web_calls_count[0] in webs_calls_count_compare:
            webs_calls_count_compare[web_calls_count[0]].append(web_calls_count[1])

    results = []

    for key, value in webs_calls_count_compare.items():
            if len(value) == 2:
                # We have data for both - casual and privacy crawling too.
                results.append([key, value[0], value[1], value[0] - value[1], (value[0] - value[1])/value[0]])

    results_sorted = sorted(results, key=lambda tup: tup[4], reverse=True)
    
    export_results(results_sorted, 'results/webpage_calls_count.csv', ['Website', 'Calls without uBlock', 'Calls with uBlock', 'Difference', 'Difference [%]'])


def analyze(curs, curs_p):
    f = open('support_files/mapped_apis.json')
    apis = json.loads(f.read())
    f.close()
    
    endpoints_and_apis_count(curs, curs_p, apis)
    func_count_on_website(curs, curs_p, apis)
    webpage_calls_count(curs, curs_p)


def main():
    (dbs_folder, dbs_p_folder) = parse_args()
    
    dbs = []
    dbs_p = []
    
    print("Opening DBs.")
    
    for filename in os.listdir(dbs_folder):
        if filename.endswith(".sqlite"):
            dbs.append(sqlite3.connect(os.path.join(dbs_folder + filename)))
    for filename in os.listdir(dbs_p_folder):
        if filename.endswith(".sqlite"):
            dbs_p.append(sqlite3.connect(os.path.join(dbs_p_folder + filename)))
    
    curs = []
    curs_p = []
    
    for db in dbs:
        curs.append(db.cursor())
    for db_p in dbs_p:
        curs_p.append(db_p.cursor())
    
    analyze(curs, curs_p)
    
    for db in dbs:
        db.close()
    for db_p in dbs_p:
        db_p.close()
    
    
    csv_2_xlsx.convert()


if __name__ == "__main__":
    main()
