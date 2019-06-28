# -*- coding: utf-8 -*-

'''
main.py
~~~~~~~

This program get the data from GA api and insert these data to MariaDB
'''
import argparse
import json
import datetime

from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools


SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
CLIENT_SECRETS_PATH = 'client_secrets.json'
QUERY_STRING_PATH = 'query_string.json'
SEL_VIEWS = ['view1', 'view2', 'view3', 'view4', 'view5']


def initGaConn() -> object:
    '''
    Create connection with GA api. It would check the auth from "analyticsreporting.dat". If
    the credential is not valid, it would try to use "CLIENT_SECRETS" to connect the API and write
    the credential info to the "analyticsreporting.dat"
    '''

    flow = client.flow_from_clientsecrets(
        CLIENT_SECRETS_PATH, scope=SCOPES,
        message=tools.message_if_missing(CLIENT_SECRETS_PATH))

    storage = file.Storage('analyticsreporting.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage)
    http = credentials.authorize(http=httplib2.Http())

    analytics = build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)
    return analytics


def getQueryInsertString(vid: str, std: str, edd: str) -> tuple:
    '''
    Deal with the query string(GA) and insert string(MariaDB). It reads the data from "QUERY_STRING_PATH"
    and process the info to split the query string(GA) and insert string(MariaDB). If you need to add 
    new query, you need to edit the "QUERY_STRING_PATH" file and add the key to const variable "SEL_VIEWS"
    '''

    insert_list = list()
    query_list = list()
    with open(QUERY_STRING_PATH, 'r') as f:
        query_string = json.load(f)

    for view_name in SEL_VIEWS:
        # for inserting mariadb info
        insert_list.append(query_string[view_name]['insertString'])
        del query_string[view_name]['insertString']

        # add needed info for ge query
        query_string[view_name]['viewId'] = vid
        query_string[view_name]['dateRanges'] = [{'startDate': std, 'endDate': edd}]
        query_list.append(query_string[view_name])

    return (query_list, insert_list)

def procGaData(conn: object, qys: list) -> list:
    '''
    Process the response data from the GA api.
    ###  NOTICE - every reports limits 1000 rows data  ####
    '''
    raw_reports = conn.reports().batchGet(
        body={
            'reportRequests': qys
        }
    ).execute()

    proced_reports = list()
    for report in raw_reports.get('reports', []):
        tmp_rp = list()
        for row in report.get('data', {}).get('rows', []):
            dims = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])[0].get('values', [])
            tmp_rp.append(dims + dateRangeValues)
        print(len(tmp_rp))
        proced_reports.append(tmp_rp)
    return proced_reports

def procDataTimeRange(data: str) -> tuple:
    '''
    Deal with the DATE_TIME_RANGE and verify the datetime value
    '''
    try:
        st_date, ed_date = data.split("/")
        
        # verify format
        st = datetime.datetime.strptime(st_date, '%Y-%m-%d')
        ed = datetime.datetime.strptime(ed_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError('Got the WRONG Format "%s" ' % data + \
            'in DATE_TIME_RANGE, should be "YYYY-MM-DD/YYYY-MM-DD" (startDate/endDate)' )
    
    # verify datetime
    check_date = datetime.datetime.today() - datetime.timedelta(days=1)
    assert st < check_date, 'Start Date (%s) is not valid (must < today)' % st_date
    assert ed < check_date, 'End Date (%s) is not valid (must < today)' % ed_date
    assert st <= ed, 'DateRange is not valid ("Start Date" must <= "End Date")'

    return (st_date, ed_date)


def main():
    # get the GA website ID & datetime range
    parser = argparse.ArgumentParser(
        prog='ga2Mariadb',
        usage='python main.py {viewID: str} {datetime range: YYYY-MM-DD/YYYY-MM-DD (startDate/endDate)}',
        description='integrate mariaDB with GA data'
    )
    parser.add_argument('VIEW_ID', help='GA website ID', type=str)
    parser.add_argument('DATE_TIME_RANGE', help='select datetime range', type=str)
    
    VIEW_ID = parser.parse_args().VIEW_ID

    # deal with datetime
    DATE_TIME_RANGE = parser.parse_args().DATE_TIME_RANGE
    st_date, ed_date = procDataTimeRange(DATE_TIME_RANGE)

    # select and process the ga query string & maria insert string
    ga_qys, maria_its = getQueryInsertString(VIEW_ID, st_date, ed_date)

    
    # print(ga_qys)
    # print(maria_its)
    
    # GA data query
    ga_conn = initGaConn()
    res = procGaData(ga_conn, ga_qys)


    import pprint
    pprint.pprint(res)
    print(len(res))

if __name__ == "__main__":
    main()
