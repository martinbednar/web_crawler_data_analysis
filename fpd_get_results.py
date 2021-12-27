#!/usr/bin/env python

import sqlite3
import csv
import argparse
import json
import os
from pathlib import Path

from support_files import csv_2_xlsx
from support_files import js_endpoint


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dbs", help="the path to the folder where the SQLite databases containing captured javascript calls are stored", type=str, required=True)
    parser.add_argument("--dbs_uMatrix", help="the path to the folder where the SQLite databases containing captured javascript calls with uMatrix are stored", type=str, required=True)
    parser.add_argument("--dbs_uBlock", help="the path to the folder where the SQLite databases containing captured javascript calls with uBlock Origin are stored", type=str, required=True)
    
    args = parser.parse_args()
    dbs_folder = getattr(args, 'dbs')
    dbs_uMatrix_folder = getattr(args, 'dbs_uMatrix')
    dbs_uBlock_folder = getattr(args, 'dbs_uBlock')
    
    return (dbs_folder, dbs_uMatrix_folder, dbs_uBlock_folder)


def export_results(results, output_file_path, csv_header):
    Path(output_file_path.rsplit('/', 1)[0]).mkdir(parents=True, exist_ok=True)
    with open(output_file_path, mode='w', newline='') as output_file:
        csv_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(csv_header)
        for row in results:
            csv_writer.writerow(row)


def analyze(curs, curs_uMatrix, curs_uBlock):
    f = open('support_files/mapped_apis.json')
    apis = json.loads(f.read())
    f.close()
    
    sql_query = "SELECT func_name, COUNT(*) as calls_count, operation FROM javascript GROUP BY func_name ORDER BY calls_count DESC"
    
    endpoints_calls_count = {}
    endpoints_calls_count_uMatrix = {}
    endpoints_calls_count_uBlock = {}
    
    endpoint_type = {}
    
    dbs_count_s = str(len(curs) + len(curs_uMatrix) + len(curs_uBlock))
    i = 1
    
    for cur in curs:
        print("Executing SQL query in db " + str(i) + "/" + dbs_count_s)
        i += 1
        cur.execute(sql_query)
        for endpoint_calls_count in cur.fetchall():
            if not endpoint_calls_count[0] in endpoints_calls_count:
                endpoints_calls_count[endpoint_calls_count[0]] = 0
                endpoint_type[endpoint_calls_count[0]] = endpoint_calls_count[2]
            endpoints_calls_count[endpoint_calls_count[0]] += endpoint_calls_count[1]
    for cur_uMatrix in curs_uMatrix:
        print("Executing SQL query in db " + str(i) + "/" + dbs_count_s)
        i += 1
        cur_uMatrix.execute(sql_query)
        for endpoint_calls_count in cur_uMatrix.fetchall():
            if not endpoint_calls_count[0] in endpoints_calls_count_uMatrix:
                endpoints_calls_count_uMatrix[endpoint_calls_count[0]] = 0
            endpoints_calls_count_uMatrix[endpoint_calls_count[0]] += endpoint_calls_count[1]
            if not endpoint_calls_count[0] in endpoint_type:
                endpoint_type[endpoint_calls_count[0]] = endpoint_calls_count[2]
    for cur_uBlock in curs_uBlock:
        print("Executing SQL query in db " + str(i) + "/" + dbs_count_s)
        i += 1
        cur_uBlock.execute(sql_query)
        for endpoint_calls_count in cur_uBlock.fetchall():
            if not endpoint_calls_count[0] in endpoints_calls_count_uBlock:
                endpoints_calls_count_uBlock[endpoint_calls_count[0]] = 0
            endpoints_calls_count_uBlock[endpoint_calls_count[0]] += endpoint_calls_count[1]
            if not endpoint_calls_count[0] in endpoint_type:
                endpoint_type[endpoint_calls_count[0]] = endpoint_calls_count[2]

    endpoints_calls_count_compare = {}
    
    print("Data agregation started.")
    
    for endpoint_calls_count_key, endpoint_calls_count_value in endpoints_calls_count.items():
        endpoints_calls_count_compare[endpoint_calls_count_key] = []
        endpoints_calls_count_compare[endpoint_calls_count_key].append(endpoint_calls_count_value)

    for endpoint_calls_count_key, endpoint_calls_count_value in endpoints_calls_count_uMatrix.items():
        if endpoint_calls_count_key in endpoints_calls_count_compare:
            endpoints_calls_count_compare[endpoint_calls_count_key].append(endpoint_calls_count_value)

    for endpoint_calls_count_key, endpoint_calls_count_value in endpoints_calls_count_uBlock.items():
        if endpoint_calls_count_key in endpoints_calls_count_compare:
            endpoints_calls_count_compare[endpoint_calls_count_key].append(endpoint_calls_count_value)
    
    print("Export to csv started.")
    
    results = []
    
    for key, value in endpoints_calls_count_compare.items():
            if len(value) == 3:
                endpoint_api = js_endpoint.get_api(key, apis)
                # We have data for all three - casual and privacy crawling too.
                calls = value[0]
                calls_uMatrix = value[1]
                calls_uBlock = value[2]
                difference_uMatrix = calls - calls_uMatrix
                difference_uBlock = calls - calls_uBlock
                difference_uMatrix_percent = difference_uMatrix/calls
                difference_uBlock_percent = difference_uBlock/calls
                weight_uMatrix = max(0, 10 + ((10-len(str(calls)))/2) - ((100-(100*difference_uMatrix_percent))/3) )
                weight_uBlock = max(0, 10 + ((10-len(str(calls)))/2) - ((100-(100*difference_uBlock_percent))/3) )
                average_weight = 0
                if weight_uMatrix > 0 and weight_uBlock > 0:
                    average_weight = round((weight_uMatrix + weight_uBlock)/2)
                results.append([key, endpoint_type[key], average_weight, weight_uMatrix, weight_uBlock, calls, calls_uMatrix, calls_uBlock, difference_uMatrix, difference_uBlock, difference_uMatrix_percent, difference_uBlock_percent])
    
    results_sorted = sorted(results, key=lambda tup: tup[2], reverse=True)
    
    export_results(results_sorted, 'results/endpoint_calls_count.csv', ['Endpoint', 'Operation', 'Weight_average', 'Weight_uMatrix', 'Weight_uBlock', 'Calls without extension', 'Calls with uMatrix', 'Calls with uBlock', 'Difference_uMatrix', 'Difference_uBlock', 'Difference_uMatrix [%]', 'Difference_uBlock [%]'])


def main():
    (dbs_folder, dbs_uMatrix_folder, dbs_uBlock_folder) = parse_args()
    
    dbs = []
    dbs_uMatrix = []
    dbs_uBlock = []
    
    print("Opening DBs.")
    
    for filename in os.listdir(dbs_folder):
        if filename.endswith(".sqlite"):
            dbs.append(sqlite3.connect(os.path.join(dbs_folder + filename)))
    for filename in os.listdir(dbs_uMatrix_folder):
        if filename.endswith(".sqlite"):
            dbs_uMatrix.append(sqlite3.connect(os.path.join(dbs_uMatrix_folder + filename)))
    for filename in os.listdir(dbs_uBlock_folder):
        if filename.endswith(".sqlite"):
            dbs_uBlock.append(sqlite3.connect(os.path.join(dbs_uBlock_folder + filename)))
    
    curs = []
    curs_uMatrix = []
    curs_uBlock = []
    
    for db in dbs:
        curs.append(db.cursor())
    for db_uMatrix in dbs_uMatrix:
        curs_uMatrix.append(db_uMatrix.cursor())
    for db_uBlock in dbs_uBlock:
        curs_uBlock.append(db_uBlock.cursor())
    
    analyze(curs, curs_uMatrix, curs_uBlock)
    
    for db in dbs:
        db.close()
    for db_uMatrix in dbs_uMatrix:
        db_uMatrix.close()
    for db_uBlock in dbs_uBlock:
        db_uBlock.close()
    
    csv_2_xlsx.convert()


if __name__ == "__main__":
    main()
