import kairosdb
import numpy as np

KDB_CLIENT = kairosdb.client.KairosDBAPIClient(api_endpoint="http://islin-hdpmas1.ifp.fr:8888/api/v1")
KDB_API = kairosdb.KairosDBAPI(KDB_CLIENT)

def exportToCSV():
    print(KDB_API.metricnames)
    requestJSON = {
        "metrics": [{
            "name": "rotorSpeed",
            "aggregators": [{
                "name": "avg",
                "align_sampling": True,
                "sampling": {"value": 1, "unit": "minutes"}
            }]
        },
            {"name": "anemometerSpeed",
            "aggregators": [{
                "name": "avg",
                "align_sampling": True,
                "sampling": {"value": 1, "unit": "minutes"}
            }]
        },
            {"name": "activePower",
            "aggregators": [{
                "name": "avg",
                "align_sampling": True,
                "sampling": {"value": 1, "unit": "minutes"}
            }]
        },
            {"name": "calculatedCP",
            "aggregators": [{
                "name": "avg",
                "align_sampling": True,
                "sampling": {"value": 1, "unit": "minutes"}
            }]
        },
            {"name": "calculatedLambda",
            "aggregators": [{
                "name": "avg",
                "align_sampling": True,
                "sampling": {"value": 1, "unit": "minutes"}
            }]
        },
            {"name": "calculatedTheta",
            "aggregators": [{
                "name": "avg",
                "align_sampling": True,
                "sampling": {"value": 1, "unit": "minutes"}
            }]
        }],
        "cache_time": 0,
        "start_relative": {"value": "2", "unit": "years"},
        "end_relative" :{"value": "1", "unit": "years"}
        }
#     start_absolute : The start time in milliseconds
#     end_absolute : The end time in milliseconds
    toExport = {}
    result = KDB_API.query_metrics(requestJSON)
    timestampValues = None
    for k in range(6):
        y=result['queries'][k]['results'][0]['values']
        zzz = np.matrix(y)
        y = zzz[:,1].A1
        t = zzz[:,0].A1.astype(np.int_)
        metricName = str(result['queries'][k]['results'][0]['name'])
        print(k,metricName)
        toExport[metricName] = y
        timestampValues = t
        print(np.min(y))
        print(np.max(y))
        print(np.min(t))
        print(np.max(t))
        print
# Export to CSV
    with open('C:/Temp/ExportKairos.csv','w') as csv_file:
        aLine='timestamp (ms)'
        for s in toExport:
            aLine=aLine+';'+s
        csv_file.write(aLine+'\n')
        for i in range(len(timestampValues)):
            aLine = str(timestampValues[i])
            for s in toExport:
                aLine=aLine+';'+str(toExport[s][i])
            if toExport['activePower'][i]<0:
                print(aLine)
            csv_file.write(aLine+'\n')
if __name__=="__main__":
    exportToCSV()


