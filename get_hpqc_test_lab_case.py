#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-09-06 14:29
# Author  : MrFiona
# File    : get_hpqc_test_lab_case.py
# Software: PyCharm Community Edition


import threadpool
from Common import Utils
from hpqc_query import HPQCQuery


#todo 获取test-lab对应目录信息
class GetHPQCTestLabCase:
    def __init__(self, host, session, query, project_name, week_name, step_name):
        """
        :param host: HPQC网址 https://hpalm.intel.com
        :param session: session对象
        :param query:  qurey对象
        :param project_name: 项目名称
        :param week_name: 项目名称下的二级目录名称
        :param step_name: 项目名称二级目录下的三级目录名称
        """
        self.host = host
        self.session = session
        self.query = query
        self.project_name = project_name
        self.week_name = week_name
        self.step_name = step_name

    def enumerate_plan(self, info):
        for i in range(3):
            domain = info[2].enumerate_plan_private_1(info[1].internal_id, self.session)
            if domain != None:
                break
        info[3].append((domain, info[1].name, info[4].StatusCodeMapping[info[0].status], info[0].bug, info[0].comment))


    def get_lab_case_info(self):
        uihelper = Utils.UIDisplayHelper()
        steps = []
        result = []

        if self.step_name.upper() == 'SILVER':
            steps = ['Daily', 'Silver']
        elif len(self.step_name) == 0:
            pass
        else:
            steps.append(self.step_name)

        for step in steps:
            if len(self.week_name) != 0 and len(self.step_name) != 0:
                path = r'/%s/%s/%s' % (self.project_name, self.week_name, step)
            else:
                path = r'/%s/' % (self.project_name)
            print 'path:\t', path
            cases = self.query.enumerate_test_set_folder(path, self.session)
            if cases == None:
                return None
            for item in cases:
                item.extend([self.query, result, uihelper])
            pool = threadpool.ThreadPool(40)
            requests = threadpool.makeRequests(self.enumerate_plan, cases)
            [pool.putRequest(req) for req in requests]
            pool.wait()
            pool.dismissWorkers(40)
        print 'result:\t', result
        return result



if __name__ == '__main__':
    import time
    from create_session import Session
    from hpqc_query import HPQCQuery
    start = time.time()
    host = r'https://hpalm.intel.com'
    session = Session(host, 'pengzh5x', 'QQ@08061635')
    query = HPQCQuery('DCG', 'BKC')
    test_case = GetHPQCTestLabCase(host, session, query, 'Bakerville', '', '')
    # test_case = GetHPQCTestLabCase(host, session, query, 'Purley_4s:2016WW18_TryRun', '2016', '')
    test_case.get_lab_case_info()
    print time.time() - start