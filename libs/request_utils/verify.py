import requests
from .. import global_config


class SubmitApplicationResponse(object):
    def __int__(self):
        self.response = None
        self.result_code = ''
        self.application_id = ''

    def parse(self, response):
        self.result_code = ''
        self.application_id = ''

        ret = response.json()
        if ret.has_key('data'):
            ret = ret['data']
            if ret.has_key('rst'):
                ret = ret['rst']
                if ret.has_key('resultCode'):
                    self.result_code = ret['resultCode']
                if ret.has_key('applicationId'):
                    self.application_id = ret['applicationId']
        return self


class LoadApplicationStatusResponse(object):
    def __int__(self):
        self.result_code = ''
        self.card_product_id = 0
        self.cash_amount_ratio = 0.0
        self.credit_limit = 0.0
        self.current_application_status = ''
        self.current_application_verify_status = ''
        self.user_key = ''
        self.card_product_id = 0

    def parse(self, response):
        ret = response.json()
        if ret.has_key('data'):
            ret = ret['data']
            if ret.has_key('rst'):
                ret = ret['rst']
                if ret.has_key('resultCode'):
                    self.result_code = ret['resultCode']
                if ret.has_key('cashAmountRatio'):
                    self.cash_amount_ratio = ret['cashAmountRatio']
                if ret.has_key('creditLimit'):
                    self.credit_limit = ret['creditLimit']
                if ret.has_key('currentApplicationStatus'):
                    self.current_application_status = ret['currentApplicationStatus']
                if ret.has_key('currentApplicationVerifyStatus'):
                    self.current_application_verify_status = ret['currentApplicationVerifyStatus']
                if ret.has_key('userKey'):
                    self.user_key = ret['userKey']
                if ret.has_key('cardProductId'):
                    self.card_product_id = ret['cardProductId']
        return self


class VerifyRequest(object):
    def __init__(self, base_URL, username=None, password=None):
        self.base_URL = base_URL
        self.username = username
        self.password = password
        self.headers = {}

        if self.username is None:
            self.username = 'admin@heika.com'
            self.password = global_config.login_username_passwd_mapping.get(self.username)
        elif self.password is None:
            self.password = global_config.login_username_passwd_mapping.get(self.username)

    def login(self):
        post_data = {"username": self.username, "password": self.password}
        response = requests.post(self.base_URL + "/login/login", data=post_data)
        response.raise_for_status()
        self.headers["Cookie"] = "JSESSIONID=" + response.cookies.get("JSESSIONID")

    def init_user_from_mobile(self, user_id):
        post_data = {"userId": user_id}
        response = requests.post(self.base_URL + "/init", data=post_data)
        response.raise_for_status()
        return response

    def commit_user_from_mobile(self, user_id):
        post_data = {"userId": user_id}
        response = requests.post(self.base_URL + "/commit", data=post_data)
        response.raise_for_status()
        return response

    def commit_to_first_verify(self, user_id, online_time, note, **investigate_results):
        post_data = {"onlineTime": online_time, "note": note, "userId": user_id}
        post_data.update(investigate_results)
        response = requests.post(self.base_URL + "/taskMgrInvestigate/commitToFirstVerify", data=post_data, headers=self.headers)
        response.raise_for_status()
        return response

    def commit_to_verify_fail(self, user_id, online_time, note, **investigate_results):
        post_data = {"onlineTime": online_time, "note": note, "userId": user_id}
        post_data.update(investigate_results)
        response = requests.post(self.base_URL + "/taskMgrInvestigate/commitToAdditionalFile", data=post_data, headers=self.headers)
        response.raise_for_status()
        return response

    def commit_to_second_verify(self, user_id, amount, card_product_id, cash_ratio, note):
        post_data = {"userId": user_id, "firstVerifyAmount": amount, "firstVerifyCardProductId": card_product_id, "firstCashRatio": cash_ratio, "firstVerifyNote": note}
        response = requests.post(self.base_URL + "/taskMgrVerify/commitToSecondVerify", data=post_data, headers=self.headers)
        response.raise_for_status()
        return response

    def commit_to_first_verify_sendback(self, user_id, note):
        post_data = {"userId": user_id, "firstVerifyNote": note}
        response = requests.post(self.base_URL + "/taskMgrVerify/commitToFirstVerifyBack", data=post_data, headers=self.headers)
        response.raise_for_status()
        return response

    def commit_to_pass_second_verify(self, user_id, amount, card_product_id, cash_ratio, note):
        post_data = {"userId": user_id, "secondVerifyAmount": amount, "secondVerifyCardProductId": card_product_id, "secondCashRatio": cash_ratio, "secondVerifyNote": note}
        response = requests.post(self.base_URL + "/taskMgrVerify/commitToPassSecondVerify", data=post_data, headers=self.headers)
        response.raise_for_status()
        return response

    def commit_to_second_verify_sendback(self, user_id, note):
        post_data = {"userId": user_id, "secondVerifyNote": note}
        response = requests.post(self.base_URL + "/taskMgrVerify/commitToSecondVerifyBack", data=post_data, headers=self.headers)
        response.raise_for_status()
        return response

    def commit_to_pass_signed_approval(self, user_id, amount, card_product_id, cash_ratio, note):
        post_data = {"userId": user_id, "signedApprovalAmount": amount, "signedApprovalCardProductId":card_product_id, "thirdCashRatio":cash_ratio, "signedApprovalNote":note}
        response = requests.post(self.base_URL + "/taskMgrVerify/commitToPassSignedApproval", data=post_data, headers=self.headers)
        response.raise_for_status()
        return response

    def commit_to_refuse(self, user_id, reject_reason, note):
        post_data = {"userId": user_id, "rejectReasonList": reject_reason, "remark": note}
        response = requests.post(self.base_URL + "/taskMgrVerify/commitToSignedApprovalRefuse", data=post_data, headers=self.headers)
        response.raise_for_status()
        return response

    def update_verify_user(self, name, user_id, amount_limit, dept_id, role_id):
        post_date = {"userId": user_id, "name": name, "amountLimit": amount_limit, "deptId": dept_id, "roleIds": role_id}
        response = requests.post(self.base_URL + "/verifyUser/usr/update", data=post_date, headers=self.headers)
        response.raise_for_status()
        return response

    def update_verify_user_to_mul_roles(self, name, user_id, amount_limit, dept_id, *role_ids):
        post_date = [("userId", user_id),("name", name), ("amountLimit", amount_limit), ("deptId", dept_id)]
        for role_id in role_ids:
            post_date.append(("roleIds", role_id))
        response = requests.post(self.base_URL + "/verifyUser/usr/update", data=post_date, headers=self.headers)
        response.raise_for_status()
        return response

    def get_user_verify_logs(self, user_id):
        post_data = {"userId": user_id}
        response = requests.post(self.base_URL + "/user/getUserVerifyLog", data=post_data, headers=self.headers)
        response.raise_for_status()
        return response

    def submit_application(self, user_key, is_self_register, channel_id):
        post_data = {"userKey": user_key, "productType": 0, "isSelfRegister": is_self_register}
        if channel_id is not None:
            post_data["channelId"] = channel_id
        response = requests.post(self.base_URL + "/incommingApplication/submitApplication", data=post_data, headers=self.headers)
        response.raise_for_status()
        parsed_response = SubmitApplicationResponse()
        return parsed_response.parse(response)

    def load_application_status(self, application_id):
        post_data = {"applicationId": application_id}
        response = requests.post(self.base_URL + "/incommingApplication/loadApplicationStatus", data=post_data, headers=self.headers)
        response.raise_for_status()
        parsed_response = LoadApplicationStatusResponse()
        return parsed_response.parse(response)

    def change_application_status(self, application_id, user_key, operate_enum, to_status):
        post_data = {"applicationId": application_id, "userKey": user_key, "operateEnum" : operate_enum, "toStatus" : to_status}
        response = requests.post(self.base_URL + "/incommingApplication/changeApplicationStatus", data=post_data, headers=self.headers)
        response.raise_for_status()
        return response

    @staticmethod
    def get_all_valid_investigate_result():
        results = {'realNameInvResult': 'VALID', 'companyInvResult': 'VALID', 'workPositionInvResult': 'VALID',
                   'monthlySalaryInvResult': 'VALID', 'workPhoneInvResult': 'VALID', 'graduationInvResult': 'VALID',
                   'universityInvResult': 'VALID', 'graduateYearInvResult': 'VALID', 'marriageStatusInvResult': 'VALID',
                   'childStatusInvResult': 'VALID', 'addressInvResult': 'VALID', 'phoneInvResult': 'VALID',
                   'hasCarInvResult': 'VALID', 'hasHouseInvResult': 'VALID', 'urgentNameInvResult': 'VALID',
                   'urgentRelationInvResult': 'VALID', 'urgentMobileInvResult': 'VALID',
                   'creditCardNumberInvResult': 'VALID'}

        return results

    @staticmethod
    def get_all_notmatch_investigate_result():
        results = {'realNameInvResult': 'NOTMATCH', 'companyInvResult': 'NOTMATCH', 'workPositionInvResult': 'NOTMATCH',
                   'monthlySalaryInvResult': 'NOTMATCH', 'workPhoneInvResult': 'NOTMATCH', 'graduationInvResult': 'NOTMATCH',
                   'universityInvResult': 'NOTMATCH', 'graduateYearInvResult': 'NOTMATCH', 'marriageStatusInvResult': 'NOTMATCH',
                   'childStatusInvResult': 'NOTMATCH', 'addressInvResult': 'NOTMATCH', 'phoneInvResult': 'NOTMATCH',
                   'hasCarInvResult': 'NOTMATCH', 'hasHouseInvResult': 'NOTMATCH', 'urgentNameInvResult': 'NOTMATCH',
                   'urgentRelationInvResult': 'NOTMATCH', 'urgentMobileInvResult': 'NOTMATCH',
                   'creditCardNumberInvResult': 'NOTMATCH'}

        return results
