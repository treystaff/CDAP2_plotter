import sqlite3

def db_connect(db):
  #Returns a database connectiton and cursor.
  # (maybe put this in a separate tools file?)
  conn = sqlite3.connect(db)
  cursor = conn.cursor()
  return conn, cursor

def load_CDAP2_data(db,path):
  #Function loads CDAP-2 reflectance data from file and inserts it into an
  # sqlite3 db

  #connect to the db
  conn,cursor = db_connect(db)

  with open(path,'r') as file:
    #Load all data into memory
    # Do this for now...change later.
    data = [line.split() for line in file]

  #Get the processing date
  year = data[0][2]
  month = data[0][4]
  day = data[0][6]
  processing_date = year + '-' + month + '-' + day

  #Date of aquisition
  acquire_date = data[2][0]
  acquire_date = acquire_date[:4]+'-'+acquire_date[4:6]+'-'+acquire_date[6:]

  #Instrument name
  instrument = data[4][0]

  #Number of pixels
  pixels = data[4][6]

  #get scan ids
  scan_id = [data[7][idx] for idx in range(1,len(data[7]))]

  #Insert relevant information into the 'scan_info' table.
  cursor.execute('INSERT INTO scan_info VALUES (?,?,?,?,?)',
    [None,processing_date,acquire_date,instrument,pixels])

  #Get the scan_info_id from the previously inserted record
  cursor.execute('''SELECT id FROM scan_info WHERE process_date = ?
    AND acquire_date = ? AND instrument = ? AND pixels = ?''',
    [processing_date,acquire_date,instrument,pixels])
  scan_info_id = cursor.fetchone()
  scan_info_id = scan_info_id[0]

  #get project names
  project = [data[9][idx] for idx in range(1,len(data[9]))]

  #rep names
  rep = [data[10][idx] for idx in range(1,len(data[10]))]

  #Scan number (count)
  count = [int(count) for count in data[8][1:]]

  #X and Y
  x = [data[11][idx] for idx in range(1,len(data[11]))]
  y = [data[12][idx] for idx in range(1,len(data[12]))]

  #Get scan data (don't worry about DC)
  band_center = [data[idx][0] for idx in range(59,len(data))]
  scan_data = []
  for idx1 in range(1,len(scan_id)+1):
      scan_data.append([data[idx2][idx1] for idx2 in range(59,len(data))])

  #INSERT TO SCANS, GET SCAN ID, THEN INSERT TO SCAN DATA TABLE,
  # DO THIS FOR ALL SCANS.
  for idx in range(len(count)):
    #Insert relevant info into the scans table
    cursor.execute('INSERT INTO scans VALUES (?,?,?,?,?,?,?,?);',
      [None,scan_info_id,scan_id[idx],project[idx],rep[idx],count[idx],
      x[idx],y[idx]])

    #Get the id for the current scan.
    cursor.execute('SELECT id from scans WHERE scan = ?',[scan_id[idx]])
    cur_scan = cursor.fetchone()
    cur_scan = cur_scan[0]

    #Insert the scan data for the current scan.
    for band,ref in zip(band_center,scan_data[idx]):
      cursor.execute('INSERT INTO scan_data VALUES (?,?,?,?)',
        [None,int(cur_scan),float(band),float(ref)])

  conn.commit()
