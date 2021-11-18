import sqlite3
import csv


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


def analyze(cur, cur_p):
    webpage_calls_count(cur, cur_p)
    endpoints_calls_count(cur, cur_p)


def main():
    db = sqlite3.connect('crawl_opensource\\crawl-data.sqlite')
    db_p = sqlite3.connect('crawl_privacy_opensource\\crawl-data.sqlite')
    
    cur = db.cursor()
    cur_p = db_p.cursor()
    
    analyze(cur, cur_p)
    
    db.close()
    db_p.close()


if __name__ == "__main__":
    main()
