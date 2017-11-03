#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-10-12 14:24
# Author  : MrFiona
# File    : _hpqc_parser_tool.py
# Software: PyCharm Community Edition




def HPQC_info_parser_tool(data):
    global_info_dict = {}
    info = data[u'entities'][0][u'Fields']

    for element in info:
        if element[u'Name'] == u'user-08':
            if element[u'values']:
                _applicable_platform = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_applicable_platform', _applicable_platform)

        if element[u'Name'] == u'user-01':
            if element[u'values']:
                _attended = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_attended', _attended)

        if element[u'Name'] == u'user-04':
            _domain = element[u'values'][0].get(u'value', None)
            global_info_dict.setdefault('_domain', _domain)

        if element[u'Name'] == u'user-07':
            if element[u'values']:
                _priority = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_priority', _priority)

        if element[u'Name'] == u'user-02':
            if element[u'values']:
                _setup_time = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_setup_time', _setup_time)

        if element[u'Name'] == u'user-03':
            if element[u'values']:
                _unattended = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_unattended', _unattended)

        if element[u'Name'] == u'user-06':
            if element[u'values']:
                _config = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_config', _config)

        if element[u'Name'] == u'name':
            _test_name = element[u'values'][0].get(u'value', None)
            global_info_dict.setdefault('_test_name', _test_name)

        if element[u'Name'] == u'status':
            if element[u'values']:
                _status = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_status', _status)

        if element[u'Name'] == u'owner':
            if element[u'values']:
                _designer = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_designer', _designer)

        if element[u'Name'] == u'creation-time':
            if element[u'values']:
                _create_date = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_create_date', _create_date)

        if element[u'Name'] == u'subtype-id':
            if element[u'values']:
                _type = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_type', _type)

        if element[u'Name'] == u'id':
            if element[u'values']:
                _test_id = element[u'values'][0].get(u'value', None)
                global_info_dict.setdefault('_test_id', _test_id)

    # print global_info_dict
    return global_info_dict



if __name__ == '__main__':
    import json
    with open(r'C:\Users\pengzh5x\Desktop\machine_scripts\HPQC\test_case_cache\Subject\Purley_FPGA\TCD_Candidate\Linux(Outofdate)\P1\AAL\PI_FPGA_AAL_SDK_Installation_L\7349.json', 'r') as p:
        data = json.load(p)
        HPQC_info_parser_tool(data)