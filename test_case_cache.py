#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-08-30 12:33
# Author  : MrFiona
# File    : test_case_cache.py
# Software: PyCharm Community Edition


import os
import cPickle
import json


class Test_Case_Cache:
    def __init__(self):
        pass

    def path_parse(self, path_string):
        pass

    def __getitem__(self, path_string):
        path = 'test_case_cache' + '/' + path_string
        if os.path.exists(path):
            with open(path, 'r') as fp:
                json.load(fp)

    def __setitem__(self, path_string, value):
        path_string_list = path_string.split('/')
        file_path = path_string_list[-1]
        path_string = '/'.join(path_string_list[:-1])
        path = 'test_case_cache' + '/' + path_string
        if not os.path.exists(path):
            print 'create the cache directory:\t', path
            os.makedirs(path)
        with open(path + os.sep + file_path, 'wb') as fp:
            print 'the cache directory is exist:\t', path
            json.dump(value, fp, sort_keys=True, indent=4)




# test_case_path = 'Subject/Purley_FPGA/TCD_Candidate/Linux(Outofdate)/P1/Manageability'
# test_case_path = 'Subject/Purley_FPGA/TCD_Candidate/Linux_new_plan/P1/Power Management'

# test = Test_Case_Cache()
# m = test[test_case_path]

# if not os.path.exists(test_case_path):
#     os.makedirs(test_case_path)