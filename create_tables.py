from mySqlite import *

def create_tables(db_path):
  db = mySqlite(db_path)

  db.query('''CREATE TABLE scan_info
    (ID INTEGER primary key,
    process_date text,
    acquire_date text,
    instrument text,
    pixels int)''')

  db.query('''CREATE TABLE scans
    (ID INTEGER primary key,
    scan_info_id REFERENCES scan_info(ID),
    scan text,
    project text,
    rep text,
    count int,
    X int,
    Y int,
    time text)''')

  db.query('''CREATE TABLE scan_data (
    ID INTEGER primary key,
    scan_id REFERENCES scans(ID),
    band double,
    ref double)''')

  db.commit()
