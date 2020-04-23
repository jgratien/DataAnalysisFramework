import pandas as pd
import os
import io
import glob
from xlwt import Workbook

def fixFiles(path,path_destination):
    all_files =  glob.glob(os.path.join(path,"*.xls"))
    lf = []
    lh = []
    xldoc = Workbook()
    sheet = xldoc.add_sheet("Sheet1", cell_overwrite_ok=True)
    for index,filename in enumerate(all_files,start=0):
        print(index,filename)
        file = io.open(filename, "r", encoding="latin-1")
        data=file.readlines()
        lh.append(data[0:10])
        del data[0:10]
        lf.append(data)
        for i, row in enumerate(data):
    # Two things are done here
    # Removeing the '\n' which comes while reading the file using io.open
    # Getting the values after splitting using '\t'
            for j, val in enumerate(row.replace('\n', '').split('\t')):
                sheet.write(i, j, val)
        filePath = path_destination  + r'/myexcel_'+str(index)+'.xls'
        xldoc.save(filePath)
    return lh

def readFiles(path):
    all_files =  glob.glob(os.path.join(path,"*.xls"))
    lf = []
    for file in all_files:
        print("READ",file)
        data = pd.read_excel(file)
        lf.append(data)
    return lf

def convertFiles(data,head,path_destination):
    print("CONVERT")
    for i,file in enumerate(data,start=0):
        print(" F[",i,"]")
        file.columns = head
        path = path_destination + r'/myTestCsv_'+str(i)+'.csv'
        file.to_csv(path,index=False)
        
if __name__ == "__main__":
    path_origin = r'/work/irlin355_1/gratienj/BigData/DigitalSandBox/Data/TimeSeries/Lacq/Jour_1'
    path_destination = r'/work/irlin355_1/gratienj/BigData/DigitalSandBox/Data/TimeSeries/Lacq/Jour_1_DT'
    lh=fixFiles(path_origin,path_destination)
    test=readFiles(path_destination)
    head=lh[0][9].replace('\n','').split('\t')
    print(head)
    convertFiles(test,head,path_destination)