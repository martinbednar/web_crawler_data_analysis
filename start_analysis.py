import sqlite3
import csv
import argparse

from support_files import csv_2_xlsx


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", help="path to SQLite database containing javascript calls crawled without privacy extension (uMatrix)", type=str, required=True)
    parser.add_argument("--db_p", help="path to SQLite database containing javascript calls crawled with privacy extension (uMatrix)", type=str, required=True)
    
    args = parser.parse_args()
    db = getattr(args, 'db')
    db_p = getattr(args, 'db_p')
    
    return (db, db_p)


def get_api(endpoint):
    return endpoint.split(".")[0]


def export_results(results, output_file_path, csv_header):
    with open(output_file_path, mode='w', newline='') as output_file:
        csv_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(csv_header)
        for row in results:
            csv_writer.writerow(row)


def webpage_calls_count(cur, cur_p):
    sql_query = "SELECT top_level_url, COUNT(*) as calls_count FROM javascript GROUP BY top_level_url ORDER BY calls_count DESC"
    
    cur.execute(sql_query)
    cur_p.execute(sql_query)

    webs_calls_count = cur.fetchall()
    webs_calls_count_p = cur_p.fetchall()

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
                results.append([key, value[0], value[1], value[0] - value[1]])
    
    export_results(results, 'results/webpage_calls_count.csv', ['website', 'casual', 'privacy', 'difference'])


def endpoints_calls_count(cur, cur_p):
    sql_query = "SELECT func_name, COUNT(*) as calls_count FROM javascript GROUP BY func_name ORDER BY calls_count DESC"
    
    cur.execute(sql_query)
    cur_p.execute(sql_query)

    endpoints_calls_count = cur.fetchall()
    endpoints_calls_count_p = cur_p.fetchall()

    endpoints_calls_count_compare = {}
    
    for endpoint_calls_count in endpoints_calls_count:
        endpoints_calls_count_compare[endpoint_calls_count[0]] = []
        endpoints_calls_count_compare[endpoint_calls_count[0]].append(endpoint_calls_count[1])

    for endpoint_calls_count in endpoints_calls_count_p:
        if endpoint_calls_count[0] in endpoints_calls_count_compare:
            endpoints_calls_count_compare[endpoint_calls_count[0]].append(endpoint_calls_count[1])
    
    results = []
    
    for key, value in endpoints_calls_count_compare.items():
            if len(value) == 2:
                # We have data for both - casual and privacy crawling too.
                results.append([key, value[0], value[1], value[0] - value[1]])
    
    export_results(results, 'results/endpoint_calls_count.csv', ['endpoint', 'casual', 'privacy', 'difference'])


def func_count_on_website(cur, cur_p):
    sql_query = "SELECT top_level_url, func_name, COUNT(*) as webpage_func_calls_count FROM javascript GROUP BY top_level_url, func_name ORDER BY top_level_url, webpage_func_calls_count DESC"
    
    cur.execute(sql_query)
    cur_p.execute(sql_query)

    func_count_on_website = cur.fetchall()
    func_count_on_website_p = cur_p.fetchall()
    
    export_results(func_count_on_website, 'results/func_count_on_website.csv', ['top_level_url', 'func_name', 'func_count_on_website'])
    export_results(func_count_on_website_p, 'results/func_count_on_website_p.csv', ['top_level_url', 'func_name', 'func_count_on_website'])
    
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
    results_diff_no_null = []
    
    for key0, value0 in func_count_on_website_compare.items():
        for key1, value1 in value0.items():
            if len(value1) == 2:
                # We have data for both - casual and privacy crawling too.
                results.append([key0, key1, value1[0], value1[1], value1[0] - value1[1]])
                if value1[0] - value1[1] != 0:
                    # Diff in calls count not equal zero.
                    results_diff_no_null.append([key0, key1, value1[0], value1[1], value1[0] - value1[1]])
    
    export_results(results, 'results/func_count_on_website_compare.csv', ['website', 'endpoint', 'casual', 'privacy', 'difference'])
    export_results(results_diff_no_null, 'results/func_count_on_website_compare_diff_not_null.csv', ['website', 'endpoint', 'casual', 'privacy', 'difference'])


def api_calls_count(cur, cur_p):
    sql_query = "SELECT func_name, COUNT(*) as calls_count FROM javascript GROUP BY func_name ORDER BY calls_count DESC"
    
    cur.execute(sql_query)
    cur_p.execute(sql_query)

    endpoints_calls_count = cur.fetchall()
    endpoints_calls_count_p = cur_p.fetchall()
    
    api_calls_count_compare = {}
    
    for api_endpoint_calls_count in endpoints_calls_count:
        endpoint_api = get_api(api_endpoint_calls_count[0])
        if not endpoint_api in api_calls_count_compare:
            api_calls_count_compare[endpoint_api] = []
            api_calls_count_compare[endpoint_api].append(0)
        api_calls_count_compare[endpoint_api][0] += api_endpoint_calls_count[1]
    
    for api_endpoint_calls_count in endpoints_calls_count_p:
        endpoint_api = get_api(api_endpoint_calls_count[0])
        if endpoint_api in api_calls_count_compare:
            if len(api_calls_count_compare[endpoint_api]) < 2:
                api_calls_count_compare[endpoint_api].append(0)
            api_calls_count_compare[endpoint_api][1] += api_endpoint_calls_count[1]
    
    results = []
    
    for key, value in api_calls_count_compare.items():
            if len(value) == 2:
                # We have data for both - casual and privacy crawling too.
                results.append([key, value[0], value[1], value[0] - value[1]])
    
    export_results(results, 'results/api_calls_count.csv', ['api', 'casual', 'privacy', 'difference'])


def analyze(cur, cur_p):
    webpage_calls_count(cur, cur_p)
    endpoints_calls_count(cur, cur_p)
    func_count_on_website(cur, cur_p)
    api_calls_count(cur, cur_p)


def main():
    (db, db_p) = parse_args()
    
    db = sqlite3.connect(db)
    db_p = sqlite3.connect(db_p)
    
    cur = db.cursor()
    cur_p = db_p.cursor()
    
    analyze(cur, cur_p)
    
    db.close()
    db_p.close()
    
    csv_2_xlsx.convert()


if __name__ == "__main__":
    main()
