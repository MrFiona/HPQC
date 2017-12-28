#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-09-06 13:24
# Author  : MrFiona
# File    : hpqc_parser.py
# Software: PyCharm Community Edition



from collections import OrderedDict
from Common import TestModels
from utils_status import UIDisplayHelper



class HPQCParser:
    def ParseTestInstance(self,jsonobj):
        try:
            ret = []
            uihelper = UIDisplayHelper()
            for entity in jsonobj[r'entities']:
                id = 0
                plan_id = 0
                casename = ''
                status = ''
                status_code = 0
                owner_name = ''
                bug = ''
                comment =''
                unit =''
                value=''
                for field in entity['Fields']:
                    if field['Name'] in ['id','status','owner','user-01','user-02','user-03','user-04' ]:
                        if field['Name'] == 'id' and field['values'] != [] and field['values'] != [{}]:
                            id = int(field['values'][0]['value'])
                            continue
                        if field['Name'] == 'status' and field['values'] != [] and field['values'] != [{}]:
                            status = field['values'][0]['value']
                            continue
                        if field['Name'] == 'owner' and field['values'] != [] and field['values'] != [{}]:
                            owner_name = field['values'][0]['value']
                            continue
                        if field['Name'] == 'user-01' and field['values'] != [] and field['values'] != [{}]:
                            bug = field['values'][0]['value']
                            continue
                        if field['Name'] == 'user-02' and field['values'] != [] and field['values'] != [{}]:
                            comment = field['values'][0]['value']
                            continue
                        if field['Name'] == 'user-03' and field['values'] != [] and field['values'] != [{}]:
                            value = field['values'][0]['value']
                            continue
                        if field['Name'] == 'user-04' and field['values'] != [] and field['values'] != [{}]:
                            unit = field['values'][0]['value']
                            continue
                for related in entity['RelatedEntities']:
                    for field in related['entities'][0]['Fields']:
                        if field['Name'] in ['name', 'id']:
                            if field['Name'] == 'name'and field['values'] != [] and field['values'] != [{}]:
                                casename = field['values'][0]['value']
                                continue
                            if field['Name'] == 'id'and field['values'] != [] and field['values'] != [{}]:
                                plan_id = int(field['values'][0]['value'])
                                continue
                status_code = uihelper.StatusMapping[status]
                instance = TestModels.OSSTestInstance(internal_id=id,status=status_code,owner=owner_name,bug=bug,comment=comment,unit=unit,value=value)
                plan = TestModels.OSSTestPlan(internal_id=plan_id,name=casename)
                ret.append([instance,plan])
            return ret
        except IOError:
            return None


class HPQCCyclingParser:
    def ParseTestInstance(self,jsonobj):
        try:
            ret = []
            uihelper = UIDisplayHelper()
            for entity in jsonobj[r'entities']:
                id = 0
                casename = ''
                sut = ''
                update_sw_config = ''
                update_hw_config = ''
                current_cycles = 0
                fail_cycles = 0
                target = 0
                bug = 0
                comment = ''
                logs = ''
                for field in entity['Fields']:
                    # if field['values'] != [] and field['values'] != [{}]:
                    #     print "name:%s    value:%s" % (field['Name'],field['values'][0]['value'])
                    if field['Name'] in ['id','status','user-01','user-02','user-03','user-04','user-05','user-06','user-07','user-08','user-09','user-10','user-11' ]:
                        if field['Name'] == 'id' and field['values'] != [] and field['values'] != [{}]:
                            id = int(field['values'][0]['value'])
                            continue
                        if field['Name'] == 'user-05' and field['values'] != [] and field['values'] != [{}]:
                            sut = field['values'][0]['value']
                            continue
                        if field['Name'] == 'user-06' and field['values'] != [] and field['values'] != [{}]:
                            update_sw_config = field['values'][0]['value']
                            continue
                        if field['Name'] == 'user-07' and field['values'] != [] and field['values'] != [{}]:
                            update_hw_config = field['values'][0]['value']
                            continue
                        if field['Name'] == 'status' and field['values'] != [] and field['values'] != [{}]:
                            status = field['values'][0]['value']
                            continue
                        if field['Name'] == 'user-09' and field['values'] != [] and field['values'] != [{}]:
                            current_cycles = int(field['values'][0]['value'])
                            continue
                        if field['Name'] == 'user-10' and field['values'] != [] and field['values'] != [{}]:
                            fail_cycles = int(field['values'][0]['value'])
                            continue
                        if field['Name'] == 'user-11' and field['values'] != [] and field['values'] != [{}]:
                            target = int(field['values'][0]['value'])
                            continue
                        if field['Name'] == 'user-01' and field['values'] != [] and field['values'] != [{}]:
                            bug = int(field['values'][0]['value'])
                            continue
                        if field['Name'] == 'user-02' and field['values'] != [] and field['values'] != [{}]:
                            comment = field['values'][0]['value']
                            continue
                        if field['Name'] == 'user-08' and field['values'] != [] and field['values'] != [{}]:
                            logs = field['values'][0]['value']
                            continue
                for related in entity['RelatedEntities']:
                    for field in related['entities'][0]['Fields']:
                        if field['Name'] in ['name', 'id']:
                            if field['Name'] == 'name' and field['values'] != [] and field['values'] != [{}]:
                                casename = field['values'][0]['value']
                                continue
                            if field['Name'] == 'id' and field['values'] != [] and field['values'] != [{}]:
                                plan_id = int(field['values'][0]['value'])
                                continue
                status_code = uihelper.StatusMapping[status]
                instance = TestModels.OSSCyclingInstance(internal_id=id,
                                                       test_case_name=casename,
                                                       sut=sut,
                                                       update_sw_config=update_sw_config,
                                                       update_hw_config=update_hw_config,
                                                       status=status_code,
                                                       current_cycles=current_cycles,
                                                       fail_cycles=fail_cycles,
                                                       target=target,
                                                       bug=bug,
                                                       comment=comment,
                                                       logs=logs,
                                                       hpqc_case_id=id )
                ret.append(instance)
            return ret
        except IOError:
            return None


class HPQCWHQLParser:
    def ParseTestInstance(self,jsonobj):
        if jsonobj is None:
            return []
        try:
            result_dict_list = []
            for entity in jsonobj[r'entities']:
                test_case_id = 0; casename = ''
                owner_name = ''; status = ''
                exec_date = ''; exec_time = ''

                result_dict = OrderedDict()
                for field in entity['Fields']:
                    if field['Name'] in [ 'status','owner','exec-time','exec-date','status', 'test-id', 'id' ]:
                        if field['Name'] == 'test-id' and field['values'] != [] and field['values'] != [{}]:
                            test_case_id = int(field['values'][0]['value'])
                            result_dict['test_case_id'] = test_case_id
                            continue
                        # if field['Name'] == 'id' and field['values'] != [] and field['values'] != [{}]:
                        #     test_case_id = int(field['values'][0]['value'])
                        #     result_dict['test_case_id'] = test_case_id
                        #     continue
                        if field['Name'] == 'status' and field['values'] != [] and field['values'] != [{}]:
                            status = field['values'][0]['value']
                            result_dict['status'] = status
                            continue
                        if field['Name'] == 'owner' and field['values'] != [] and field['values'] != [{}]:
                            owner_name = field['values'][0]['value']
                            result_dict['owner_name'] = owner_name
                            continue
                        if field['Name'] == 'status' and field['values'] != [] and field['values'] != [{}]:
                            status = field['values'][0]['value']
                            continue
                        if field['Name'] == 'exec-time' and field['values'] != [] and field['values'] != [{}]:
                            exec_time = field['values'][0]['value']
                            result_dict['exec_time'] = exec_time
                            continue
                        if field['Name'] == 'exec-date' and field['values'] != [] and field['values'] != [{}]:
                            exec_date = field['values'][0]['value']
                            result_dict['exec_date'] = exec_date
                            continue


                for related in entity['RelatedEntities']:
                    for field in related['entities'][0]['Fields']:
                        if field['Name'] in ['name', 'id']:
                            if field['Name'] == 'name'and field['values'] != [] and field['values'] != [{}]:
                                casename = field['values'][0]['value']
                                result_dict['casename'] = casename
                                continue

                print "\ntest_case_id=%s owner_name=%s casename=%s status=%s exec_date=%s exec_time=%s\n" % (test_case_id, owner_name, casename, status, exec_date, exec_time)
                result_dict_list.append(result_dict)
            return result_dict_list

        except IOError:
            pass


import json
with open(r'C:\Users\pengzh5x\Desktop\machine_scripts\HPQC\Bakerville_test_plan_test_set_info\test_set_Assurance AQ_19828_json_data.json', 'rb') as f:
    data = json.load(f)

from _hpqc_parser_tool import HPQC_info_parser_tool

test = HPQC_info_parser_tool(data)
print test
