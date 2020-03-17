This is the Service used to query the Historian database every X seconds.
-------------------------------------------------------------------------

This program make request to historian servers in order to get all raw values in almost real time.
The data are writen locally then uploaded to hadoop cluster via SFTP.

This service can be launch with different options :

```
 -mode [options]    : Service mode
     DAEMON: service extracting every data from historian each X seconds
     STATUS: gives information about extraction succeeded and intervals lack
     RETRIEVE: run the extraction between two date/time retrieving missing intervals
     FILE_TRANSFER: transfer data files produced between two date/time
     USAGE: display the launching options
 -start <date>      : Start of date/time range for extracting missing data or transferring missing data files
                      (in RETRIEVE or FILE_TRANSFER mode)
                      Format : yyyy-MM-dd HH:mm (for example : 2019-02-20 10:00)
 -end <date>        : End of date/time range for extracting missing data or transferring missing data files
                      (in RETRIEVE or FILE_TRANSFER mode)
 -force             : Force the treatment for extracting data or transferring files (in RETRIEVE or
                      FILE_TRANSFER mode)
```

The configuration is stored in YML file : `application.yml`

The content of the file :
