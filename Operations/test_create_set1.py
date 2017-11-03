#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-09-12 08:49
# Author  : MrFiona
# File    : test_create_set.py
# Software: PyCharm Community Edition


import re
import json
import urllib
import urllib2
import base64


class ReturnData:
    def __init__(self, code, data):
        self.code = code
        self.data = data


class Session:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password =password
        self.cookies = {}
        self.token = None
        retrieve_data = self.retrieve_token()
        session_data = self.open_session()
        # print 'retrieve_data.data:\t', retrieve_data.data, retrieve_data.code
        # print 'session_data.data:\t', session_data.data, session_data.code
        # print 'retrieve_data:\t', retrieve_data
        # print 'session_data:\t', session_data

    def __del__(self):
        self.close_session()
        self.discard_token()

    def retrieve_token(self):
        try:
            url = r'%s/qcbin/authentication-point/authenticate' % self.host
            credential = "Basic %s" % base64.b64encode(r'%s:%s' % (self.username,self.password))
            authorization = {r'Authorization':credential,}
            req = urllib2.Request(url,data=None,headers=authorization)
            response = urllib2.urlopen(req)
            # print 'response.headers:\t', response.headers
            cookies = response.headers[r'set-cookie']
            # print 'cookies:\t', cookies
            pat = re.compile(r'^LWSSO_COOKIE_KEY=(?P<token>[^;]+);\S+$')
            m = pat.match(cookies)
            if m:
                token = m.group('token')
                # print 'token:\t', token
                self.token = token
                return ReturnData(response.code,token)
            return ReturnData(-1, 'Please Check the format')
        except IOError, ex:
            return ReturnData(-1, ex.message)

    def open_session(self):
        ret = None
        if not self.token:
            ret = self.retrieve_token()

        if ret and not self.token:
            return ret

        try:
            url = r'%s/qcbin/rest/site-session' % self.host
            cookie_key = "LWSSO_COOKIE_KEY=%s" % self.token
            data = urllib.urlencode(r'')
            request_headers = {r'Cookie':cookie_key,}
            request_headers['Content-Type'] = "application/x-www-form-urlencoded"
            req = urllib2.Request(url,data=None,headers=request_headers)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
            response = opener.open(req,data)
            pat = re.compile(r'^Set-Cookie:\s*(?P<name>[^=]+)=(?P<value>[^;]+);[\w\W]*$')
            cookies = {}
            for item in response.headers.headers:
                m = pat.match(item)
                if m:
                    cookies[m.group(r'name')] = m.group(r'value')
            self.cookies = cookies
            return ReturnData(response.code,cookies)
        except IOError,ex:
            return ReturnData(-1,ex.message)

    def close_session(self):
        if not self.cookies.has_key(r'LWSSO_COOKIE_KEY') or not self.cookies.has_key(r'QCSession'):
            return ReturnData(-1, r'')
        try:
            url = r'%s/qcbin/rest/site-session' % self.host
            cookiestring = r'LWSSO_COOKIE_KEY=%s;QCSession=%s;Path=/' % (self.cookies[r'LWSSO_COOKIE_KEY'],self.cookies[r'QCSession'])
            req_headers = {r'Cookie':cookiestring,r'Accept':'application/json'}
            req = urllib2.Request(url,data=None,headers=req_headers)
            print 'req.get_method:\t', req.get_method
            req.get_method = lambda:'DELETE'
            response = urllib2.urlopen(req)
            return ReturnData(response.code, response.read())
        except IOError,ex:
            return ReturnData(-1,ex.message)

    def discard_token(self):
        try:
            url = r'%s/qcbin/authentication-point/logout' % self.host
            cookie = "LWSSO_COOKIE_KEY=%s" % self.token
            req_headers = {r'Cookie':cookie,}
            req = urllib2.Request(url,data=None,headers=req_headers)
            response = urllib2.urlopen(req)
            return ReturnData(response.code,r'')
        except Exception,ex:
            return ReturnData(-1,ex.message)

    def extend_session(self):
        if not self.cookies.has_key(r'LWSSO_COOKIE_KEY') or not self.cookies.has_key(r'QCSession'):
            return ReturnData(-1, r'')
        try:
            url = r'%s/qcbin/rest/site-session' % self.host
            cookiestring=r'LWSSO_COOKIE_KEY=%s;QCSession=%s;Path=/' % (self.cookies[r'LWSSO_COOKIE_KEY'],self.cookies[r'QCSession'])
            req_headers = {r'Cookie':cookiestring,}
            req = urllib2.Request(url,data=None,headers=req_headers)
            response = urllib2.urlopen(req)
            return ReturnData(response.code,response.read())
        except IOError,ex:
            return ReturnData(-1,ex.message)


class HPQCQuery:
    def __init__(self, project, domain):
        self.project = project
        self.domain = domain


    def enumerate_test_set_folder(self, path, session):
        try:
            session.extend_session()
            folders = path.split(r'/')
            print 'folders:\t', folders
            parent_id = 0
            for folder in folders:
                print 'folder:\t', folder, type(folder)
                if folder:
                    ret_folders = self.enumerate_folder_private(parent_id, session,0)
                    print 'ret_folders:\t', ret_folders
                    if ret_folders == None:
                        return None
                    for ret_folder in ret_folders:
                        if ret_folder[1] == folder:
                            parent_id = ret_folder[0]
            print 'parent_id:\t', parent_id
            testsets = self.enumerate_test_set_private(parent_id, session,0)
            print 'testsets:\t', testsets
            if testsets == None:
                return  None
            instances = []
            parser = HPQCParser()
            for testset in testsets:
                print 'testset:\t', testset
                if not re.match('PnP',testset[1]):
                    jsonobj = self.enumerate_test_instance_private(testset[0], session)
                    if jsonobj == None:
                        return None
                    ret = parser.ParseTestInstance(jsonobj)
                    if ret:
                        instances += ret
            return instances
        except IOError:
            return None

    def enumerate_pnp_test_set_folder(self, path, session):
        try:
            session.extend_session()
            folders = path.split(r'/')
            parent_id = 0
            for folder in folders:
                if folder:
                    ret_folders = self.enumerate_folder_private(parent_id, session, 0)
                    print 'ret_folders:\t', ret_folders
                    if ret_folders == None:
                        return None
                    for ret_folder in ret_folders:
                        if ret_folder[1] == folder:
                            parent_id = ret_folder[0]
            testsets = self.enumerate_test_set_private(parent_id, session, 0)
            print 'testsets1:\t', testsets
            if testsets == None:
                return None
            instances = {}
            parser = HPQCParser()
            pattern = '-'

            for testset in testsets:
                if re.search(pattern, testset[1]):
                    # if testset[1].split('-')[1] not in instances.keys():
                    #     instances[testset[1].split('-')[1]] = []
                    if testset[1] not in instances.keys():
                        instances[testset[1]] = []
                    jsonobj = self.enumerate_test_instance_private(testset[0], session)

                    if jsonobj == None:
                        return None
                    ret = parser.ParseTestInstance(jsonobj)
                    if ret:
                        # instances[testset[1].split('-')[1]] += ret
                        instances[testset[1]] += ret
            return instances
        except IOError:
            return None

    def enumerate_pnp_case_plan(self, path, session, original_preview_string='default'):
        try:
            session.extend_session()
            folders = path.split(r'/')
            parent_id = 0
            for folder in folders:
                if folder:
                    ret_folders = self.enumerate_folder_private(parent_id, session,1)
                    if ret_folders == None:
                        return None
                    folder_compare = [ ele for ele in ret_folders if ele[1] == folder]
                    if folder_compare:
                        # print 'folder_compare:\t', folder_compare[0]
                    # for ret_folder in ret_folders:
                    #     if ret_folder[1] == folder:
                    #         parent_id = ret_folder[0]
                        parent_id = folder_compare[0][0]
            testsets = self.enumerate_test_set_private(parent_id, session,1)
            if testsets:
                print 'original_preview_string path:\t%s\ttestsets:\t%s' % (path, testsets)
                test_case_num_list, test_case_name_list = zip(*testsets)
                # print 'test_case_num_list:\t', test_case_num_list
                # print 'test_case_name_list:\t', test_case_name_list
                f_case.write('\n' + path + '\n')
                f_case.write(' '*10 +'1 => ' + str(test_case_num_list[0]) + '\t' + test_case_name_list[0] + '\n')
                for line_num in range(1, len(test_case_num_list)):
                    f_case.write(' '*10 + '%d => ' % (line_num+1) + str(test_case_num_list[line_num]) + '\t' + test_case_name_list[line_num] + '\n')
                for line in range(len(test_case_num_list)):
                    f_case_combine.write(path + '/' + str(test_case_num_list[line]) + '/' + test_case_name_list[line] + '\n')
            if testsets == None:
                return  None
            return testsets
        except IOError:
            return None

    def enumerate_folder(self, path, session):
        try:
            session.extend_session()
            folders = path.split(r'/')
            # print 'folders:\t', folders
            parent_id = 0

            for folder in folders:
                if folder:
                    ret_folders = self.enumerate_folder_private(parent_id, session,0)
                    # print 'ret_folders:\t', ret_folders
                    if ret_folders == None:
                        return None
                    for ret_folder in ret_folders:
                        if ret_folder[1] == folder:
                            # print ret_folder, folder
                            parent_id = ret_folder[0]
            testsets = self.enumerate_folder_private(parent_id, session,0)
            print 'path:\t%s\ttestsets:\t%s' % (path, testsets)
            if testsets == None:
                return  None
            return testsets
        except IOError:
            return None

    def enumerate_plan_folder(self, path, session):
        try:
            session.extend_session()
            folders = path.split(r'/')
            parent_id = 0
            for folder in folders:
                if folder:
                    ret_folders = self.enumerate_folder_private(parent_id, session,1)
                    print 'ret_folders:\t', ret_folders
                    if ret_folders == None:
                        return None
                    folder_compare = [ele for ele in ret_folders if ele[1] == folder]
                    if folder_compare:
                        # print 'folder_compare_pan_folder:\t', folder_compare[0]
                    # for ret_folder in ret_folders:
                    #     if ret_folder[1] == folder:
                    #         parent_id = ret_folder[0]
                        parent_id = folder_compare[0][0]
            testsets = self.enumerate_folder_private(parent_id, session,1)
            # print 'path:\t%s\ttestsets:\t%s' % (path, testsets)
            if testsets == None:
                return None
            return testsets
        except IOError:
            return None

    def enumerate_test_instance_private(self, parent_folder, session):
        try:
            url = r'%s/qcbin/rest/domains/dcg/projects/bkc/test-instances?fields=test.name&query={cycle-id[%d]}' % (
                session.host, parent_folder)
            cookiestring = r'LWSSO_COOKIE_KEY=%s;QCSession=%s;XSRF-TOKEN=%s;Path=/' % \
                           (session.token,
                            session.cookies[r'QCSession'],
                            session.cookies[r'XSRF-TOKEN'])
            req_headers = {r'Cookie': cookiestring, r'Accept': r'application/json'}
            req = urllib2.Request(url, data=None, headers=req_headers)
            response = urllib2.urlopen(req)
            data = json.load(response)

            #todo 插入excel中
            insert_excel_data(data)

            # print 'instances:\t', data, type(data)
            # with open('%d_test_data_1.json' % parent_folder, 'w') as f:
            #     json.dump(data, f, sort_keys=True, indent=4)
            #     f.write(data)
            return data
        except IOError:
        # except WindowsError:
            # print '111'
            return None
        except Exception:
        # except UserWarning:
        #     print '222'
            return None

    def enumerate_test_set_private(self, parent_folder, session,flag):
        try:
            if flag == 0:
                url = r'%s/qcbin/rest/domains/dcg/projects/bkc/test-sets?query={parent-id[%d]}' % (
                    session.host, parent_folder)
            else:
                 url = r'%s/qcbin/rest/domains/dcg/projects/bkc/tests?query={parent-id[%d]}' % (
                    session.host, parent_folder)
            cookiestring = r'LWSSO_COOKIE_KEY=%s;QCSession=%s;XSRF-TOKEN=%s;Path=/' % \
                           (session.token,
                            session.cookies[r'QCSession'],
                            session.cookies[r'XSRF-TOKEN'])
            req_headers = {r'Cookie': cookiestring, r'Accept': r'application/json'}
            req = urllib2.Request(url, data=None, headers=req_headers)
            response = urllib2.urlopen(req)
            jsonobj = json.load(response)
            print jsonobj
            sets = []
            for entity in jsonobj[r'entities']:
                name = ''
                id = 0
                for field in entity['Fields']:
                    if field['Name'] == 'id':
                        id = int(field['values'][0]['value'])
                    if field['Name'] == 'name':
                        name = field['values'][0]['value']
                sets.append((id, name))
            # print sets
            return sets
        except IOError:
            return None
        except Exception:
            return None

    def enumerate_folder_private(self, parent, session,flag):
        try:
            if flag == 0:
                url = r'%s/qcbin/rest/domains/dcg/projects/bkc/test-set-folders?query={parent-id[%d]}' % (
                    session.host, parent)
            else:
                 url = r'%s/qcbin/rest/domains/dcg/projects/bkc/test-folders?query={parent-id[%d]}' % (
                    session.host, parent)
            cookiestring = r'LWSSO_COOKIE_KEY=%s;QCSession=%s;XSRF-TOKEN=%s;Path=/' % \
                           (session.token,
                            session.cookies[r'QCSession'],
                            session.cookies[r'XSRF-TOKEN'])
            req_headers = {r'Cookie': cookiestring, r'Accept': r'application/json'}
            req = urllib2.Request(url, data=None, headers=req_headers)
            response = urllib2.urlopen(req)
            jsonobj = json.load(response)
            # print 'jsonobj:\t', jsonobj
            folders = []
            for entity in jsonobj[r'entities']:
                name = ''
                id = 0
                for field in entity['Fields']:
                    if field['Name'] == 'id':
                        id = int(field['values'][0]['value'])
                    if field['Name'] == 'name':
                        name = field['values'][0]['value']
                folders.append((id, name))
            return folders
        except IOError:
            return None
        except Exception:
            return None

    def enumerate_plan_private(self, plan_id, test_case_file_path):
        result = None
        if cache:
            try:
                result = cache[test_case_file_path + '/' + str(plan_id) + '.json']
            except KeyError:
                pass

        if result is None:
            try:
                url = r'%s/qcbin/rest/domains/dcg/projects/bkc/tests?query={id[%d]}' % (
                    session.host, plan_id)
                cookiestring = r'LWSSO_COOKIE_KEY=%s;QCSession=%s;XSRF-TOKEN=%s;Path=/' % \
                               (session.token,
                                session.cookies[r'QCSession'],
                                session.cookies[r'XSRF-TOKEN'])
                req_headers = {r'Cookie': cookiestring, r'Accept': r'application/json'}
                req = urllib2.Request(url, data=None, headers=req_headers)
                response = urllib2.urlopen(req)
                json_obj = json.load(response)
                if cache:
                    cache[test_case_file_path + '/' + str(plan_id) + '.json'] = json_obj

                # with open('%d_test_data.json' % plan_id, 'w') as f:
                #     json.dump(json_obj, f, sort_keys=True, indent=4)
                # parser = HPQCCyclingParser()
                # ret = parser.ParseTestInstance(json_obj)
                # for entity in jsonobj[r'entities']:
                #     user04 = ''
                #     for field in entity['Fields']:
                #         if field['Name'] == 'user-04':
                #             if field.get('values', None) and field.get('values', None) != [{}]:
                #             #if field.get(field['values'][0]['value'], None):
                #                 user04 = field['values'][0]['value']
                #             else:
                #                 user04 = ''
                # print 'user04:\t', user04
                # return user04
                # print ret
            except IOError:
                return None
            except Exception:
                return None

    def enumerate_plan_private_1(self, planid):
        try:
            # host = r'https://hpalm.intel.com'
            # session = Session(host, 'ruipengx', '393728-hijk')
            url = r'%s/qcbin/rest/domains/dcg/projects/bkc/tests?query={id[%d]}' % (
                session.host, planid)
            cookiestring = r'LWSSO_COOKIE_KEY=%s;QCSession=%s;XSRF-TOKEN=%s;Path=/' % \
                           (session.token,
                            session.cookies[r'QCSession'],
                            session.cookies[r'XSRF-TOKEN'])
            req_headers = {r'Cookie': cookiestring, r'Accept': r'application/json'}
            req = urllib2.Request(url, data=None, headers=req_headers)
            response = urllib2.urlopen(req)
            jsonobj = json.load(response)
            print jsonobj
            for entity in jsonobj[r'entities']:
                user04 = ''
                for field in entity['Fields']:
                    if field['Name'] == 'user-04':
                        if field.get('values', None) and field.get('values', None) != [{}]:
                            # if field.get(field['values'][0]['value'], None):
                            user04 = field['values'][0]['value']
                        else:
                            user04 = ''
            return user04
        except IOError:
            return None
        except Exception:
            return None

    def enumerate_cycling_test_set_folder(self, path, session):
        try:
            session.extend_session()
            folders = path.split(r'/')
            parent_id = 0
            for folder in folders:
                if folder:
                    ret_folders = self.enumerate_folder_private(parent_id, session, 0)
                    print 'ret_folders:\t', ret_folders
                    if ret_folders == None:
                        return None
                    for ret_folder in ret_folders:
                        if ret_folder[1] == folder:
                            parent_id = ret_folder[0]
            testsets = self.enumerate_test_set_private(parent_id, session, 0)
            print 'parent_id:\t%s\ttestsets:\t%s' % (parent_id, testsets)

            if testsets == None:
                return None
            instances = {}
            parser = HPQCCyclingParser()
            for testset in testsets:
                if testset[1] not in instances.keys():
                    instances[testset[1]] = []
                jsonobj = self.enumerate_test_instance_private(testset[0], session)
                # print 'jsonobj:\t', jsonobj
                if jsonobj == None:
                    return None
                ret = parser.ParseTestInstance(jsonobj)
                if ret:
                    # instances[testset[1].split('-')[1]] += ret
                    instances[testset[1]] += ret
            return instances
        except IOError:
            return None

    def enumerate_whql_test_set_folder(self, path, session):
        try:
            session.extend_session()
            folders = path.split(r'/')
            parent_id = 0
            for folder in folders:
                if folder:
                    ret_folders = self.enumerate_folder_private(parent_id, session, 0)
                    if ret_folders == None:
                        return None
                    for ret_folder in ret_folders:
                        if ret_folder[1] == folder:
                            parent_id = ret_folder[0]
            testsets = self.enumerate_test_set_private(parent_id, session, 0)

            if testsets == None:
                return None
            instances = {}
            parser = HPQCWHQLParser()
            for testset in testsets:
                if testset[1] not in instances.keys():
                    instances[testset[1]] = []
                jsonobj = self.enumerate_test_instance_private(testset[0], session)

                if jsonobj == None:
                    return None
                ret = parser.ParseTestInstance(jsonobj)
                if ret:
                    # instances[testset[1].split('-')[1]] += ret
                    instances[testset[1]] += ret
            return instances
        except IOError:
            return None

    def test_instance_func(self, path, session):
        session.extend_session()
        folders = path.split(r'/')
        parent_id = 0
        for folder in folders:
            if folder:
                ret_folders = self.enumerate_folder_private(parent_id, session, 1)
                print 'ret_folders:\t', ret_folders
                if ret_folders == None:
                    return []
                for ret_folder in ret_folders:
                    if ret_folder[1] == folder:
                        parent_id = ret_folder[0]
        testsets = self.enumerate_test_set_private(parent_id, session, 1)
        print 'parent_id:\t%s\ttestsets:\t%s' % (parent_id, testsets)
        return testsets




host = r'https://hpalm.intel.com'
# query = HPQCQuery('BKC', 'DCG')
session = Session(host, 'pengzh5x', 'QQ@08061635')
query = HPQCQuery('DCG', 'BKC')


import time

# todo 创建test-set-folders
def create_pnp_test_set(test_set_name):
    try:
        # url = r'%s/qcbin/rest/domains/dcg/projects/bkc/test-sets' % (session.host)
        # url = r'%s/qcbin/rest/domains/dcg/projects/bkc/test-sets/13793/fields?required=true' % (session.host)
        url = r'%s/qcbin/rest/domains/dcg/projects/bkc/test-set-folders/4833?query={force-delete-children=y}' % (session.host)
        cookiestring = r'LWSSO_COOKIE_KEY=%s;QCSession=%s;XSRF-TOKEN=%s;Path=/' % \
                       (session.token,
                        session.cookies[r'QCSession'],
                        session.cookies[r'XSRF-TOKEN'])
        req_headers = {r'Cookie': cookiestring, r'Accept': r'application/json'}
        # todo 注意:当hierarchical-path 的值为空是则无法移动至其子目录下, 但是可以移动至上级目录，例如此例为2736父目录为NFVi项目目录，可以移动至Root目录下
        # todo 而且永远只能往上级目录移动！！！！但是不可以移动至项目子目录下,多级目录创建直接将parent-id改成你想创建的目录的id
        # data = '''{"Fields":[{"Name":"name","values":[{"value":"%s"}]},
        #                      {"Name": "parent-id", "values": [{"value": "2737"}]},
        #                      {"Name": "hierarchical-path", "values": [{"value": "AAAAAEAB"}]}
        #      ]}''' % test_set_name
        # print data
        data = '''{"Fields":[
                            {"Name": "status", "values": [{"value": "Open"}]},
                            {"Name": "name", "values": [{"value": "%s"}]},
                            {"Name": "subtype-id", "values": [{"value": "hp.qc.test-set.default"}]},
                            {"Name": "parent-id", "values": [{"value": "2736"}]},
                            {"Name": "open-date", "values": [{"value": "%s"}]}
                            ],"Type":"test-set"}''' % ('GGGm', time.strftime('%Y-%m-%d', time.localtime(time.time())))

        # {"Name": "status", "values": [{"value": "Open"}]},
        # {"Name": "name", "values": [{"value": "gggg1"}]},
        # {"Name": "subtype-id", "values": [{"value": "hp.qc.test-set.default"}]},
        # {"Name": "parent-id", "values": [{"value": "4713"}]},
        # {"Name": "has-linkage", "values": [{"value": "N"}]},
        # {"Name": "open-date", "values": [{"value": "2017-09-21"}]}


        # {"values": [{"value": "Open"}], "Name": "status"},
        # {"values": [{"value": "gggg1"}], "Name": "name"},
        # {"values": [{"value": "hp.qc.test-set.default"}], "Name": "subtype-id"},
        # {"values": [{"value": "4713"}], "Name": "parent-id"},
        # {"values": [{"value": "N"}], "Name": "has-linkage"},
        # {"values": [{"value": "2017-09-21"}], "Name": "open-date"}

        # data = '''{"Fields":[
        #             {"Name":"status","values":[{"value":"Open"}]},
        #             {"Name":"name","values":[{"value":"Abcde-j"}]},
        #             {"Name":"subtype-id","values":[{"value":"%s"}]},
        #             {"Name":"parent-id","values":[{"value":"%d"}]},
        #             {"Name":"has-linkage","values":[{"value":"N"}]},
        #             {"Name":"open-date","values":[{"value":"2017-09-21"}]}
        #             ],"Type":"test-set"}''' % ('hp.qc.test-set.default', 4713)

        req = urllib2.Request(url, data=None, headers=req_headers)
        req.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(req)
        print response.read()
        return 1
    except urllib2.URLError, e:
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

create_pnp_test_set('666')


# {"values": [{"values":"1234"}], "Name": "request-id"},
#                              {"values": [{"value": "1"}], "Name": "ver-stamp"},
#                              {"values": [{"value": "1"}], "Name": "id"},

# {"values": [], "Name": "close-date"},
# {"values": [{}], "Name": "assign-rcyc"},
# {"values": [{"value": "2017-09-12 00:26:19"}], "Name": "last-modified"},
# {"values": [{"value": "Open"}], "Name": "status"},
# {"values": [{}], "Name": "cycle-config"},
# {"values": [], "Name": "request-id"},
# {"values": [{}], "Name": "exec-event-handle"},
# {"values": [{"value": "2017-11-29"}], "Name": "open-date"},
# {"values": [{}], "Name": "attachment"},
# {"values": [{}], "Name": "mail-settings"},
# {"values": [{"value": "hp.qc.test-set.default"}], "Name": "subtype-id"},
# {"values": [{"value": "1"}], "Name": "ver-stamp"},
# {"values": [{"value": "4782"}], "Name": "parent-id"},
# {"values": [{}], "Name": "os-config"},
# {"values": [{}], "Name": "description"},
# {"values": [{"value": "test_set1111"}], "Name": "name"},
# {"values": [{"value": "N"}], "Name": "has-linkage"},
# {"values": [{}], "Name": "pinned-baseline"},
# {"values": [{}], "Name": "report-settings"},
# {"values": [{}], "Name": "comment"}
# ], "Type":
# "test-set"                                                                                                    


class MyClass(object):
    def __init__(self):
        self._some_property = "properties are nice"
        self._some_other_property = "VERY nice"
    def normal_method(*args,**kwargs):
        print "calling normal_method({0},{1})".format(args,kwargs)
    @classmethod
    def class_method(*args,**kwargs):
        print "calling class_method({0},{1})".format(args,kwargs)
    @staticmethod
    def static_method(*args,**kwargs):
        print "calling static_method({0},{1})".format(args,kwargs)
    @property
    def some_property(self,*args,**kwargs):
        print "calling some_property getter({0},{1},{2})".format(self,args,kwargs)
        return self._some_property
    @some_property.setter
    def some_property(self,*args,**kwargs):
        print "calling some_property setter({0},{1},{2})".format(self,args,kwargs)
        self._some_property = args[0]
    @property
    def some_other_property(self,*args,**kwargs):
        print "calling some_other_property getter({0},{1},{2})".format(self,args,kwargs)
        return self._some_other_property

# o= MyClass()
# o.class_method()
# o.static_method()

# o.some_property = 10
# print o.some_property

# MyClass.static_method()
# MyClass.class_method()

# import argparse
#
#
# parser = argparse.ArgumentParser(description="A dir generator")
# parser.add_argument('-d', '--dir', type=str,
#                     help='set target dir path. defaults to ./',
#                     default='./')
# parser.add_argument('-f', '--file', type=str,
#                     help='set config file path. defaults to ./index.json',
#                     default='./index.json')
# args = parser.parse_args()
# print args
# file_path = args.file
# dir_path = args.dir
# print file_path, dir_path