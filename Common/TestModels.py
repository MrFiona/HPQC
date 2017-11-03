from datetime import datetime


class OSSTestPlan:
    def __init__(self, internal_id='', create_time=datetime.now(), update_time=datetime.now(), name='', status=0):
        self.internal_id = internal_id
        self.create_time = create_time
        self.update_time = update_time
        self.name = name
        self.status = status


class OSSComponent:
    def __init__(self, create_time=datetime.now(), update_time=datetime.now(), name=''):
        self.create_time = create_time
        self.update_time = update_time
        self.name = name


class OSSProject:
    def __init__(self, name,
                 description, create_time=datetime.now(), update_time=datetime.now(),
                 status=0, test_id_list=()):
        self.name = name
        self.description = description
        self.create_time = create_time
        self.update_time = update_time
        self.status = status
        self.test_id_list = test_id_list


class OSSDefect:
    def __init__(self, internal_id='',
                 create_time=datetime.now(),
                 update_time=datetime.now(),
                 name='', priority=3,
                 severity=3, description='',
                 status=0,
                 reported_by='',
                 owner='',
                 close_time=None):
        self.internal_id = internal_id
        self.create_time = create_time
        self.update_time = update_time
        self.name = name
        self.severity = severity
        self.priority = priority
        self.description = description
        self.status = status
        self.reported_by = reported_by
        self.owner = owner
        self.close_time = close_time


class OSSTestInstance:
    def __init__(self, internal_id='',
                 status=0,
                 result=0,
                 owner='',
                 bug='',
                 comment='',
                 unit='',
                 value='',
                 start_time=datetime.now(),
                 complete_time=datetime.now(),
                 config_internal_id=''):
        self.internal_id = internal_id
        self.status = status
        self.result = result
        self.owner = owner
        self.bug = bug
        self.comment = comment
        self.unit=unit
        self.value=value
        self.start_time = start_time
        self.complete_time = complete_time
        self.config_internal_id = config_internal_id

class OSSCyclingInstance:
    def __init__(self, internal_id='',
                 test_case_name='',
                 sut='',
                 update_sw_config='',
                 update_hw_config='',
                 status = 0,
                 current_cycles = 0,
                 fail_cycles = 0,
                 target = 0,
                 bug = 0,
                 comment = '',
                 logs = '',
                 hpqc_case_id = 0):
        self.internal_id = internal_id
        self.test_case_name = test_case_name
        self.sut = sut
        self.update_sw_config = update_sw_config
        self.update_hw_config = update_hw_config
        self.status = status
        self.current_cycles = current_cycles
        self.fail_cycles = fail_cycles
        self.target = target
        self.bug = bug
        self.comment = comment
        self.logs = logs
        self.hpqc_case_id = hpqc_case_id

class OSSTestDefectLink:
    def __init__(self, defect_internal_id, instance_internal_id):
        self.defect_internal_id = defect_internal_id
        self.instance_internal_id = instance_internal_id


class OSSConfig:
    def __init__(self, internal_id, name, description, status):
        self.internal_id = internal_id
        self.name = name
        self.description = description
        self.status = status
