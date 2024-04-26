# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 11:38:11 2024

@author: Danny
"""
import re
import numpy as np

def read(raw_data):
        
    separated_data=[] 
    
    if len(raw_data[1].split(' '))>1:
        separator= ' '
    if len(raw_data[1].split('\t'))>1:
        separator= '\t'
    if len(raw_data[1].split(','))>1:
        separator= ','
        
    for i in raw_data:       
        separated_data.append(i.split(separator))
        
    data=[]
    data_serie=[] #Temporary container for storing "series_data" that will be appended to the "master_data" and reset after a serie is completed
    data_sweep=[]  #Temporary container for storing "sweep_data" that will be appended to the "seies_data" and reset after a serie is completed
    data_line=[]
    
    notebook=[]
    notebook_line=[]
    notebook_header=[] #Permanent storage of notebook header to identify notebook data
    notebook_sweep=[]
    
    sweep_tracker=0 #Tracker for storing a data entry in the "sweep_data"
    notebook_tracker=0 #Tracker for storing a data entry in the "notebook_data"
    
    # Other variables 
    technique=[] # [Important] Store the technique for a measurement 
    blank_counter=[] #Serves to count the number of blank lines
    X_serie=[]
    X=[]
    Y=[]
    Y_serie=[]
      
    temp_date= separated_data[1][3]
    date= temp_date[0:11]     
    
    for line in separated_data: #Going through the HEKA file stored in data line per line
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------   
        """      
        This subsection is just to find gap in the data and give a preventive error message
        This is not necessary, but very helpful in debugging issues especially if the error stems from anomaly in dataset rather than the code itself
        """  
        if line[0]=='\n':
            blank_counter=blank_counter+1
            if blank_counter>2:
                print("blank line in data")
                break
     
        if line[0]!='\n':
            blank_counter=0
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    #Identifying a sweep header means two thing we just started a new serie or we ended a sweep and start a new sweep         
        if re.search('Sweep_', line[0]): 
            sweep_tracker=1 #If we identify a "Sweep" then we activate the "sweep_tracker"
            notebook_tracker=0
                          
        if re.search('Sweep #', line[0]):
            if len(notebook_header)<1:
                notebook_header.append(line)              
    
    # Identifying a " " means a data entry from a sweep or the notebook 
        if re.search(' ', line[0][0]):
            if sweep_tracker==1: # if its a sweep then we append to 'sweep_data'
                for element in line:
                    data_line.append(float(element))
                
                data_sweep.append(data_line)
                data_line=[]
                              
            if notebook_tracker==1: # if its a notebook then we append to 'notebook_data'
                for element in line[:-1]:
                    
                    if element[-1]=="m":
                        notebook_line.append(float(element[:-1])*1e-3)
                    if element[-1]=="µ":
                        notebook_line.append(float(element[:-2])*1e-6)
                    if element[-1]=="n":
                        notebook_line.append(float(element[:-1])*1e-9)
                    if re.search("[0-9]", element[-1]):
                        notebook_line.append(float(element))
                    if re.search("NAN", element):
                        notebook_line.append("NAN")           
                
                if line[-1][-2]=="m":
                    notebook_line.append(float(line[-1][:-2])*1e-3)
                if line[-1][-2]=="µ":
                    notebook_line.append(float(line[-1][:-3])*1e-6)
                if line[-1][-2]=="n":
                    notebook_line.append(float(line[-1][:-2])*1e-9)  
                if re.search("[0-9]", line[-1][-2]):
                    notebook_line.append(float(line[-1][:-1]))
                if re.search("NAN", line[-1]):
                    notebook_line.append("NAN")
                    
                notebook_sweep.append(notebook_line)
                notebook_line=[]
                
    # Identifying a line skip (\n) as the first element always mean end of a sweep and the start of a new sweep           
        if re.search('\n', line[0]):
            
            if len(data_sweep)>0:
                data_serie.append(data_sweep) #Since we are starting the notebook section that means we reached the end of a sweep then we need to append the 'sweep_data' to the 'serie_data'
                data_sweep=[] # Clear out for new sweep   
                sweep_tracker=0 #If we identify a "Sweep" then we activate the "sweep_tracker"
                notebook_tracker=1
                       
            if len(notebook_sweep)>0: # If it's the end of a sweep and the
                data.append(data_serie)
                data_serie=[] # Clear out for new serie
                notebook.append(notebook_sweep)
                notebook_sweep=[]    
                
    notebook_header= notebook_header[0]       
    
    header_i= {'x':'', 'y':'', 'z':'', 'scanrate':''}
    technique= []
    
    for i,j in enumerate(notebook_header):
        if re.search("X-pos", j):
            header_i['x']= i
            
        if re.search("Y-pos", j):
            header_i['y']= i
            
        if re.search("Z-pos", j):
            header_i['z']= i
            
        if re.search("Rate", j):
            header_i['scanrate']= i
        
    for i in notebook:
        for j in i:
            X_serie.append((np.round(float(j[header_i['x']])*1e6,2)))
            Y_serie.append((np.round(float(j[header_i['y']])*1e6,2)))
        X.append(X_serie)
        X_serie=[]
        Y.append(Y_serie)
        Y_serie=[]    
    X= np.round(X-np.min(X),0)
    Y= np.round(Y-np.min(Y),0)  
    map_XY= [np.unique(X),np.unique(Y)]

    return data, notebook, notebook_header, date, map_XY
    

            