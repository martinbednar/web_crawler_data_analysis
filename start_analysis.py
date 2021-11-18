import sqlite3
import csv

def webpage_calls_count(cur, cur_p):
    cur.execute("SELECT top_level_url, COUNT(*) as calls_count FROM javascript GROUP BY top_level_url ORDER BY calls_count DESC")
    cur_p.execute("SELECT top_level_url, COUNT(*) as calls_count FROM javascript GROUP BY top_level_url ORDER BY calls_count DESC")

    webs_calls_count = cur.fetchall()
    webs_calls_count_p = cur_p.fetchall()

    webs_calls_count_compare = {}

    for web_calls_count in webs_calls_count:
        webs_calls_count_compare[web_calls_count[0]] = []
        webs_calls_count_compare[web_calls_count[0]].append(web_calls_count[1])

    for web_calls_count in webs_calls_count_p:
        if web_calls_count[0] in webs_calls_count_compare:
            webs_calls_count_compare[web_calls_count[0]].append(web_calls_count[1])

    with open('webpage_calls_count.csv', mode='w', newline='') as output_file:
        fieldnames = ['website', 'casual', 'privacy', 'difference']
        csv_writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writeheader()
        for key, value in webs_calls_count_compare.items():
            if len(value) == 2:
                # We have data for both - casual and privacy crawling too
                csv_writer.writerow({'website': key, 'casual': value[0], 'privacy': value[1], 'difference': value[0] - value[1]})


def analyze(cur, cur_p):
    webpage_calls_count(cur, cur_p)


def main():
    db = sqlite3.connect('crawler_opensource\\crawl-data.sqlite')
    db_p = sqlite3.connect('crawler_privacy_opensource\\crawl-data.sqlite')
    
    cur = db.cursor()
    cur_p = db_p.cursor()
    
    analyze(cur, cur_p)
    
    db.close()
    db_p.close()


if __name__ == "__main__":
    main()
