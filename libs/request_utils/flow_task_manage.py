# -*- coding: utf-8 -*-

import requests
import verify

class FlowTaskManage(verify.VerifyRequest):

    def flow_setup(self, domain_type, task_id, *values):
        values_in_string = '&'.join(['value=' + str(i) for i in values])
        response = requests.get(self.base_URL + '/flowsetup/save?domainType={0}&taskId={1}&strategyType=FILL&{2}'
                                .format(domain_type, task_id, values_in_string), headers=self.headers)
        response.raise_for_status()
        return response.json()

    def flow_setup_by_people(self, task_id, *values):
        return self.flow_setup('PEOPLE', task_id, *values)

    def flow_setup_by_role(self, task_id, *values):
        return self.flow_setup('ROLE', task_id, *values)

    # 按人员, 首次调查
    def flow_setup_by_people_for_inquireing(self, *values):
        return self.flow_setup_by_people(1, *values)

    # 按人员，待一审
    def flow_setup_by_people_for_inquire_success(self, *values):
        return self.flow_setup_by_people(2, *values)

    # 按人员，二审
    def flow_setup_by_people_for_first_verify_sucess(self, *values):
        return self.flow_setup_by_people(3, *values)

    # 按人员，上签审批
    def flow_setup_by_people_for_second_verify_sucess(self, *values):
        return self.flow_setup_by_people(4, *values)

    # 按角色，首次调查
    def flow_setup_by_role_for_inquireing(self, *values):
        return self.flow_setup_by_role(1, *values)

    # 按角色，待一审
    def flow_setup_by_role_for_inquire_success(self, *values):
        return self.flow_setup_by_role(2, *values)

    # 按角色，二审
    def flow_setup_by_role_for_first_verify_sucess(self, *values):
        return self.flow_setup_by_role(3, *values)

    # 按角色，上签审批
    def flow_setup_by_role_for_second_verify_sucess(self, *values):
        return self.flow_setup_by_role(4, *values)

    def get_pending_tasks(self):
        response = requests.post(self.base_URL + '/taskMgr/searchPendingTasks', headers=self.headers)
        response.raise_for_status()
        json = response.json()
        return json['data']['rows'], json['data']['total']

    def get_done_tasks(self):
        response = requests.post(self.base_URL + '/taskMgr/searchDoneTasks', headers=self.headers)
        response.raise_for_status()
        json = response.json()
        return json['data']['rows'], json['data']['total']

    def get_involved_tasks(self):
        response = requests.post(self.base_URL + '/taskMgr/involvedTask', headers=self.headers)
        response.raise_for_status()
        json = response.json()
        return json['data']['rows'], json['data']['total']
