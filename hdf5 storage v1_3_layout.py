
 # -*- coding: utf-8 -*-
"""
Created on Sun Aug 27 20:06:08 2023

"""

"""
Python modules and packages
"""


import re
import random
import h5py


import numpy as np
#import matplotlib.pyplot as plt

#from matplotlib.figure import Figure
#from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox

import HEKA

"""
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Section 0A: GUI class
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
"""
class gui:       
    
    def __init__(self, tkwindow, text, width= 15, button_type=None, options=None, bind_event=None):
        self.var= tk.StringVar(tkwindow) #Initiating tkinter variable that can change during program run
        self.var.set('No input') #Setting initial value as "not selected yet"
        self.text= text #Text for label of metadata variable
        self.width= int(width)
        self.options= options #For method with options chosen from menu, list of all options in the menu
        self.label= tk.Label(tkwindow, text=self.text) #Initializing a label
        self.button_type= button_type
        self.button= self.create_button(button_type, tkwindow) #Initializing a button based on keyword "entry or "combobox"
        self.metabind= bind_event #Initialize a bind based on the binding trigger '<FocusIn>' or other
    
    def create_button(self, button, tkwindow):
            
        if button=="combobox":
            return ttk.Combobox(tkwindow, textvariable=self.var, width= self.width, values=self.options, state='normal')
            
        if button=="entry":
           return tk.Entry(tkwindow, textvariable= self.var, width= self.width)
        
        else:
            pass
       
    def value(self):
        return self.var.get()   
    
    def clear_entry(self, *event):
        self.var.set("")

class global_var():
    def __init__(self):
        
        self.data= []
        self.dict= {}
                                         
"""
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Section 0B: Root Tkinter interface
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
"""
Metadata= global_var()
preset_values= global_var()

with open('Preset.txt', 'r') as f: #(preparing to read the preset file)
    data= f.readlines() # File read where each line of the line is an element in the list for example data[0] is first line and data[-1] is last line
    for j in data:
        preset_values.data.append(j.split('\t')[0]) 
        
def update(all_metadata, tree):
    
   name=[]
   value=[]
    
   for item in tree.get_children():
       tree.delete(item) 
     
   for i in all_metadata:
       if i.value()!="No input":
           Metadata.data.append(i)
           name.append(i.text)
           value.append(i.value())                
           
   for i in range(len(name)):
       tree.insert('', tk.END, values=(name[i], value[i]))

def export(Metadata, data, notebook, notebook_header):
    hdf5file= 'testfile.hdf5' 
    answer= True
                         
    with h5py.File(hdf5file,'r') as f:
        for entry in f.keys():     
            if Metadata['Filename']==f[entry].attrs.get('Filename'):
                answer= messagebox.askyesno("WARNING!", "This file has already been registered are you sure you want to export the same file?")
                break    
            
            f.close()
            
    answer= messagebox.askyesno("WARNING!", "Are you sure you want to export data?")
    
    if answer:               
        with h5py.File(hdf5file,'a') as f:  
            metaData= f.create_group(Metadata['File ID'])
            dataDirectory= metaData.create_group('Data')
            notebookDirectory = metaData.create_group('Notebook')
                               
            for entry in Metadata[1:]:
                metaData.attrs[entry[0]]= entry[1]                
                        
            #This will get us the column we want.
            def getColumnData(seriesNumber,sweepNumber,columnNumber):
                newList=[]
                for n in range(len(data[seriesNumber][sweepNumber])):
                    newList.append(data[seriesNumber][sweepNumber][n][columnNumber])
                return newList
            
            #Next level is the Data -> Serie 1 and Notebook -> Serie 1
            for i in range(len(data)): #Series
                series=dataDirectory.create_group('Serie '+str(i))
                notebookSeries=notebookDirectory.create_group('Serie '+str(i)) #REDUNDANCY!
                for j in range(len(data[i])): #Sweep
                    for k in range(len(data[i][j][0])): #Columns
                        series.create_dataset('Sweep'+str(j)+'Column'+str(k),data=getColumnData(i,j,k))
                    for l in range(len(notebook[i][j])): #Notebook placements, I suppose just like columns.
                        series.attrs[notebook_header[0][l].strip()+str(j)] = notebook[i][j][l]
                        notebookSeries.attrs[notebook_header[0][l].strip()+str(j)] = notebook[i][j][l] #REDUNDANCY!
    
            messagebox.showinfo("INFORMATION", "Data successfully exported! \nThank you for your contribution to science!")            

def save(*event):
    saved_presetlist=[]
    answer= True
    with open('Preset.txt', 'r') as f: #(preparing to read the preset file)
        data= f.readlines() # File read where each line of the line is an element in the list for example data[0] is first line and data[-1] is last line
        for j in data:
            saved_presetlist.append(j.split('\t')[0]) 
                       
    for i in saved_presetlist:
        if i==save_preset.value():
            answer= messagebox.askyesno("WARNING!", "The preset already exist! Overwrite this preset ?")
    
    if answer:
        new_preset=[save_preset.value()]  
        preset_values.data.append(save_preset.value())
        save_preset.button['values']=preset_values.data
        load_preset.button['values']=preset_values.data
            
        for i in Metadata.data[6:]:    
            new_preset.append(i.text)
            new_preset.append(str(i.value()))
        new_preset.append("\n")
        preset_string= '\t'.join(new_preset)
        
        with open('Preset.txt', 'a') as f:
            f.writelines(preset_string)    
 
def load(*event):
    with open('Preset.txt', 'r') as f:
        data= f.readlines() # File read where each line of the line is an element in the list for example data[0] is first line and data[-1] is last line
        
        for j in data:
            if j.split('\t')[0]== load_preset.value():
                preset_data= j.split('\t')
                
        if preset_data:
            for i in range(1,len(preset_data)-1,2):
                Metadata.dict[preset_data[i]].var.set(preset_data[i+1])
                              
    
#Creating the export_main window
root= tk.Tk()
root.title("Data repository")
#root.wm_iconbitmap('Mauzeroll logo.ico')
root.geometry('1600x1200+50+50')

file_frame= ttk.Frame(root); file_frame.place(relx=0.005, rely=0.005, relwidth= 0.5)
file_frame1= ttk.Frame(file_frame); file_frame1.pack(fill=tk.X)
file_frame2= ttk.Frame(file_frame); file_frame2.pack(fill=tk.X)

input_frame= ttk.Frame(root); input_frame.place(relx=0.005, rely=0.07, relwidth= 0.25, relheight= 0.25)
input_frame1= ttk.Frame(input_frame); input_frame1.pack(fill=tk.X)
input_frame2= ttk.Frame(input_frame); input_frame2.pack(fill=tk.X)
input_frame3= ttk.Frame(input_frame); input_frame3.pack(fill=tk.X)
input_label= ttk.Label(input_frame1, text="Input metadata and update before exporting", font=('URW Gothic L','10', 'bold')); input_label.pack(side=tk.LEFT)
blank_label= ttk.Label(input_frame2, text="                             ", font=('URW Gothic L','9', 'bold')); blank_label.pack(side=tk.LEFT)
load_label= ttk.Label(input_frame2, text="   Load preset   ", font=('URW Gothic L','9', 'bold')); load_label.pack(side=tk.LEFT)
save_label= ttk.Label(input_frame2, text="   Save preset   ", font=('URW Gothic L','9', 'bold')); save_label.pack(side=tk.LEFT)

Update_button= tk.Button(input_frame3, text=" Update ", width=12, relief=tk.RAISED)
Update_button.pack(side=tk.LEFT)

load_preset= gui(input_frame3, "Load preset", button_type="combobox", options= preset_values.data); load_preset.button.pack(side=tk.LEFT)
save_preset= gui(input_frame3, "Save preset", button_type="combobox", options= preset_values.data); save_preset.button.pack(side=tk.LEFT)
save_preset.button.bind("<Return>", save)
load_preset.button.bind("<Return>", load)

Export_button= tk.Button(root, text="Export data", width=10, relief=tk.RAISED)
Export_button.place(x=110, y=60, width= 100)

metadata_notebook= ttk.Notebook(root); metadata_notebook.place(x=10, y=150)
metadata_frame= ttk.Frame(root); metadata_frame.place(x=360, y=120, width= 400, height=400)

tab1_frame= ttk.Frame(metadata_notebook, width=350, height=400); tab1_frame.place(x=10, y=10)
tab2_frame= ttk.Frame(metadata_notebook, width=350, height=400); tab2_frame.place(x=10, y=10)
tab3_frame= ttk.Frame(metadata_notebook, width=350, height=400); tab3_frame.place(x=10, y=10)
tab4_frame= ttk.Frame(metadata_notebook, width=350, height=400); tab3_frame.place(x=10, y=10)
metadata_notebook.add(tab1_frame, text='General Echem')
metadata_notebook.add(tab2_frame, text='Battery')
metadata_notebook.add(tab3_frame, text='EIS')
metadata_notebook.add(tab4_frame, text='Other')

"""
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Section 1: File reading
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
"""
# [1.1] Variables
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
filename= gui(root, "Name of file for Trace")
filepath= gui(root, "Full file path")

# [1.2] Functions
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
label1= tk.Label(file_frame1, text="Select the file to export", font=('URW Gothic L','10', 'bold')); label1.pack(side= tk.LEFT)
filebrowser= tk.Button(file_frame2, text="  Browse file  ", relief=tk.RAISED, command= lambda: file_read()); filebrowser.pack(side= tk.LEFT)
filebrowser_label= tk.Label(file_frame2, textvariable= filename.var, width=60, bg="white", relief=tk.SUNKEN); filebrowser_label.pack(side= tk.LEFT)

#label2= tk.Label(root, text="Message box", font=('URW Gothic L','10', 'bold')); label2.place(relx=0.055, rely=0.0275, relwidth=0.3, relheight=line_h)
#text1= tk.Text(root, height=4); text1.place(relx=0.055, rely=0.0275, relwidth=0.3, relheight=0.02)

def file_read():
       
    file= fd.askopenfilenames(title= "Select data file", initialdir='/', filetypes=[('Data files', '*.txt'), ('Data files', '*.asc')])  
    
    if file:      
        filepath.var.set(file[0])
        filename.var.set(file[0].split('/')[-1])
    
    with open(filepath.value(), 'r') as f:
        raw_data= f.readlines()
          
    if re.search('EC-Lab', raw_data[0]):
        print("biologic file")
    
    elif re.search('Series', raw_data[0]):
        data, notebook, notebook_header, date, map_XY= HEKA.read(raw_data)
        letters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' 
        fid.var.set(f"HEKA_{date[1:5]}_{random.choice(letters)}{random.randint(1,9999)}")
        fn.var.set(filename.value())
        dtype.var.set('HEKA')
        nheader.var.set(notebook_header)
        exp_date.var.set(date)
        mdim.var.set(f'Number of points: {len(map_XY[0])-1} X {len(map_XY[1])-1} - Dimensions: {np.max(map_XY[0])} um X {np.max(map_XY[1])} um')     
        
        Update_button.configure(command= lambda: update(all_metadata, metadata_tree))
        Export_button.configure(command= lambda: export(Metadata.dict, data, notebook, notebook_header))
        
    else:
        print("other type of file")

     
# [1.3] Buttons and labels
#----------------------------------------------------------------------------------------------------------------------------------------------------------------

"""
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Section 2: Metadata input
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
""" 

# [2.1] Variables
#----------------------------------------------------------------------------------------------------------------------------------------------------------------

# [2.1.2] metadata input variable
fid= gui(root, "File ID")
fn= gui(root, "Filename")
dtype= gui(root, "Datatype")
nheader= gui(root, "Notebook header")
exp_date= gui(root, "Date of experiment")
mdim= gui(root, "Map dimension")

op= gui(tab1_frame, "Author of experiment", button_type="entry")
tech= gui(tab1_frame, "Measurement technique", button_type="entry")
project= gui(tab1_frame, "Project", button_type="entry")
inst= gui(tab1_frame, "Instrument used", button_type="entry")
sample= gui(tab1_frame, "Sample", button_type="entry")
electrolyte= gui(tab1_frame, "Electrolyte", button_type="entry")
mediator= gui(tab1_frame, "Redox mediator", button_type="entry")
ref= gui(tab1_frame, "Reference electrode", button_type="entry")
appmethod= gui(tab1_frame, "Approach method", button_type="entry")
rcap= gui(tab1_frame, "Electrode radius", button_type="entry", bind_event='<FocusIn>') 
cat= gui(tab2_frame, "Cathode material", button_type="entry")
an= gui(tab2_frame, "Anode material", button_type="entry")
m_cat= gui(tab2_frame, "Mass of cathode", button_type="entry")
m_an= gui(tab2_frame, "Mass of anode", button_type="entry")
sep= gui(tab2_frame, "Separator", button_type="entry")
cell_type= gui(tab2_frame, "Type of cell", button_type="entry")
comment= gui(tab1_frame, "Additional info", button_type="entry")
amp= gui(tab3_frame, "Amplitude", button_type="entry")
app= gui(tab3_frame, "Applied potential", button_type="entry")
freq= gui(tab3_frame, "Frequency", button_type="entry")

fixed_metadata= [fid, fn, dtype, nheader, exp_date, mdim]
general_metadata= [op, tech, project, inst, sample, electrolyte, mediator, ref, appmethod, rcap, comment]
battery_metadata= [cat, an, m_cat, m_an, sep, cell_type]
EIS_metadata= [amp, app, freq]
all_metadata= fixed_metadata+general_metadata+battery_metadata+EIS_metadata

for n in all_metadata:
    Metadata.dict[n.text]=n

for i,j in enumerate(general_metadata):
    j.label.place(x=10, y=10+i*25, width=150, height= 20)
    j.button.place(x=170, y=10+i*25, width=150, height= 20)

for i,j in enumerate(battery_metadata):
    j.label.place(x=10, y=10+i*25, width=150, height= 20)
    j.button.place(x=170, y=10+i*25, width=150, height= 20)  

for i,j in enumerate(EIS_metadata):
    j.label.place(x=10, y=10+i*25, width=150, height= 20)
    j.button.place(x=170, y=10+i*25, width=150, height= 20) 

# [2.1.3] metadata view
column= ['Metadata', 'Value']
y_scrollbar= ttk.Scrollbar(metadata_frame, orient='vertical'); y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
x_scrollbar= ttk.Scrollbar(metadata_frame, orient='horizontal'); x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
metadata_tree= ttk.Treeview(metadata_frame, columns= column, show='headings', selectmode='browse',  yscrollcommand= y_scrollbar, xscrollcommand= x_scrollbar)
metadata_tree.pack()
y_scrollbar.config(command=metadata_tree.yview)
x_scrollbar.config(command=metadata_tree.xview)
metadata_tree.heading('Metadata', text='Metadata')
metadata_tree.heading('Value', text='Value')

metadata_tree.column('Metadata', anchor=tk.W, width=150)
metadata_tree.column('Value', anchor=tk.W, width=600)


# [2.2] Functions
#----------------------------------------------------------------------------------------------------------------------------------------------------------------

      
           
root.mainloop()
