class UIDisplayHelper:
    def __init__(self):
        self.StatusCodeMapping={1:'Passed',
                                2:'Blocked',
                                3:'Failed',
                                4:'Not Completed',
                                5:'No Run',
                                6:'N/A',
                                0:'Invalid'}
        self.StatusMapping = {'Passed':1,
                              'Blocked':2,
                              'Failed':3,
                              'Not Completed':4,
                              'No Run':5,
                              'N/A':6,
                              'Invalid':0}