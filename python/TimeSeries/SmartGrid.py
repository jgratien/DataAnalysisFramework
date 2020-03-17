#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 09:46:08 2019

@author: gratienj
"""
import json
import datetime
import ephem

site = ephem.Observer()
#site.lon = ''
#site.lat = ''
#site.elevation = 0
site = ephem.city('Lyon')

def analyzeLog(v):
    l = json.loads(v)
    date_str = l['date']
    date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    year = date.year
    month=date.month
    day=date.day
    site.date = str(year)+'/'+str(month)+'/'+str(day)
    sun = ephem.Sun()
    sunrise_date = ephem.localtime(site.next_rising(sun))
    sunset_date = ephem.localtime(site.next_setting(sun))
    t=int(round(date.timestamp()))
    v = l['value']
    if date>sunrise_date and date < sunset_date:  
        return (t,v)
    else:
        return (t,0.0)