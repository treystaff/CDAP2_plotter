from __builtin__ import file

def load_data(path):
    with open(path,'r') as file:
        #NOTE: THIS IS AN INCOMPLETE REPRESENTATION 
        #OF THE INFORMATION STORED IN path.
        
        #Load all data into memory
        data = [line.split() for line in file]
        
        #Get the processing date
        year = data[0][2]
        month = data[0][4]
        day = data[0][6]
        processing_date = year + '-' + month + '-' + day 
        
        #Date of aquisition
        aquire_date = data[2][0]
        
        #get scan ids
        scan_id = [data[7][idx] for idx in range(1,len(data[7]))]
        
        #get project names
        project = [data[9][idx] for idx in range(1,len(data[9]))]
        
        #rep
        rep = [data[10][idx] for idx in range(1,len(data[10]))]
        
        #X and Y
        x = [data[11][idx] for idx in range(1,len(data[11]))]
        Y = [data[12][idx] for idx in range(1,len(data[12]))]
        
        #Get scan data (don't worry about DC yet)
        band_center = [data[idx][0] for idx in range(59,len(data))]
        scan_data = []
        for idx1 in range(1,len(scan_id)+1):
            scan_data.append([data[idx2][idx1] for idx2 in range(59,len(data))])