from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import wgparser
import time

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Surf Bro'
FULL_DAY = False


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')

    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'bro-calendar-python.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        #else: # Needed only for compatibility with Python 2.6
        #    credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_surf_date(day_forecast):
    initial_date = time.localtime(day_forecast[wgparser.initial_timestamp])

    initial_date_writable = list(initial_date)
    
    # corrects date if month changes
    if initial_date.tm_mday > float(day_forecast[wgparser.day]):
        if initial_date_writable[1] == 12:
            initial_date_writable[1] = 1
            initial_date_writable[0] += 1
        else:
            initial_date_writable[1] += 1

    initial_date_writable[2] = int(day_forecast[wgparser.day])
    initial_date_writable[3] = int(day_forecast[wgparser.hour])
            
    return time.struct_time(tuple(initial_date_writable))
    

def create_event(calendar_id, day_forecast):    
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    surf_date = get_surf_date(day_forecast)

    if FULL_DAY:
        start = {
                 'date': "{0:04.0f}-{1:02.0f}-{2:02.0f}".format(float(surf_date.tm_year),
                                                                float(surf_date.tm_mon),
                                                                float(surf_date.tm_mday)),
                }
        end = {
               'date': "{0:04.0f}-{1:02.0f}-{2:02.0f}".format(float(surf_date.tm_year),
                                                              float(surf_date.tm_mon),
                                                              float(surf_date.tm_mday)),
              }
    else:
        start = {
                 'dateTime': "{0:04.0f}-{1:02.0f}-{2:2.0f}T{3:2.0f}:00:00".format(float(surf_date.tm_year),
                                                                                  float(surf_date.tm_mon),
                                                                                  float(surf_date.tm_mday),
                                                                                  float(surf_date.tm_hour)),
                 'timeZone': day_forecast[wgparser.timezone_id].replace('\\',''),
                }
        end = {
                 'dateTime': "{0:04.0f}-{1:02.0f}-{2:2.0f}T{3:2.0f}:00:00".format(float(surf_date.tm_year),
                                                                                  float(surf_date.tm_mon),
                                                                                  float(surf_date.tm_mday),
                                                                                  float(surf_date.tm_hour)+3),
               'timeZone': day_forecast[wgparser.timezone_id].replace('\\',''),
              }
        
    summary = 'Bro, let\'s surf! ({0}m, {1:.0f}kn {2}, {3:.0f}{4}C)'.format(day_forecast[wgparser.wave_height],
                                                                            float(day_forecast[wgparser.wind_speed]),
                                                                            wgparser.get_wind_dir(day_forecast[wgparser.wind_direction]),
                                                                            float(day_forecast[wgparser.temperature]),
                                                                            u"\u00b0".encode("utf-8"))
    
    description = 'Your surf bro says that you should go surfing!\
    \n{0}h forecast: {1} m waves, {2} knots wind ({3}), {4} {5}C'.format(day_forecast[wgparser.hour],
                                                                   day_forecast[wgparser.wave_height],
                                                                   day_forecast[wgparser.wind_speed],
                                                                   wgparser.get_wind_dir(day_forecast[wgparser.wind_direction]),
                                                                   day_forecast[wgparser.temperature],
                                                                   u"\u00b0".encode("utf-8"))
    
    event = {
             'summary': summary,
             'location': u'Florian\u00F3polis, SC, Brazil'.encode("utf-8"),
             'description': description,
             'start': start,
             'end': end,
             'reminders': {
                           'useDefault': False,
                           'overrides': [
                                         {'method': 'popup', 'minutes': 24*60},
                                         ],
                           },
             }

    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print('Event created day {0}:\n{1}'.format(day_forecast[wgparser.day], event.get('htmlLink')))
    