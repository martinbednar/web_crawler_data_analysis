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
    
    args = parser.parse_args()
    dbs = getattr(args, 'dbs')
    
    return dbs


def export_results(results, output_file_path, csv_header):
    with open(output_file_path, mode='w', newline='') as output_file:
        csv_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(csv_header)
        for row in results:
            csv_writer.writerow(row)


def endpoints_and_apis_count(curs, curs_p):
    sql_query = "SELECT func_name, COUNT(*) as calls_count FROM javascript GROUP BY func_name ORDER BY calls_count DESC"
    
    endpoints_calls_count = {}
    endpoints_calls_count_p = {}
    
    for cur in curs:
        cur.execute(sql_query)
        for endpoint_calls_count in cur.fetchall():
            if endpoint_calls_count[0] in endpoints_calls_count:
                endpoints_calls_count[endpoint_calls_count[0]] += endpoint_calls_count[1]
            else:
                endpoints_calls_count[endpoint_calls_count[0]] = endpoint_calls_count[1]
    for cur_p in curs_p:
        cur_p.execute(sql_query)
        for endpoint_calls_count in cur_p.fetchall():
            if endpoint_calls_count[0] in endpoints_calls_count_p:
                endpoints_calls_count_p[endpoint_calls_count[0]] += endpoint_calls_count[1]
            else:
                endpoints_calls_count_p[endpoint_calls_count[0]] = endpoint_calls_count[1]

    endpoints_calls_count_compare = {}
    
    api_calls_count_compare = {}
    
    f = open('support_files/mapped_apis.json')
    apis = json.loads(f.read())
    f.close()
    
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
    
    results = []
    
    for key, value in endpoints_calls_count_compare.items():
            if len(value) == 2:
                # We have data for both - casual and privacy crawling too.
                results.append([key, value[0], value[1], value[0] - value[1]])
    
    export_results(results, 'results/endpoint_calls_count.csv', ['Endpoint', 'Calls without uMatrix', 'Calls with uMatrix', 'Difference'])
    
    results = []
    
    for key, value in api_calls_count_compare.items():
            if len(value) == 2:
                # We have data for both - casual and privacy crawling too.
                results.append([key, value[0], value[1], value[0] - value[1]])
    
    export_results(results, 'results/api_calls_count.csv', ['api', 'casual', 'privacy', 'difference'])


def func_count_on_website(curs, curs_p):
    sql_query = "SELECT top_level_url, func_name, COUNT(*) as webpage_func_calls_count FROM javascript GROUP BY top_level_url, func_name ORDER BY top_level_url, webpage_func_calls_count DESC"
    
    func_count_on_website = []
    func_count_on_website_p = []
    
    for cur in curs:
        cur.execute(sql_query)
        func_count_on_website.extend(cur.fetchall())
    for cur_p in curs_p:
        cur_p.execute(sql_query)
        func_count_on_website_p.extend(cur_p.fetchall())
    
    export_results(func_count_on_website, 'results/func_count_on_website.csv', ['Website', 'Endpoint', 'Calls without uMatrix'])
    export_results(func_count_on_website_p, 'results/func_count_on_website_p.csv', ['Website', 'Endpoint', 'Calls with uMatrix'])
    
    func_count_on_website_compare = {}
    
    for web_func_calls_count in func_count_on_website:
        if not web_func_calls_count[0] in func_count_on_website_compare:
            func_count_on_website_compare[web_func_calls_count[0]] = {}
        func_count_on_website_compare[web_func_calls_count[0]][web_func_calls_count[1]] = []
        func_count_on_website_compare[web_func_calls_count[0]][web_func_calls_count[1]].append(web_func_calls_count[2])
    
    for web_func_calls_count in func_count_on_website_p:
        if web_func_calls_count[0] in func_count_on_website_compare:
            if web_func_calls_count[1] in func_count_on_website_compare[web_func_calls_count[0]]:
                func_count_on_website_compare[web_func_calls_count[0]][web_func_calls_count[1]].append(web_func_calls_count[2])
    
    results = []
    
    for key0, value0 in func_count_on_website_compare.items():
        for key1, value1 in value0.items():
            if len(value1) == 2:
                # We have data for both - casual and privacy crawling too.
                results.append([key0, key1, value1[0], value1[1], value1[0] - value1[1]])
    
    export_results(results, 'results/func_count_on_website_compare.csv', ['Website', 'Endpoint', 'Calls without uMatrix', 'Calls with uMatrix', 'Difference'])


def analyze(curs, curs_p):
    endpoints_and_apis_count(curs, curs_p)
    func_count_on_website(curs, curs_p)


def main():
    dbs_folder = parse_args()
    
    dbs = []
    dbs_p = []
    
    for filename in os.listdir(dbs_folder):
        if filename.endswith(".sqlite"):
            if "privacy" in filename:
                dbs_p.append(sqlite3.connect(os.path.join(dbs_folder + filename)))
            else:
                dbs.append(sqlite3.connect(os.path.join(dbs_folder + filename)))
    
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
