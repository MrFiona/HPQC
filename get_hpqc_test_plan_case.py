#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-09-06 15:13
# Author  : MrFiona
# File    : get_hpqc_test_plan_case.py
# Software: PyCharm Community Edition


from threading import Thread, Lock
from collections import OrderedDict as _dict
from test_case_cache import Test_Case_Cache



class GetHPQCTestPlanCase:
    def __init__(self, session, query, project_path):
        """
        :param session:
        :param query:
        :param project_path:
        """
        self.session = session
        self.query = query
        self.project_path = project_path
        self.f_case = open('result_test_case_info_pnp9.txt', 'w')
        self.f_case_combine = open('test_case_combine_pnp9.txt', 'w')

    def return_close(self):
        self.f_case.close()
        self.f_case_combine.close()

    def recursive_FPGA_case_plan(self, dir_case_plan_string, session):
        # power_folder = self.query.enumerate_plan_folder(dir_case_plan_string, session, flag=1)
        # performance = self.query.enumerate_pnp_case_plan(self.f_case, self.f_case_combine, dir_case_plan_string, session, flag=1)

        session.extend_session()
        folders = dir_case_plan_string.split(r'/')
        parent_id = 0
        for folder in folders:
            if folder:
                ret_folders = self.query.enumerate_folder_private(parent_id, session, flag=1)
                if ret_folders == None:
                    ret_folders = []
                    # print 'ret_folders:\t', dir_case_plan_string
                folder_compare = [ele for ele in ret_folders if ele[1] == folder]
                if folder_compare:
                    parent_id = folder_compare[0][0]
        ret_folders = self.query.enumerate_folder_private(parent_id, session, flag=1)

        testsets = self.query.enumerate_test_set_private(parent_id, session, flag=1)
        if testsets:
            print 'original_preview_string path:\t%s\ttestsets:\t%s' % (dir_case_plan_string, testsets)
            test_case_num_list, test_case_name_list = zip(*testsets)
            print 'test_case_num_list:\t', test_case_num_list
            print 'test_case_name_list:\t', test_case_name_list
            self.f_case.write('\n' + dir_case_plan_string + '\n')
            self.f_case.write(' ' * 10 + '1 => ' + str(test_case_num_list[0]) + '\t' + test_case_name_list[0] + '\n')
            for line_num in xrange(1, len(test_case_num_list)):
                self.f_case.write(' ' * 10 + '%d => ' % (line_num + 1) + str(test_case_num_list[line_num]) + '\t' +
                             test_case_name_list[line_num] + '\n')
            for line in xrange(len(test_case_num_list)):
                self.f_case_combine.write(
                    dir_case_plan_string + '/' + str(test_case_num_list[line]) + '/' + test_case_name_list[line] + '\n')

        if not ret_folders:
            return

        thread_list = []
        for folder in ret_folders:
            t = Thread(target=self.recursive_FPGA_case_plan, args=(dir_case_plan_string + '/' + folder[1], session))
            thread_list.append(t)

        for t in thread_list:
            t.start()

        for t in thread_list:
            t.join()

    # TODO 获取test plan里test-case详细信息
    def get_plan_case_info(self):
        try:
            self.recursive_FPGA_case_plan(self.project_path, self.session)
        except Exception, e:
            print 'get_pnp_case_plan: %s' % e

    # todo 从get_plan_case_info接口获取到的test-case信信息，建立其缓存目录
    def establish_plan_case_cache_dir(self):
        cache = Test_Case_Cache()
        test_case_id_list = []
        test_case_name_pah_list = []
        with open('test_case_combine_pnp9.txt', 'r') as p:
            for line in p:
                test_case_string_list = line.strip().split('/')
                print 'test_case_string_list:\t', test_case_string_list
                test_case_id = int(test_case_string_list[-2])
                test_case_id_list.append(test_case_id)
                pre_case_string_list = test_case_string_list[:-2]
                pre_case_string_list.append(test_case_string_list[-1])
                test_case_name_pah_list.append('/'.join(pre_case_string_list))
        print 'test_case_id_list:\t', test_case_id_list, len(test_case_id_list)
        # print test_case_name_pah_list, len(test_case_name_pah_list)

        thread_list = []
        for case in range(len(test_case_id_list)):
            # self.query.enumerate_plan_private(self.session, cache, test_case_id_list[case], test_case_name_pah_list[case])
            t = Thread(target=self.query.enumerate_plan_private,
                       args=(self.session, cache, test_case_id_list[case], test_case_name_pah_list[case]))
            thread_list.append(t)

        for t in thread_list:
            t.start()

        for t in thread_list:
            t.join()

    # todo 在从test_plan中获取test-case时将test-case信息记录在excel中
    def insert_test_case_info_into_excel(self):
        pass




if __name__ == '__main__':
    import time
    from create_session import Session
    from hpqc_query import HPQCQuery
    start = time.time()
    host = r'https://hpalm.intel.com'
    session = Session(host, 'pengzh5x', 'QQ@08061635')
    query = HPQCQuery('DCG', 'BKC')
    test_case = GetHPQCTestPlanCase(session, query, 'Subject/Purley_FPGA')
    test_case.get_plan_case_info()
    test_case.return_close()
    test_case.establish_plan_case_cache_dir()
    print time.time() - start
    # with open('test_case_combine_pnp6.txt', 'r') as p:
    #     for line in p:
    #         print line.strip()