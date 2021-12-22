import sqlite3

db1 = sqlite3.connect("crawl_0-100_privacy.sqlite")
cur1 = db1.cursor()

db_names = []

for db_number in range(100,5100,100):
    db_names.append("crawl_%d-%d_privacy.sqlite" % (db_number, db_number+100))

for db_name in db_names:
    db2 = sqlite3.connect(db_name)
    cur2 = db2.cursor()

    sql_query = "SELECT * FROM javascript"

    cur2.execute(sql_query)
    data = cur2.fetchall()

    sql_query = "insert into javascript (incognito,browser_id,visit_id,extension_session_uuid,event_ordinal,page_scoped_event_ordinal,window_id,tab_id,frame_id,script_url,script_line,script_col,func_name,script_loc_eval,document_url,top_level_url,call_stack,symbol,operation,value,arguments,time_stamp) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    for row in data:
       cur1.execute(sql_query, row[1:]) 
    db1.commit()
    db2.close()


db1.close()