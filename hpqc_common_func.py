#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-09-26 15:44
# Author  : MrFiona
# File    : hpqc_common_func.py
# Software: PyCharm Community Edition


from urllib2 import URLError
import functools
from threading import Thread
from collections import OrderedDict as _dict
from _hpqc_parser_tool import HPQC_info_parser_tool


#todo
def url_access_error_decorator(func_label_name):
    def inner_func(func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            cmd = None
            while 1:
                try:
                    cmd = func(*args, **kwargs)
                    # print 'args:\t', args
                    # print 'kwargs:\t', kwargs
                except URLError as e:
                    if hasattr(e, 'code'):
                        if kwargs.get('print_error', False):
                            print 'func_label_name: %s, HTTPError occurred! The server could not fulfill the request. Error code: %s' \
                                  % (func_label_name, e.reason)
                    elif hasattr(e, 'reason'):
                        if kwargs.get('print_error', False):
                            print 'func_label_name: %s, URLError occurred! We failed to reach a server. Reason: %s' \
                                  % (func_label_name, e.reason)
                except Exception:
                    if kwargs.get('print_error', False):
                        print 'Exception occurred!!!'
                else:
                    print '%s successfully!!!!' % func_label_name
                    break

            return cmd
        return wrap
    return inner_func


#todo
def recursive_get_info(query, f_case, f_case_combine, dir_case_plan_string, session, flag):
    query.enumerate_pnp_case_plan(f_case, f_case_combine, dir_case_plan_string, session, flag)
    power_folder = query.enumerate_plan_folder(dir_case_plan_string, session, flag)

    if not power_folder:
        return

    thread_list = []
    for folder in power_folder:
        t = Thread(target=recursive_get_info, args=(query, f_case, f_case_combine, dir_case_plan_string + '/' + folder[1], session, flag))
        thread_list.append(t)

    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()


# TODO 从项目里获取test-case或者test-set详细信息 flag: 1--test-plan；0--test-lab
def recursive_get_program_test_case_or_test_sets(query, f_case, f_case_combine, dir_case_plan_string, session, flag):
    try:
        recursive_get_info(query, f_case, f_case_combine, dir_case_plan_string, session, flag)
    except Exception, e:
        print 'get_pnp_case_plan: %s' % e


#todo 一个装饰器捕获IOError循环执行
def create_test_set_decorator(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        while 1:
            try:
                func(*args, **kwargs)
                break
            except IOError:
                pass

    return wrap


#todo 将保存在文件中的test_plan里的test-case关键信息以字典形式返回
def get_test_plan_test_case_info():
    import os
    import json
    global_info_dict = _dict()
    for dirpath, dirnames, filenames in os.walk(os.getcwd() + os.sep + 'test_case_cache' + os.sep + 'Subject' + os.sep + 'Purley_FPGA'):
        i = 0
        for eb in filenames:
            i += 1
            print os.path.join(dirpath, eb)
            with open(os.path.join(dirpath, eb), 'r') as p:
                data = json.load(p)
                signal_data_dict = HPQC_info_parser_tool(data)
                print signal_data_dict
                global_info_dict[signal_data_dict['_test_id']] = signal_data_dict
    print global_info_dict, len(global_info_dict)






if __name__ == '__main__':
    get_test_plan_test_case_info()