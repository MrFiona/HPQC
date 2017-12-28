#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-09-06 14:46
# Author  : MrFiona
# File    : hpqc_query.py
# Software: PyCharm Community Edition


import os
import re
import json
import time
import urllib2
from hpqc_parser import HPQCParser, HPQCCyclingParser, HPQCWHQLParser
from hpqc_common_func import url_access_error_decorator
from _hpqc_parser_tool import HPQC_info_parser_tool



class HPQCQuery:
    def __init__(self, project, domain):
        self.project = project
        self.domain = domain

    #todo 获取test-lab指定项目目录下的所有test-case,但是不能获得目录下的子目录以及test-set
    # @url_access_error_decorator('enumerate_test_set_folder')
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
                        print 'error'
                        return None
                    ret = parser.ParseTestInstance(jsonobj)
                    if ret:
                        instances += ret
            return instances
        except IOError:
            return None

    #todo flag: 1--test-plan；0--test-lab 列出test-lab中指定项目路径下的所有test-case id以及名称 f_case, f_case_combine为文件对象
    # @url_access_error_decorator('enumerate_pnp_case_plan')
    def enumerate_pnp_case_plan(self, f_case, f_case_combine, path, session, flag):
        try:
            session.extend_session()
            folders = path.split(r'/')
            parent_id = 0
            for folder in folders:
                if folder:
                    ret_folders = self.enumerate_folder_private(parent_id, session,flag)
                    if ret_folders == None:
                        return None
                    folder_compare = [ ele for ele in ret_folders if ele[1] == folder]
                    if folder_compare:
                        parent_id = folder_compare[0][0]
            testsets = self.enumerate_test_set_private(parent_id, session,flag)
            if testsets:
                print 'original_preview_string path:\t%s\ttestsets:\t%s' % (path, testsets)
                test_case_num_list, test_case_name_list = zip(*testsets)
                # print 'test_case_num_list:\t', test_case_num_list
                # print 'test_case_name_list:\t', test_case_name_list
                f_case.write('\n' + path + '\n')
                f_case.write(' '*10 +'1 => ' + str(test_case_num_list[0]) + '\t' + test_case_name_list[0] + '\n')
                for line_num in range(1, len(test_case_num_list)):
                    f_case.write(' '*10 + '%d => ' % (line_num+1) + str(test_case_num_list[line_num]) + '\t' + test_case_name_list[line_num] + '\n')
                time.sleep(0.01)
                for line in range(len(test_case_num_list)):
                    f_case_combine.write(path + '/' + str(test_case_num_list[line]) + '/' + test_case_name_list[line] + '\n')
                time.sleep(0.01)
            if testsets == None:
                return  None
            return testsets
        except IOError:
            return None

    #todo 获取test-lab中指定项目路径下的目录id以及名称
    # @url_access_error_decorator('enumerate_folder')
    def enumerate_folder(self, path, session):
        try:
            session.extend_session()
            folders = path.split(r'/')
            print 'folders:\t', folders
            parent_id = 0

            for folder in folders:
                if folder:
                    ret_folders = self.enumerate_folder_private(parent_id, session,0)
                    print 'ret_folders:\t', ret_folders
                    if ret_folders == None:
                        return None

                    for ret_folder in ret_folders:
                        if ret_folder[1] == folder:
                            # print ret_folder, folder
                            parent_id = ret_folder[0]
                            print 'parent_id:\t', parent_id
            testsets = self.enumerate_folder_private(parent_id, session,0)
            print 'path:\t%s\ttestsets:\t%s' % (path, testsets)
            if testsets == None:
                return  None
            return testsets
        except IOError:
            return None

    #todo 获取指定项目目录下的所有目录id以及名称 flag: 1--test-plan；0--test-lab
    # @url_access_error_decorator('enumerate_plan_folder')
    def enumerate_plan_folder(self, path, session, flag):
        try:
            session.extend_session()
            folders = path.split(r'/')
            # print 'folders:\t', folders
            parent_id = 0
            for folder in folders:
                if folder:
                    ret_folders = self.enumerate_folder_private(parent_id, session,flag)
                    # print 'ret_folders:\t', ret_folders
                    if ret_folders == None:
                        return None
                    folder_compare = [ele for ele in ret_folders if ele[1] == folder]
                    if folder_compare:
                        parent_id = folder_compare[0][0]
            testsets = self.enumerate_folder_private(parent_id, session,flag)
            # print 'path:\t%s\ttestsets:\t%s' % (path, testsets)
            if testsets == None:
                return None
            return testsets
        except IOError:
            return None

    #todo 获取test-lab指定test-set下的所有的test-case id以及名称  parent_folder为目录的id
    # @url_access_error_decorator('enumerate_test_instance_private')
    def enumerate_test_instance_private(self, parent_folder, session, program_name='default', test_set_name='default'):
        try:
            url = r'%s/qcbin/rest/domains/dcg/projects/bkc/test-instances?fields=test.name&query={cycle-id[%d]}' % (
                session.host, parent_folder)
            cookiestring = r'LWSSO_COOKIE_KEY=%s;QCSession=%s;XSRF-TOKEN=%s;Path=/' % \
                           (session.token, session.cookies[r'QCSession'], session.cookies[r'XSRF-TOKEN'])
            req_headers = {r'Cookie': cookiestring, r'Accept': r'application/json'}
            req = urllib2.Request(url, data=None, headers=req_headers)
            response = urllib2.urlopen(req)
            data = json.load(response)
            print 'instances:\t', data

            if program_name != 'default' and test_set_name != 'default':
                if not os.path.exists('create_test_case_' + program_name):
                    os.makedirs('create_test_case_' + program_name)

                with open('create_test_case_' + program_name + os.sep + '%s_test_case_json_data.json' % test_set_name, 'w') as f:
                    json.dump(data, f, sort_keys=True, indent=4)
            return data
        except IOError:
            return None
        except Exception:
            return None

    #todo flag: 1--test-plan；0--test-lab 获取指定目录中的所有test-set id以及名称  parent_folder为目录的id
    @url_access_error_decorator('enumerate_test_set_private')
    def enumerate_test_set_private(self, parent_folder, session, flag, print_error=True, save_data=False, program_name='default'):
        if flag == 0:
            url = r'%s/qcbin/rest/domains/dcg/projects/bkc/test-sets?query={parent-id[%d]}' % (
                session.host, parent_folder)
        else:
             url = r'%s/qcbin/rest/domains/dcg/projects/bkc/tests?query={parent-id[%d]}' % (
                session.host, parent_folder)
        cookiestring = r'LWSSO_COOKIE_KEY=%s;QCSession=%s;XSRF-TOKEN=%s;Path=/' % \
                       (session.token, session.cookies[r'QCSession'], session.cookies[r'XSRF-TOKEN'])
        req_headers = {r'Cookie': cookiestring, r'Accept': r'application/json'}
        req = urllib2.Request(url, data=None, headers=req_headers)
        response = urllib2.urlopen(req)
        jsonobj = json.load(response)

        #todo 接口类型字符串
        if flag == 1:
            label_string = 'test_plan'
        elif flag == 0:
            label_string = 'test_lab'
        else:
            label_string = 'unknown'

        #todo 兼容功能 json格式保存数据
        if save_data and program_name != 'default':
            if not os.path.exists(program_name + '_%s_test_set_info' % label_string):
                os.makedirs(program_name + '_%s_test_set_info' % label_string)

        sets = []
        for entity in jsonobj[r'entities']:
            name = ''
            id_num = 0
            for field in entity['Fields']:
                if field['Name'] == 'id':
                    id_num = int(field['values'][0]['value'])
                if field['Name'] == 'name':
                    name = field['values'][0]['value']
            sets.append((id_num, name))

            #todo 兼容功能 json格式保存数据
            if save_data and program_name != 'default':
                with open(program_name + '_%s_test_set_info' % label_string + os.sep +
                        'test_set_%s_%s_json_data.json' %(name, str(id_num)), 'wb') as p:
                    json.dump(jsonobj, p, sort_keys=True, indent=4)

        return sets

    #todo flag: 1--test-plan；0--test-lab 获取项目中的目录id以及名称信息 parent为id
    @url_access_error_decorator('enumerate_folder_private')
    def enumerate_folder_private(self, parent, session, flag, print_error=True):
        # try:
            if flag == 0:
                url = r'%s/qcbin/rest/domains/dcg/projects/bkc/test-set-folders?query={parent-id[%d]}' % (
                    session.host, parent)
            else:
                 url = r'%s/qcbin/rest/domains/dcg/projects/bkc/test-folders?query={parent-id[%d]}' % (
                    session.host, parent)
            cookiestring = r'LWSSO_COOKIE_KEY=%s;QCSession=%s;XSRF-TOKEN=%s;Path=/' % \
                           (session.token, session.cookies[r'QCSession'], session.cookies[r'XSRF-TOKEN'])
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
        # except IOError:
        #     return None
        # except Exception:
        #     return None

    #todo 从test-plan里获取到的test-case信息建立缓存，并将test-case关键信息记录在test_case_info_dict字典
    @url_access_error_decorator('enumerate_plan_private')
    def enumerate_plan_private(self, session, cache, plan_id, test_case_file_path, print_error=True):
        result = None
        if cache:
            try:
                result = cache[test_case_file_path + '/' + str(plan_id) + '.json']
            except KeyError:
                pass

        if result is None:
            # try:
                url = r'%s/qcbin/rest/domains/dcg/projects/bkc/tests?query={id[%d]}' % (
                   session.host, plan_id)
                cookiestring = r'LWSSO_COOKIE_KEY=%s;QCSession=%s;XSRF-TOKEN=%s;Path=/' % \
                               (session.token, session.cookies[r'QCSession'],session.cookies[r'XSRF-TOKEN'])
                req_headers = {r'Cookie': cookiestring, r'Accept': r'application/json'}
                req = urllib2.Request(url, data=None, headers=req_headers)
                response = urllib2.urlopen(req)
                json_obj = json.load(response)
                if cache:
                    cache[test_case_file_path + '/' + str(plan_id) + '.json'] = json_obj
            # except IOError:
            #     return None
            # except Exception:
            #     return None

    # @url_access_error_decorator('enumerate_plan_private_1')
    def enumerate_plan_private_1(self, planid, session):
        try:
            url = r'%s/qcbin/rest/domains/dcg/projects/bkc/tests?query={id[%d]}' % (
                session.host, planid)
            cookiestring = r'LWSSO_COOKIE_KEY=%s;QCSession=%s;XSRF-TOKEN=%s;Path=/' % \
                           (session.token, session.cookies[r'QCSession'], session.cookies[r'XSRF-TOKEN'])
            req_headers = {r'Cookie': cookiestring, r'Accept': r'application/json'}
            req = urllib2.Request(url, data=None, headers=req_headers)
            response = urllib2.urlopen(req)
            jsonobj = json.load(response)
            user04 = ''
            for entity in jsonobj[r'entities']:
                for field in entity['Fields']:
                    if field['Name'] == 'user-04':
                        if field.get('values', None) and field.get('values', None) != [{}]:
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
                return
            instances = {}
            parser = HPQCWHQLParser()
            for testset in testsets:
                if testset[1] not in instances.keys():
                    instances[testset[1]] = []
                jsonobj = self.enumerate_test_instance_private(testset[0], session)

                if jsonobj == None:
                    return
                parser.ParseTestInstance(jsonobj)
        except IOError:
            pass

    def get_instance_info_by_id(self, test_instance_id):
        try:
            url = r'%s/qcbin/rest/domains/dcg/projects/bkc/test-instances/%d' % (
                session.host, test_instance_id)
            cookiestring = r'LWSSO_COOKIE_KEY=%s;QCSession=%s;XSRF-TOKEN=%s;Path=/' % \
                           (session.token,
                            session.cookies[r'QCSession'],
                            session.cookies[r'XSRF-TOKEN'])
            req_headers = {r'Cookie': cookiestring, r'Accept': r'application/json'}
            req = urllib2.Request(url, data=None, headers=req_headers)
            response = urllib2.urlopen(req)
            data = json.load(response)
            print 'instances:\t', data, type(data)
            # with open('%d_test_data_1.json' % parent_folder, 'w') as f:
            #     json.dump(data, f, sort_keys=True, indent=4)
            #     f.write(data)
            return data
        except IOError:
            return None
        except Exception:
            return None




if __name__ == '__main__':
    import os
    import time
    from create_session import Session
    from hpqc_parser import HPQCWHQLParser
    from hpqc_common_func import recursive_get_program_test_case_or_test_sets

    start = time.time()
    host = r'https://hpalm.intel.com'
    session = Session(host, 'pengzh5x', 'QQ@08061635')
    query = HPQCQuery('DCG', 'BKC')
    # query.enumerate_plan_folder('Subject/Purley_FPGA/TCD_Candidate', session)
    # query.enumerate_folder('Purley AEP_2s/2017WW44', session)
    # query.enumerate_test_set_private(5003, session, 0)
    # json_obj = query.enumerate_test_instance_private(17169, session)
    # parser = HPQCWHQLParser()
    # result = parser.ParseTestInstance(json_obj)
    # print 'result:\t', result

    f_case = open(os.getcwd() + os.sep + 'test_lab' + os.sep + 'result_test_case_info_test_NFVi_2017WW38-WW39.txt', 'w')
    f_case_combine = open(os.getcwd() + os.sep + 'test_lab' + os.sep + 'test_case_combine_test_NFVi_2017WW38-WW39.txt', 'w')
    query.enumerate_pnp_case_plan(f_case, f_case_combine, 'Bakerville/2016WW47/BKC', session, flag=0)
    query.enumerate_pnp_case_plan(f_case, f_case_combine, 'Subject/Purley_FPGA/TCD_Candidate/Linux(Outofdate)/P1/Stress', session, flag=1)

    # recursive_get_program_test_case_or_test_sets(query, f_case, f_case_combine, 'NFVi', session)
    # f_case.close()
    # f_case_combine.close()

    # query.enumerate_whql_test_set_folder('NFVi/2017WW02/BKC', session)
    # query.get_instance_info_by_id(15201)
    # import re
    # for program in ['NFVi', 'Purley_2s', 'Bakerville']:
    #     test_sets = query.enumerate_folder(program, session)
    #     if test_sets:
    #         week_folders_id_list = [ folders for folders in test_sets if re.match('\d+WW\d+', folders[1]) ]
    #         week_folders_id_list.sort(key=lambda x: x[1], reverse=True)
    #         print 'week_folders_id_list:\t', week_folders_id_list

    #todo 获取test-lab顶级目录信息
    parent_id = 0
    ret_folders = query.enumerate_folder_private(parent_id, session, 0)
    print 'ret_folders:\t', ret_folders
    print time.time() - start
