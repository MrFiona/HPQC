#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-09-06 15:51
# Author  : MrFiona
# File    : create_test_set_folders.py
# Software: PyCharm Community Edition


import urllib2
from urllib2 import URLError




# todo 创建test-set-folders
def create_pnp_test_set(session, test_set_name, project_id):
    try:
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
            ]}''' % (test_set_name, project_id)

        req = urllib2.Request(url, data=data, headers=req_headers)
        req.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(req)
        print response.read()
        return 1
    except URLError, e:
        if hasattr(e, 'code'):
            print 'HTTPError occurred'
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
        elif hasattr(e, 'reason'):
            print 'URLError occurred'
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        else:
            print 'No exception was raised.'



import demjson
# data = 'help "hello"'
data = '''{"Fields": [

                             {"values": [], "Name": "close-date"},
                             {"values": [{}], "Name": "assign-rcyc"},
                             {"values": [{"value": "2017-09-12 00:26:19"}], "Name": "last-modified"},
                             {"values": [{"value": "Open"}], "Name": "status"},
                             {"values": [{}], "Name": "cycle-config"},
                             {"values": [], "Name": "request-id"},
                             {"values": [{}], "Name": "exec-event-handle"},
                             {"values": [{"value": "2017-11-29"}], "Name": "open-date"},
                             {"values": [{}], "Name": "attachment"},
                             {"values": [{}], "Name": "mail-settings"},
                             {"values": [{"value": "hp.qc.test-set.default"}], "Name": "subtype-id"},
                             {"values": [{"value": "1"}], "Name": "ver-stamp"},
                             {"values": [{"value": "4775"}], "Name": "parent-id"},
                             {"values": [{}], "Name": "os-config"},
                             {"values": [{}], "Name": "description"},
                             {u'values': [{u'value': u'16533'}], u'Name': u'id'},
                             {"values": [{"value": "test_set1111"}], "Name": "name"},
                             {"values": [{"value": "N"}], "Name": "has-linkage"},
                             {"values": [{}], "Name": "pinned-baseline"},
                             {"values": [{}], "Name": "report-settings"},
                             {"values": [{}], "Name": "comment"}
                             ], "Type":"test-set"
                 }'''
encode_data = demjson.encode(data)
print encode_data
decode_data = demjson.decode(encode_data)
print decode_data



import random
#
# int_data = int(random.random()*100 / 1)
# string_data = chr(int_data)
# test_list = {}
# for i in range(1,10):
#     test_list[int(random.random()*100 / 1)] = int(random.random()*100 / 2)
# # print string_data
# print test_list


g = [48, 49, 39, 2, 38, 15, 33, 81, 41]
test_dict = {32: 20, 4: 44, 71: 47, 24: 38, 19: 45, 21: 49, 88: 3, 57: 17, 58: 46}
print test_dict
h = sorted(test_dict.items(), key=lambda x: x[1])
print h

from collections import OrderedDict

h = OrderedDict(h)
print h


def Singleton(cls):
    instance_dict = {}
    def wrap(*args, **kwargs):
        if cls not in instance_dict:
            instance_dict[cls] = cls(*args, **kwargs)
        return instance_dict[cls]
    return wrap

@Singleton
class A(object):
    a = 10
    def __init__(self, x=0):
        self.x = x
        print 'init %s' % x


a = A(12)
b = A(23)
print id(a), id(b)

