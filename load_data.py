from mySqlite import mySqlite

def clean_str(string):
    return string.strip().strip('"').rstrip('"')

def load_CDAP2_data(db_path,data_path):
  #Function loads CDAP-2 reflectance data from file and inserts it into an
  # sqlite3 db

  #connect to the db
  db = mySqlite(db_path)

  with open(data_path,'r') as file:
    #Load all data into memory
    # Do this for now...maybe change later.
    data = [line.split('\t') for line in file]

  #Get the processing date
  processing_date = clean_str(data[0][0][12:-15])

  #Date of aquisition
  acquire_date = clean_str(data[2][0])
  acquire_date = acquire_date[:4]+'-'+acquire_date[4:6]+'-'+acquire_date[6:]

  #Instrument name
  instrument = clean_str(data[4][0])

  #Number of pixels
  pixels = data[4][3]

  #get scan ids
  scan_id = [clean_str(data[7][idx]) for idx in range(1,len(data[7]))]

  #Insert relevant information into the 'scan_info' table.
  db.query('INSERT INTO scan_info VALUES (?,?,?,?,?)',
    [None,processing_date,acquire_date,instrument,pixels])

  #Get the scan_info_id from the previously inserted record
  scan_info_id = db.query('''SELECT id FROM scan_info WHERE process_date = ?
    AND acquire_date = ? AND instrument = ? AND pixels = ?''',
    [processing_date,acquire_date,instrument,pixels])

  scan_info_id = scan_info_id[0][0]

  #get project names
  project = [clean_str(data[9][idx]) for idx in range(1,len(data[9]))]

  #rep names
  rep = [clean_str(data[10][idx]) for idx in range(1,len(data[10]))]

  #Scan number (count)
  count = [int(count) for count in data[8][1:]]

  #X and Y
  x = [data[11][idx] for idx in range(1,len(data[11]))]
  y = [data[12][idx] for idx in range(1,len(data[12]))]

  #Scan time
  scanTime = [data[23][idx] for idx in range(1,len(data[23]))]

  #Get scan data (don't worry about DC)
  band_center = [data[idx][0] for idx in range(59,len(data))]
  scan_data = []
  for idx1 in range(1,len(scan_id)+1):
      scan_data.append([data[idx2][idx1] for idx2 in range(59,len(data))])

  #INSERT TO SCANS, GET SCAN ID, THEN INSERT TO SCAN DATA TABLE,
  # DO THIS FOR ALL SCANS.
  for idx in range(len(count)):
    #Modify scan time to hh:mm:ss.ms
    sTime = scanTime[idx][1:3]+':'+scanTime[idx][4:6]+':'+scanTime[idx][7:-1]
    #Insert relevant info into the scans table
    db.query('INSERT INTO scans VALUES (?,?,?,?,?,?,?,?,?);',
      [None,scan_info_id,scan_id[idx],project[idx],rep[idx],count[idx],
      x[idx],y[idx],sTime])

    #Get the id for the current scan.
    cur_scan = db.query('SELECT id from scans WHERE scan = ?',[scan_id[idx]])
    cur_scan = cur_scan[0][0]

    #Insert the scan data for the current scan.
    for band,ref in zip(band_center,scan_data[idx]):
      db.query('INSERT INTO scan_data VALUES (?,?,?,?)',
        [None,int(cur_scan),float(band),float(ref)])

  db.commit()
