import sqlite3
import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dbs", help="path to folder, where SQLite databases containing javascript calls crawled are stored", type=str, required=True)
    
    args = parser.parse_args()
    dbs = getattr(args, 'dbs')
    
    return dbs


def test_operations(curs):
    sql_query = "SELECT operation FROM javascript GROUP BY operation ORDER BY operation DESC"
    
    i = 0
    
    for cur in curs:
        cur.execute(sql_query)
        for row in cur.fetchall():
            if row[0] != "call":
                print(str(i) + ": ")
                print(row[0])
        i += 1


def main():
    dbs_folder = parse_args()
    
    dbs = []
    
    for filename in os.listdir(dbs_folder):
        if filename.endswith(".sqlite"):
            dbs.append(sqlite3.connect(os.path.join(dbs_folder + filename)))
    
    curs = []
    
    for db in dbs:
        curs.append(db.cursor())
    
    test_operations(curs)
    
    for db in dbs:
        db.close()


if __name__ == "__main__":
    main()
