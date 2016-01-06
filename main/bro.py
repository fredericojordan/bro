'''
Created on 16 de dez de 2015

@author: fvj
'''
import wgparser
import ranker
import calendar_api

location_id = 105160 # Florianopolis - SC
surf_calendar_id = "4hr9aa7gviqe7pems3dj5hhb18@group.calendar.google.com" # Surf calendar
primary_calendar_id = 'primary'

page_root = 'http://www.windguru.cz/pt/index.php?sc='
forecast = wgparser.get_forecast(page_root + str(location_id))

best_day = ranker.get_best(forecast)
calendar_api.create_event(surf_calendar_id, best_day)