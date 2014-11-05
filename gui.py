import sys
sys.path.append('/home/trey/Documents/code/CDAP2_plotter/')
from tkinter import *
from tkinter import ttk
from tkinter import colorchooser
import matplotlib.pyplot as plt
from load_data import *
from mySqlite import *

class scanData:
  def __init__(self,db):
    self.currentSelection = None
    self.selectedScans = []
    self.scanIds = []
    self.db = db

  def add(self,scaninfo):
    #Currently, scaninfo is a dictionary
    #Get the scan name from the db (and scan_info_id)
    scan_info_id, scaninfo['scan'] = self.db.query('''SELECT scan_info_id,scan FROM scans
      WHERE id = ?''',scaninfo['id'])[0]

    #Get scan_info from the db
    process_date,acquire_date,instrument,pixels = self.db.query(
      '''SELECT process_date,acquire_date,instrument,pixels FROM scan_info
      WHERE id = ?''',scan_info_id)[0]

    scaninfo['process_date'] = process_date
    scaninfo['acquire_date'] = acquire_date
    scaninfo['instrument'] = instrument
    scaninfo['pixels'] = pixels

    #Add scan data to scaninfo
    data = self.db.query('''SELECT band,ref
      FROM scan_data WHERE scan_id = ?''',int(scaninfo['id']))

    band,ref = zip(*data)

    #Add the matplotlib 2D line obj
    scaninfo['line'], = plt.plot(band,ref)

    #Add a dict of line properties (properties filled in by user)
    scaninfo['properties'] = {'color':None,'thickness':None,'style':None,
      'label':None}
    self.selectedScans.append(scaninfo)

  def remove(self,idx):
    #If the plot window is open, refresh the view.
    if plt.fignum_exists(1):
      self.selectedScans[idx]['line'].remove()
      plt.show()
    return self.selectedScans.pop(idx)

  def get_cur_scan(self):
    if self.currentSelection is not None:
      return self.selectedScans[self.currentSelection]

class app:
  def __init__(self,master):
    self.master = master
    self.master.title("CDAP2_Plotter")
    self.master.columnconfigure(0,weight=1)
    self.master.rowconfigure(0,weight=1)

    #Create the tab structure.
    self.create_tabs()

    #Set up the db connection
    self.db = mySqlite('/tmp/CDAPtest.db')

    #Initialize the scanData obj.
    self.scanData = scanData(self.db)

    #Create the widgets
    self.create_widgets()

    #put a bit of padding around all widgets
    for child in self.master.winfo_children():
      child.grid_configure(padx=5, pady=5)

    self.nb.grid(row=0,column=0,sticky=(N,E,W,S))

    #Turn on matplotlib's interactive plot
    plt.ion()

  def create_tabs(self):
    #The application will have three tabs.
    self.nb = ttk.Notebook(self.master)
    self.t1 = ttk.Frame(self.nb)
    #The column for each tab will be
    self.t1.columnconfigure(1,weight=1)
    self.nb.add(self.t1,text='T1')
    self.t2 = ttk.Frame(self.nb)
    self.t2.columnconfigure(1,weight=1)
    self.nb.add(self.t2,text='T2')
    self.t3 = ttk.Frame(self.nb)
    self.t3.columnconfigure(1,weight=1)
    self.nb.add(self.t3,text='T3')

  #The create widgets function.
  def create_widgets(self):
    self.create_project_dropdown()
    self.create_scans_tree()
    self.create_scan_select_button()
    self.create_scan_remove_button()
    self.create_selected_scans_listboxes()
    self.create_metadata_box()
    self.create_t3_frames()
    self.create_line_color_button()

  def create_project_dropdown(self):
    #Create a label for the dropdown
    self.projectLabel = ttk.Label(self.t2,text='Project:')
    self.projectLabel.grid(column=0,row=0,sticky=(N,E,W,S))
    #Select a project.
    self.projectNameVar = StringVar()
    self.project_name = ttk.Combobox(self.t2,textvariable=self.projectNameVar)
    self.project_name.bind("<<ComboboxSelected>>",self.populate_scans)
    self.project_name.grid(column=1,row=0,sticky=(N,E,W,S))
    self.t2.rowconfigure(0,weight=0)
    self.get_project_names(self)

  def create_scans_tree(self):
    #Create a tree listing available scans
    self.tree = ttk.Treeview(self.t2,columns=('X','Y','COUNT','TIME'))
    self.tree.column('X',width=50)
    self.tree.heading('X',text='X')
    self.tree.column('Y',width=50)
    self.tree.heading('Y',text='Y')
    self.tree.column('COUNT',width=75)
    self.tree.heading('COUNT',text='COUNT')
    self.tree.column('TIME',width=75)
    self.tree.heading('TIME',text='TIME')
    self.tree.grid(column=0,row=1,columnspan=2,sticky=(N,S,E,W))
    self.t2.rowconfigure(1,weight=1)

  def create_scan_select_button(self):
    #Create a move-to-selected button
    self.selectScanB = ttk.Button(self.t2,text='+',command=self.select_scans)
    self.selectScanB.grid(column=0,row=2,sticky=(W))

  def create_scan_remove_button(self):
    self.removeScanB = ttk.Button(self.t2,text='-',command=self.remove_scans)
    self.removeScanB.grid(column=1,row=2,sticky=(E))

  def create_line_color_button(self):
    self.lineColorB = ttk.Button(self.linePropertiesFrm,text='Choose Color',
      command=self.choose_line_color)
    self.lineColorB.grid(column=1,row=1,sticky=(E))

    #ALSO A LABEL
    self.colorLabel = ttk.Label(self.linePropertiesFrm,text='Line Color:')
    self.colorLabel.grid(column=0,row=1,sticky=(W))

  def create_selected_scans_listboxes(self):
    #Tab2 listbox
    self.selectedListboxT2 = Listbox(self.t2)
    self.selectedListboxT2.bind("<<ListboxSelect>>",self.update_selection)
    self.selectedListboxT2.grid(column=0,row=3,columnspan=2,sticky=(N,S,E,W))
    #Tab3 listbox
    self.selectedListboxT3 = Listbox(self.t3)
    self.selectedListboxT3.bind("<<ListboxSelect>>",self.update_selection)
    self.selectedListboxT3.grid(column=0,row=1,columnspan=2,sticky=(N,S,E,W))

  def update_selection(self,event):
    if event.widget == self.selectedListboxT2:
      self.scanData.currentSelection = int(self.selectedListboxT2.curselection()[0])
      self.selectedListboxT3.activate(self.scanData.currentSelection)
    else:
      self.scanData.currentSelection = int(self.selectedListboxT3.curselection()[0])
      self.selectedListboxT2.activate(self.scanData.currentSelection)
    self.populate_metadata()

  def create_t3_frames(self):
    self.linePropertiesFrm = ttk.Frame(self.t3)
    self.linePropertiesFrm.grid(column=0,row=2,columnspan=2,sticky=(N,S,E,W))
    self.graphPropertiesFrm = ttk.Frame(self.t3)
    self.graphPropertiesFrm.grid(column=0,row=3,columnspan=2,sticky=(N,S,E,W))

    #Label the line properties frame.
    self.linePropertiesLabel = ttk.Label(self.linePropertiesFrm,text='Line Properties')
    self.linePropertiesLabel.grid(column=0,row=0,sticky=(N,E,W,S))

    #Label the graph properties frame.
    self.graphPropertiesLabel = ttk.Label(self.graphPropertiesFrm,text='Graph Properties')
    self.graphPropertiesLabel.grid(column=0,row=0,sticky=(N,E,W,S))

  def create_metadata_box(self):
    #CREATES THE METADATA BOX ON T3.
    #THIS WILL BE POPULATED WITH INFORMATION ON SCAN SELECTION.
    #(Needs key binding on select)
    self.metaBox = Text(self.t3)
    self.metaBox.grid(column=0,row=0,columnspan=2,sticky=(N,S,E,W))
    self.metaBox.config(state=DISABLED)

  def get_project_names(self,event):
    #Get a list of projects from the db
    project_names = self.db.query('''SELECT DISTINCT(project) from scans
      ORDER BY project,rep,count''')
    self.project_name['values'] = [project[0] for project in project_names]

  #Basic data plotting function.
  def plot_data(self):
    plt.show()

  def choose_line_color(self):
    selectedColor = colorchooser.askcolor()
    if selectedColor:
      plt.setp(self.scanData.get_cur_scan()['line'],
        color=selectedColor[-1])
      self.scanData.get_cur_scan()['properties']['color'] = selectedColor[-1]

  def populate_scans(self,event):
    #FUNCTION TO POPULATE THE SCANS TREE.
    #First remove any existing scans from the tree
    while self.tree.get_children():
      self.tree.delete(tree.get_children()[0])

    #Query for a new list of scans
    scans = self.db.query('''SELECT ID,rep,X,Y,count,time from scans WHERE project = ?
     ORDER BY count''', self.projectNameVar.get())

    #Add every scan to the tree.
    if scans:
      uniqueReps = set([scan[1] for scan in scans])
      #CODE TO NEST SCANS UNDER REPS THAT EXPAND.
      for rep in uniqueReps:
        self.tree.insert('','end',rep,text=rep)
      for scan in scans:
        self.tree.insert(scan[1],'end',scan[0],
          values=(scan[2],scan[3],scan[4],scan[5]))

  def select_scans(self):
    #Takes selected scans from tree and adds them to the selected list.
    if self.tree.selection():
      #Add scans to selected lists)
      for selected in self.tree.selection():
        srep = self.tree.parent(selected)
        #Only scans will have a parent (the rep name).
        if srep and selected not in self.scanData.scanIds:
          #Add the scan's id to the list of scan ids.
          self.scanData.scanIds.append(selected)
          #Pull ou the information for each selection and add to the scans list.
          sproject = self.projectNameVar.get()
          item = self.tree.item(selected)
          scount = str(item['values'][2])
          sx = str(item['values'][0])
          sy = str(item['values'][1])
          stime = item['values'][3]

          #Add the selected scan info to the selected scan obj
          self.scanData.add({'id':selected,'project':sproject,'rep':srep,
            'count':scount,'x':sx,'y':sy,'time':stime})

          listtext = sproject+' #'+scount + ': ' + srep + ' (' + sx + ', '+sy+')'
          self.selectedListboxT2.insert(END,listtext)
          self.selectedListboxT3.insert(END,listtext)

  def remove_scans(self):
    #For now, only remove them from the list of selected scans.
    # In future, this function will remove from plot.
    rselected = self.selectedListboxT2.curselection()
    if rselected:
      for rs in rselected:
        self.scanData.remove(rs)
        self.selectedListboxT2.delete(rs)
        self.selectedListboxT3.delete(rs)

  def populate_metadata(self):
    #First, delete any existing text
    self.metaBox.config(state=NORMAL)
    self.metaBox.delete(0.0,END)
    #If there is a current selection, populate the metadata.
    if self.scanData.currentSelection is not None:
      #Now, format and add the metadata information.
      metatext = 'Project: {project} \nScan: {scan} \nRep: {rep}\n(X,Y): ({x},{y})\n'
      metatext +='Count: {count} \nAcquire Date and Time: {acquire_date} at UTC {time} \n'
      metatext +='Processing Date: {process_date} \nInstrument(s): {instrument} \n'
      metatext +='Number of Pixels: {pixels}'
      metatext = metatext.format(**self.scanData.selectedScans[self.scanData.currentSelection])
      self.metaBox.insert(0.0,metatext)
    self.metaBox.config(state=DISABLED)

  def on_exit():
    plt.close('all')
    root.quit()

#final lines (needed to make everything run)
root = Tk()
app(root)
root.protocol("WM_DELETE_WINDOW", app.on_exit)
root.mainloop()
