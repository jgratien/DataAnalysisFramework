import requests
import json

url = 'http://sensors.ifpen.fr/'
def fromAPI(start,end,tags):
    # CALCULATED_DATA : interpolation from historian. It uses "interval" value
    mydata = {'server':'ISNTS35-N','type':'CALCULATED_DATA','tags':tags,'start':start,'end':end,'numberOfSamples':None,'qualifiedValues':True,"interval":600}
    # RAW_DATA : raw data. It uses "numberOfSample to limit output array size. If set to "none" retrieve all values between start and en dates. "interval" is not used but required
    mydata = {'server':'ISNTS35-N','type':'RAW_DATA','tags':tags,'start':start,'end':end,'numberOfSamples':1000,'qualifiedValues':True,"interval":None}
    s = json.dumps(mydata)
    r2 = requests.post(url, data=s)
    parsed = json.loads(r2._content)
    return parsed

def writeToCSV(jsonContent,cvsFile):
    forecast = jsonContent['values']
    with open(cvsFile,"w") as myCSV:
        myStr = ''
        for k in jsonContent['headers']:
            myStr+=k+';'
        myCSV.write(myStr[:-1]+'\n')
        for f in forecast:
            myStr=str(f[0]).replace('T', ' ')+';'
            for i in range(1,len(f)):
                myStr+=str(f[i]['value'])+';'
            myCSV.write(myStr[:-1]+'\n')
    myCSV.close()

if __name__ == "__main__":
    start = '2019-06-01 00:00:00'
    end = '2019-06-25 00:00:00'
    # Some example of tags
    tags = ['METEO.CENTRALE_METEO.MET_temperature','METEO.CENTRALE_METEO.MET_sunshine','METEO.CENTRALE_METEO.MET_humidity']
    tags = ['CRY.CENTRALE_SOLAIRE.CRY_act_prod_pow','CRY.TGBT_NORMAL.CRY_act_cons_pow','LAU.PHOTOVOLTAIQUE.LAU_app_prod_pow']
    mycsvFile = "C:/Temp/historianPower-Meteo-CRY.csv"
    print(json.dumps(fromAPI(start,end,tags), indent=4, sort_keys=True))
#     writeToCSV(fromAPI(start,end,tags), mycsvFile)