import sys
sys.path.append('/home/trey/Documents/code/CDAP2_plotter/')
from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
from load_data import *

def plot_data(*args):
  conn,cursor = db_connect('/tmp/CDAPtest.db')
  print(scan_idVar.get())
  cursor.execute('''select band,ref from scan_data where
    scan_id = (select id from scans where scan = ?)''',[scan_idVar.get()])
  data = cursor.fetchall()
  band,ref = zip(*data)
  plt.ion()
  plt.plot(band,ref)

#Set up the main window
root = Tk()
root.title("Simple Plot GUI")
mainframe = ttk.Frame(root,padding="3 3 12 12")
mainframe.grid(column=0, row=0,sticky=(N,W,E,S))
#The frame will take up the entire window's size if resized.
mainframe.columnconfigure(0,weight=1)
mainframe.rowconfigure(0,weight=1)

scan_idVar = StringVar()
scan_id = ttk.Combobox(root,textvariable=scan_idVar)
scan_id.grid(column=1,row=1,sticky=(W))

#Get a list of scan_ids from the db
conn,cursor = db_connect('/tmp/CDAPtest.db')
cursor.execute('SELECT scan from scans ORDER BY project,rep,count')
scan_ids = cursor.fetchall()
scan_id['values'] = [scan[0] for scan in scan_ids]

button = ttk.Button(root,text="Plot",command=plot_data)
button.grid(column=2,row=1,sticky=(E))

#put a bit of padding around all widgets
for child in mainframe.winfo_children():
  child.grid_configure(padx=5, pady=5)

#final line (needed to make everything run)
root.mainloop()
