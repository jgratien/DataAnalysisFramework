import pandas as pd
import os
import io
import glob
from xlwt import Workbook

def fixFiles(path):
    all_files =  glob.glob(os.path.join(path,"*.xls"))
    lf = []
    lh = []
    xldoc = Workbook()
    sheet = xldoc.add_sheet("Sheet1", cell_overwrite_ok=True)
    for index,filename in enumerate(all_files,start=0):
        print(filename)
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
        filePath= path + r'/myexcel_'+str(index)+'.xls'
        xldoc.save(filePath)
    return lh

def readFiles(path):
    all_files =  glob.glob(os.path.join(path,"*.xls"))
    lf = []
    for file in all_files:
        data = pd.read_excel(file)
        lf.append(data)
    return lf

def convertFiles(data,head,path_destination):
    for i,file in enumerate(data,start=0):
        file.columns = head
        path = path_destination + r'/myTestCsv_'+str(i)+'.csv'
        file.to_csv(path,index=False)
        
if __name__ == "__main__":
    path_origin = r'/home/ymo/local/work-ref/data/Lacq/jour_1'
    lh=fixFiles(path_origin)
    path_destination = r'/home/ymo/local/work-ref/data/Lacq/jour_1_DT'
    test=readFiles(path_destination)
    head=lh[0][9].replace('\n','').split('\t')
    convertFiles(test,head,path_destination)