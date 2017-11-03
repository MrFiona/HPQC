#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-09-26 15:34
# Author  : MrFiona
# File    : hpqc_create_operation.py
# Software: PyCharm Community Edition


import os
import time
import json
import urllib2
from hpqc_common_func import url_access_error_decorator

import socket

socket.timeout(100)



# todo 创建test-set-folders
@url_access_error_decorator('create_test_set_folders')
#todo 增加控制错误输出标记位 print_error 默认打印错误信息
def create_test_set_folders(session, test_set_folders_name, project_id, json_name, program_name, print_error=True):
    url = r'%s/qcbin/rest/domains/dcg/projects/bkc/test-set-folders' % (session.host)
    cookiestring = r'LWSSO_COOKIE_KEY=%s;QCSession=%s;XSRF-TOKEN=%s;Path=/' % \
                   (session.token,
                    session.cookies[r'QCSession'],
                    session.cookies[r'XSRF-TOKEN'])
    req_headers = {r'Cookie': cookiestring, r'Accept': r'application/json'}
    # todo 注意:当hierarchical-path 的值为空是则无法移动至其子目录下, 但是可以移动至上级目录，例如此例为2736父目录为NFVi项目目录，可以移动至Root目录下
    # todo 而且永远只能往上级目录移动！！！！但是不可以移动至项目子目录下
    data = '''{"Fields":[{"Name":"name","values":[{"value":"%s"}]},
                         {"Name": "parent-id", "values": [{"value": "%d"}]},
                         {"Name": "hierarchical-path", "values": [{"value": "AAAAAEAB"}]}
        ]}''' % (test_set_folders_name, project_id)

    req = urllib2.Request(url, data=data, headers=req_headers)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req)
    json_data = json.load(response)

    if not os.path.exists('create_test_folders_' + program_name):
        os.makedirs('create_test_folders_' + program_name)

    with open('create_test_folders_' + program_name + os.sep + json_name + '_json_data.json', 'wb') as p:
        json.dump(json_data, p, sort_keys=True, indent=4)


# todo 创建test-set
@url_access_error_decorator('create_test_set')
def create_test_set(session, test_set_name, project_id, json_name, program_name, print_error=True):
    url = r'%s/qcbin/rest/domains/dcg/projects/bkc/test-sets' % (session.host)
    cookiestring = r'LWSSO_COOKIE_KEY=%s;QCSession=%s;XSRF-TOKEN=%s;Path=/' % \
                   (session.token,
                    session.cookies[r'QCSession'],
                    session.cookies[r'XSRF-TOKEN'])
    req_headers = {r'Cookie': cookiestring, r'Accept': r'application/json'}
    data = '''{"Fields":[
                        {"Name": "status", "values": [{"value": "Open"}]},
                        {"Name": "name", "values": [{"value": "%s"}]},
                        {"Name": "subtype-id", "values": [{"value": "hp.qc.test-set.default"}]},
                        {"Name": "parent-id", "values": [{"value": "%d"}]},
                        {"Name": "open-date", "values": [{"value": "%s"}]}
                        ],"Type":"test-set"}''' % (test_set_name, project_id, time.strftime('%Y-%m-%d', time.localtime(time.time())))

    req = urllib2.Request(url, data=data, headers=req_headers)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req)
    json_data = json.load(response)

    if not os.path.exists('create_test_set_' + program_name):
        os.makedirs('create_test_set_' + program_name)

    with open('create_test_set_' + program_name + os.sep + json_name + '_' + str(project_id) + '_json_data.json', 'wb') as p:
        print 'create!!!!'
        json.dump(json_data, p, sort_keys=True, indent=4)



@url_access_error_decorator('create_test_instance')
def create_test_instance_json(case_info, session, print_error=True):
    # try:
        url = r'%s/qcbin/rest/domains/dcg/projects/bkc/test-instances' % (session.host)
        cookiestring = r'LWSSO_COOKIE_KEY=%s;QCSession=%s;XSRF-TOKEN=%s;Path=/' % \
                       (session.token,
                        session.cookies[r'QCSession'],
                        session.cookies[r'XSRF-TOKEN'])
        req_headers = {r'Cookie': cookiestring, r'Accept': r'application/json'}
        data = '''{"Fields":[{"Name":"status","values":[{"value":"%s"}]},
                             {"Name":"iterations","values":[{"value":"%s"}]},
                             {"Name":"user-01","values":[{"value":"%s"}]},
                             {"Name":"user-04","values":[{"value":"%s"}]},
                             {"Name":"user-03","values":[{"value":"%s"}]},
                             {"Name":"exec-date","values":[{"value":"%s"}]},
                             {"Name":"cycle-id","values":[{"value":"%s"}]},
                             {"Name":"test-id","values":[{"value":"%s"}]},
                             {"Name":"exec-time", "values": [{"value": "%s"}]},
                             {"Name":"subtype-id","values":[{"value":"hp.qc.test-instance.MANUAL"}]},
                             {"Name":"test-order","values":[{"value":"%s"}]}],"Type":"test-instance"}'''%\
                            (case_info['status'],
                             case_info['iterations'],
                             case_info['hsd_id'],
                             case_info['unit'],
                             case_info['value'],
                             case_info['exec_date'],
                             case_info['test_set_id'],
                             case_info['test_case_id'],
                             case_info['exec-time'],
                             case_info['test_case_order'])

        req = urllib2.Request(url, data=data, headers=req_headers)
        req.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(req)




if __name__ == '__main__':
    import time
    from create_session import Session
    from hpqc_query import HPQCQuery

    start = time.time()
    host = r'https://hpalm.intel.com'
    session = Session(host, 'pengzh5x', 'QQ@08061635')
    query = HPQCQuery('DCG', 'BKC')
    # NFVi 2736
    # (5013, u'MrFiona_test_folders')
    # todo project_id为0时代表root根目录
    # create_test_set_folders(session, 'test_create_set_folders_116' ,0, 'test_create_set_folders_116', 'root', print_error=False)
    # create_test_set(session, '21231' ,5013, 'ddd', 'ttt', print_error=True)
    case_info = {'status': 'Passed',
                 'exec_date': time.strftime('%Y-%m-%d', time.localtime(time.time())),
                 'exec-time':time.strftime('%H-%M-%S', time.localtime(time.time())),
                 'test_set_id': '17709',
                 'test_case_id': '20180',
                 'test_case_order': '1',
                 'iterations':'1',
                 'hsd_id':'',
                 'unit':'',
                 'value':''}
    create_test_instance_json(case_info, session)
