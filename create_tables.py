import sqlite3
def create_tables(db):
  conn = sqlite3.connect(db)
  c = conn.cursor()

  c.execute('''CREATE TABLE scan_info
    (ID INTEGER primary key,
    process_date text,
    acquire_date text,
    instrument text,
    pixels int)''')

  c.execute('''CREATE TABLE scans
    (ID INTEGER primary key,
    scan_info_id REFERENCES scan_info(ID),
    scan text,
    project text,
    rep text,
    count int,
    X int,
    Y int)''')

  c.execute('''CREATE TABLE scan_data (
    ID INTEGER primary key,
    scan_id REFERENCES scans(ID),
    band double,
    ref double)''')

  conn.commit()
