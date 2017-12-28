#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-09-11 08:52
# Author  : MrFiona
# File    : hpqc_main_entrance.py
# Software: PyCharm Community Edition



import os
import re
import json
try:
    import cPickle as pickle
except:
    import pickle
import time
import xlsxwriter
from operator import itemgetter
from collections import OrderedDict
from create_session import Session
from hpqc_query import HPQCQuery
from hpqc_parser import HPQCWHQLParser
from hpqc_create_operation import create_test_set, create_test_set_folders, create_test_instance_json
from hpqc_common_func import recursive_get_program_test_case_or_test_sets, create_test_set_decorator




start = time.time()
host = r'https://hpalm.intel.com'
session = Session(host, 'pengzh5x', 'QQ@08061635')
query = HPQCQuery('DCG', 'BKC')


#todo 获取项目名称以及id
def get_program_name_id(program_name):
    program_name_id_list = []
    while 1:
        result = query.enumerate_folder_private(0, session, 0)
        if result:
            break
    for element in result:
        if program_name == element[1]:
            program_name_id_list.append(element)
    # print 'program_name_id_list:\t', program_name_id_list
    return program_name_id_list


#todo 获取最近一周周目录名称以及id
def get_program_max_week_folders(program_name):
    test_sets = query.enumerate_folder(program_name, session)
    if test_sets:
        # week_folders_id_list = [ folders for folders in test_sets ]
        week_folders_id_list = [ folders for folders in test_sets if re.match('\d+WW\d+', folders[1]) ]
        # week_folders_id_list.sort(key=lambda x: x[1], reverse=True)
        week_folders_id_list.sort(key=itemgetter(1), reverse=True)
        print 'week_folders_id_list:\t', week_folders_id_list
    else:
        week_folders_id_list = []
    week_name_id_list = list(week_folders_id_list[0])
    return week_name_id_list


#todo 获取指定目录下的目录名称以及id flag: 1--test-plan；0--test-lab
def get_folders_by_parent_id(parent_id, flag):
    result = query.enumerate_folder_private(parent_id,session, flag)
    return result


#todo 生成待创建周目录的名称
def generate_newest_week_name(week_name_id_list):
    week_name = week_name_id_list[1]
    split_list = week_name.split('WW')
    print 'split_list:\t', split_list
    week_num = int(split_list[-1])
    split_list[-1] = str(week_num + 10)
    return 'WW'.join(split_list)


#todo 主程序
def HPQC_main_entrance(program_name):
    program_name_id_list = get_program_name_id(program_name)
    print 'program_name_id_list:\t', program_name_id_list
    week_name_id_list = get_program_max_week_folders(program_name)
    #todo 获取未创建最新目录之前最大week目录下的目录名称以及id
    print 'week_name_id_list:\t', week_name_id_list
    son_week_dir_name_id_list = get_folders_by_parent_id(int(week_name_id_list[0]), 0)
    print 'son_week_dir_name_id_list:\t', son_week_dir_name_id_list

    #todo 创建最新的周目录
    newest_week_name = generate_newest_week_name(week_name_id_list)
    print 'newest_week_name:\t', newest_week_name
    create_test_set_folders(session, newest_week_name, program_name_id_list[0][0], 'newest_week', program_name_id_list[0][1])
    with open('create_test_folders_' + program_name + os.sep + 'newest_week_json_data.json', 'rb') as p:
        json_data = json.load(p)
    newest_week_dir_id = [ element['values'][0]['value'] for element in json_data['Fields'] if element['Name'] == 'id' ][0]
    print 'newest_week_dir_id:\t', newest_week_dir_id, type(newest_week_dir_id)
    #todo 创建最新周目录下的子目录
    for son_name in son_week_dir_name_id_list:
        create_test_set_folders(session, son_name[1], int(newest_week_dir_id), son_name[1], program_name_id_list[0][1])
    #todo 在新创建的周目录创建test-set

    workbook = xlsxwriter.Workbook('%s_%s_test_case.xlsx' %(program_name_id_list[0][1], week_name_id_list[1]))
    sheet = workbook.add_worksheet('result_data')
    sheet.write_row(0, 0, ['test_case_name', 'test_case_id', ' test_case_order', 'hpqc_project', 'work_week',
                                  'test_set_name', 'test_case_value', 'test_case_unit', 'test_case_hsd', 'test_status',
                                  'test_iterations', 'test_exec_date', 'comments'])
    num_line = 1
    for son_name in son_week_dir_name_id_list:
        #todo 获取子目录下的test-set名称以及id
        test_set_id_name_list = query.enumerate_test_set_private(son_name[0], session, 0)
        print 'test_set_id_name_list:\t', test_set_id_name_list
        #todo 获取json文本里已经创建的子目录id
        with open('create_test_folders_' + program_name + os.sep + son_name[1] + '_json_data.json', 'rb') as p:
            json_data = json.load(p)
        newest_son_week_dir_id = [element['values'][0]['value'] for element in json_data['Fields'] if element['Name'] == 'id'][0]
        print 'newest_son_week_dir_id:\t', newest_son_week_dir_id
        #todo 在子目录中创建test-set
        for test_set in test_set_id_name_list:
            test_set_new = test_set[1].replace('/', '#')
            print 'test_set_new:\t', test_set_new
            create_test_set(session, test_set[1], int(newest_son_week_dir_id), test_set_new, program_name_id_list[0][1])
            #todo 上传test-case到test-set中
            with open('create_test_set_' + program_name + os.sep + test_set_new + '_' + str(newest_son_week_dir_id) + '_json_data.json', 'rb') as p:
                json_data = json.load(p)
            newest_test_set_id = [element['values'][0]['value'] for element in json_data['Fields'] if element['Name'] == 'id'][0]
            print 'newest_test_set_id:\t', newest_test_set_id
            #todo 获取上一周对应位置的相同test-set里的test-case相关信息并将test-case上传到最新创建的test-case
            json_obj = query.enumerate_test_instance_private(test_set[0], session, program_name_id_list[0][1], test_set_new)
            parser = HPQCWHQLParser()
            test_case_dict_list = parser.ParseTestInstance(json_obj)
            print 'test_case_dict_list:\t', test_case_dict_list
            if test_set_id_name_list:
                test_set_id_name_list = []
            #todo 得到上一周test-set里的test-case然后依次创建
            for test_case in test_case_dict_list:
                print 'test_case:\t', test_case
                case_info = {'status': test_case['status'],
                             'exec_date': time.strftime('%Y-%m-%d', time.localtime(time.time())),
                             'test_set_id': str(newest_test_set_id),
                             'value': '',
                             'unit': 'MB/Sec',
                             'iterations':'1',
                             'hsd_id': '',
                             'test_case_id':  test_case['test_case_id'],
                             'test_case_order': '1',
                             'exec-time': time.strftime('%H-%M-%S', time.localtime(time.time()))}
                print 'case_info:\t', case_info
                #todo 开始上传test-case到新建的test-set
                create_test_instance_json(case_info, session)
                insert_data = [test_case['casename'], test_case['test_case_id'], '1', program_name, son_name[1], test_set[1], '592.97', 'GB/Sec',
                               '', test_case['status'], '1', time.strftime('%Y-%m-%d', time.localtime(time.time())), 'comments']
                print 'insert_data:\t', insert_data
                sheet.write_row(num_line, 0, insert_data)
                num_line += 1


#todo 创建test-set
@create_test_set_decorator
def func_create_test_set(split_info_list, program_id, program_name, print_error=True):
    # todo 创建test-set
    create_test_set(session, split_info_list[-1], int(program_id), split_info_list[-1], program_name, print_error=print_error)
    with open('create_test_set_' + program_name + os.sep + split_info_list[-1] + '_' + str(
            program_id) + '_json_data.json', 'rb') as p:
        json_data = json.load(p)

    return json_data


HPQC_main_entrance('Bakerville')
# f_case = open('result_test_case_info_pnp113.txt', 'w')
# f_case_combine = open('test_case_combine_pnp113.txt', 'w')
# recursive_get_program_test_case_or_test_sets(query, f_case, f_case_combine, 'Subject/Bakerville', session, 0)
# f_case.close()
# f_case_combine.close()



print time.time() - start
