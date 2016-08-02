# -*- coding: utf-8 -*-

from libs.DB_utils.utils import *
from libs.request_utils import verify
from libs.request_utils import flow_task_manage
from libs.global_enum import *
from libs.model import user_search_result
from robot.libraries.BuiltIn import BuiltIn
import time


class VerifyLibrary(object):

    def __init__(self, base_URL, username, dubbo_web_base_URL=None):
        self.base_URL = base_URL
        self.username = username
        self.request_utils = verify.VerifyRequest(base_URL, username)
        self.flow_task_request_utils = flow_task_manage.FlowTaskManage(base_URL, username)
        self.built_in = BuiltIn()
        if dubbo_web_base_URL is not None:
            self.dubbo_web_request_utils = verify.VerifyRequest(dubbo_web_base_URL)

    def update_verify_user_role(self, email, dept_id, role_id, amount_limit=5000):
        with DBHelper() as db_helper:
            real_name = db_helper.get_verify_user_name_by_email(email)
            verify_user_id = db_helper.get_verify_user_id_by_email(email)
        self.request_utils.login()
        response = self.request_utils.update_verify_user(real_name, verify_user_id, amount_limit, dept_id, role_id)
        return response.json()

    def update_verify_user_mul_roles(self, email, dept_id, amount_limit, *role_ids):
        with DBHelper() as db_helper:
            real_name = db_helper.get_verify_user_name_by_email(email)
            verify_user_id = db_helper.get_verify_user_id_by_email(email)
        self.request_utils.login()
        response = self.request_utils.update_verify_user_to_mul_roles(real_name, verify_user_id, amount_limit, dept_id, *role_ids)
        return response.json()

    def compare_user_search_result(self, ui_row, ui_row_index, key, search_type, verify_user_status):
        ui_row_index = int(ui_row_index)
        key = key.encode('utf-8')
        search_type = search_type.encode('utf-8')
        verify_user_status = verify_user_status.encode('utf-8')

        # get user search result from DB
        with DBHelper() as db_helper:
            if verify_user_status is None:
                self.built_in.log(key)
                search_type_enum = SearchType.get_enum(search_type)
                user_verify_status = db_helper.search_user(search_type_enum, key)
            else:
                user_verify_status = db_helper.search_user(SearchType.get_enum(search_type), key, VerifyUserStatus.get_enum(verify_user_status).name)
            if len(user_verify_status) - 1 < ui_row_index:
                raise AssertionError('User search result from DB has count %s, but you want to get index %s' % (len(user_verify_status), ui_row_index))

        self.built_in.log('Start to fetch from DB')
        user_verify_status_index = user_verify_status[ui_row_index]
        usr_DB = user_search_result.UserSearchResult()
        usr_DB.user_id = unicode(user_verify_status_index[0])
        usr_DB.nick_name = user_verify_status_index[1]
        usr_DB.real_name = user_verify_status_index[2]
        usr_DB.mobile = user_verify_status_index[3]
        usr_DB.id_no = user_verify_status_index[4]
        usr_DB.channel = unicode(Channel.get_value(user_verify_status_index[5]), 'utf-8')
        usr_DB.verify_user_status = unicode(VerifyUserStatus.get_value(user_verify_status_index[6]), 'utf-8')
        if usr_DB.verify_user_status == u'等待提交' or usr_DB.verify_user_status == u'等待调查':
            self.built_in.log('Verify user status is uncommit or inquireing')
            usr_DB.operator = ''
            usr_DB.operate_time = ''
        else:
            self.built_in.log('Verify user status is NOT uncommit or inquireing')
            with DBHelper() as db_helper:
                operator_operate_time = db_helper.get_latest_verify_user_status_log(usr_DB.user_id)
            if operator_operate_time is not None and len(operator_operate_time) == 2:
                usr_DB.operator = operator_operate_time[0]
                usr_DB.operate_time = unicode(operator_operate_time[1].strftime('%Y-%m-%d %H:%M'), 'utf-8')
            else:
                usr_DB.operator = ''
                usr_DB.operate_time = ''

        self.built_in.log('Start to fetch from UI')
        usr_UI = user_search_result.UserSearchResult()
        usr_UI.user_id = ui_row['userId']
        usr_UI.nick_name = ui_row['nickName']
        usr_UI.real_name = ui_row['realName']
        usr_UI.mobile = ui_row['mobile']
        usr_UI.id_no = ui_row['idNo']
        usr_UI.channel = ui_row['userType']
        usr_UI.verify_user_status = ui_row['verifyUserStatus']
        usr_UI.operator = ui_row['operator']
        usr_UI.operate_time = ui_row['operateTime']

        self.built_in.log('Start to compare them')
        if usr_DB == usr_UI:
            return
        else:
            raise AssertionError('User search result from DB and UI are different for row index %s !!' % ui_row_index)

    def update_verify_user_status(self, user_id, verify_user_status):
        user_id = int(user_id)
        verify_user_status = VerifyUserStatus.get_enum(verify_user_status.encode('utf-8'))
        with DBHelper() as db_helper:
            if verify_user_status == VerifyUserStatus.UNCOMMIT:
                db_helper.update_user_to_uncommit_status(user_id)
                return
            if verify_user_status == VerifyUserStatus.INQUIREING:
                db_helper.update_user_to_inquireing_status(user_id)
                return
            if verify_user_status == VerifyUserStatus.INQUIRE_SUCCESS:
                db_helper.update_user_to_inquire_success_status(user_id)
                return
            if verify_user_status == VerifyUserStatus.VERIFY_FAIL:
                db_helper.update_user_to_verify_fail_status(user_id)
                return
            if verify_user_status == VerifyUserStatus.FIRST_VERIFY_SUCCESS:
                db_helper.update_user_to_first_verify_success_status(user_id)
                return
            if verify_user_status == VerifyUserStatus.FIRST_SEND_BACK:
                db_helper.update_user_to_first_verify_sendback_status(user_id)
                return
            if verify_user_status == VerifyUserStatus.VERIFY_SUCCESS:
                db_helper.update_user_to_second_verify_success_status(user_id)
                return
            if verify_user_status == VerifyUserStatus.SECOND_SEND_BACK:
                db_helper.update_user_to_second_verify_sendback(user_id)
                return
            if verify_user_status == VerifyUserStatus.VERIFY_REJECT:
                db_helper.update_user_to_second_verify_reject(user_id)
                return
            raise AssertionError('No code can handle verify user status!!')

    def cleanup_task_by_executor_names(self, *names):
        with DBHelper() as db_helper:
            for name in names:
                name = name.encode('utf-8')
                verify_user_id = db_helper.get_verify_user_id_by_real_name(name)
                db_helper.delete_verify_process_task_by_executor_id(verify_user_id)

    def populate_task_by_nick_names(self, *nick_names):
        with DBHelper() as db_helper:
            for nick_name in nick_names:
                nick_name = nick_name.encode('utf-8')
                user_id = db_helper.get_user_id_by_nick_name(nick_name)
                db_helper.update_user_to_inquireing_status(user_id)
                db_helper.delete_verify_user_status_by_user_id(user_id)
                self.dubbo_web_request_utils.init_user_from_mobile(user_id)
                self.dubbo_web_request_utils.commit_user_from_mobile(user_id)
                time.sleep(1)

    def commit_user_by_nick_names(self, *nick_names):
        with DBHelper() as db_helper:
            for nick_name in nick_names:
                nick_name = nick_name.encode('utf-8')
                user_id = db_helper.get_user_id_by_nick_name(nick_name)
                self.dubbo_web_request_utils.commit_user_from_mobile(user_id)
                time.sleep(1)

    # 按人员, 首次调查
    def flow_setup_by_people_for_inquireing(self, *verify_user_names):
        self._flow_setup_by_people(AuditUserStatusEnum.INQUIREING, *verify_user_names)

    # 按人员, 待一审
    def flow_setup_by_people_for_inquire_success(self, *verify_user_names):
        self._flow_setup_by_people(AuditUserStatusEnum.INQUIRE_SUCCESS, *verify_user_names)

    # 按人员, 待二审
    def flow_setup_by_people_for_first_verify_success(self, *verify_user_names):
        self._flow_setup_by_people(AuditUserStatusEnum.FIRST_VERIFY_SUCCESS, *verify_user_names)

    # 按人员, 上签
    def flow_setup_by_people_for_second_verify_success(self, *verify_user_names):
        self._flow_setup_by_people(AuditUserStatusEnum.SECOND_VERIFY_SUCCESS, *verify_user_names)

    def _flow_setup_by_people(self, audit_user_status, *verify_user_names):
        user_name_encoded = [i.encode('utf-8') for i in verify_user_names]
        with DBHelper() as db_helper:
            values_in_integer = [db_helper.get_verify_user_id_by_real_name(i) for i in user_name_encoded]
        self.built_in.log('Values for flow setup: ' + str(values_in_integer))
        self.flow_task_request_utils.login()

        if audit_user_status == AuditUserStatusEnum.INQUIREING:
            response = self.flow_task_request_utils.flow_setup_by_people_for_inquireing(*values_in_integer)
        elif audit_user_status == AuditUserStatusEnum.INQUIRE_SUCCESS:
            response = self.flow_task_request_utils.flow_setup_by_people_for_inquire_success(*values_in_integer)
        elif audit_user_status == AuditUserStatusEnum.FIRST_VERIFY_SUCCESS:
            response = self.flow_task_request_utils.flow_setup_by_people_for_first_verify_sucess(*values_in_integer)
        elif audit_user_status == AuditUserStatusEnum.SECOND_VERIFY_SUCCESS:
            response = self.flow_task_request_utils.flow_setup_by_people_for_second_verify_sucess(*values_in_integer)
        else:
            raise AssertionError('Can not handle other audit user status!!')
        self.built_in.log('Response for flow setup: ' + str(response))

    # 将指定的审核用户分配多个角色id
    def assign_verify_user_to_mul_roles(self, verify_user_real_name, *role_ids):
        with DBHelper() as db_helper:
            email = db_helper.get_verify_user_email_by_real_name(verify_user_real_name.encode('utf-8'))
        self.update_verify_user_mul_roles(email, 1, 5000, *role_ids)

    # 按角色, 首次调查
    def flow_setup_by_role_for_inquireing(self, role_id):
        self._flow_setup_by_role(AuditUserStatusEnum.INQUIREING, role_id)

    # 按角色, 待一审
    def flow_setup_by_role_for_inquire_success(self, role_id):
        self._flow_setup_by_role(AuditUserStatusEnum.INQUIRE_SUCCESS, role_id)

    # 按角色, 待二审
    def flow_setup_by_role_for_first_verify_success(self, role_id):
        self._flow_setup_by_role(AuditUserStatusEnum.FIRST_VERIFY_SUCCESS, role_id)

    # 按角色, 上签
    def flow_setup_by_role_for_second_verify_success(self, role_id):
        self._flow_setup_by_role(AuditUserStatusEnum.SECOND_VERIFY_SUCCESS, role_id)

    def _flow_setup_by_role(self, audit_user_status, role_id):
        role_id = int(role_id)
        self.flow_task_request_utils.login()
        self.built_in.log('Start to set flow task by role')
        if audit_user_status == AuditUserStatusEnum.INQUIREING:
            response = self.flow_task_request_utils.flow_setup_by_role_for_inquireing(role_id)
        elif audit_user_status == AuditUserStatusEnum.INQUIRE_SUCCESS:
            response = self.flow_task_request_utils.flow_setup_by_role_for_inquire_success(role_id)
        elif audit_user_status == AuditUserStatusEnum.FIRST_VERIFY_SUCCESS:
            response = self.flow_task_request_utils.flow_setup_by_role_for_first_verify_sucess(role_id)
        elif audit_user_status == AuditUserStatusEnum.SECOND_VERIFY_SUCCESS:
            response = self.flow_task_request_utils.flow_setup_by_role_for_second_verify_sucess(role_id)
        else:
            raise AssertionError('Can not handle other audit user status!!')
        self.built_in.log('Response for flow setup: ' + str(response))

    # 验证待办任务
    def verify_pending_job(self, verify_user_name, expected_task_with_nick_name, expected_task_name):
        self._verify_task('pending', verify_user_name, expected_task_with_nick_name, expected_task_name)

    # 验证办结任务
    def verify_done_job(self, verify_user_name, expected_task_with_nick_name, expected_task_name):
        self._verify_task('done', verify_user_name, expected_task_with_nick_name, expected_task_name)

    # 验证我参与的进件的任务
    def verify_involved_job(self, verify_user_name, expected_task_with_nick_name, expected_task_name):
        self._verify_task('involved', verify_user_name, expected_task_with_nick_name, expected_task_name)

    def _verify_task(self, task_type, verify_user_name, expected_task_with_nick_name, expected_task_name):
        verify_user_name = verify_user_name.encode('utf-8')
        expected_task_with_nick_name = expected_task_with_nick_name.encode('utf-8')

        with DBHelper() as db_helper:
            email = db_helper.get_verify_user_email_by_real_name(verify_user_name)
        self.built_in.log('Using user name {0} to log in'.format(email))
        flow_task_request_for_current_user = flow_task_manage.FlowTaskManage(self.base_URL, email)
        flow_task_request_for_current_user.login()

        if task_type == 'pending':
            tasks = flow_task_request_for_current_user.get_pending_tasks()[0]
        elif task_type == 'done':
            tasks = flow_task_request_for_current_user.get_done_tasks()[0]
        elif task_type == 'involved':
            tasks = flow_task_request_for_current_user.get_involved_tasks()[0]
        else:
            raise AssertionError('There is no this kind of type %s' % task_type)

        self.built_in.log('{0} task for user {1}: {2}'.format(task_type, email, tasks))
        self.built_in.log('Start to verify returned tasks')
        for task in tasks:
            if task['nickName'] == expected_task_with_nick_name and task['taskName'] == expected_task_name:
                return
        raise AssertionError('Fail to find nick name in task!!')

    # 获取待办任务数
    def get_pending_task_count(self, verify_user_name):
        return self._get_task_count('pending', verify_user_name)

    # 获取办结任务数
    def get_done_task_count(self, verify_user_name):
        return self._get_task_count('done', verify_user_name)

    # 获取我参与的进件任务数
    def get_involved_task_count(self, verify_user_name):
        return self._get_task_count('involved', verify_user_name)

    def _get_task_count(self, task_type, verify_user_name):
        verify_user_name = verify_user_name.encode('utf-8')
        with DBHelper() as db_helper:
            email = db_helper.get_verify_user_email_by_real_name(verify_user_name)
        self.built_in.log('Using user name {0} to log in'.format(email))
        flow_task_request_for_current_user = flow_task_manage.FlowTaskManage(self.base_URL, email)
        flow_task_request_for_current_user.login()

        if task_type == 'pending':
            return flow_task_request_for_current_user.get_pending_tasks()[1]
        elif task_type == 'done':
            return flow_task_request_for_current_user.get_done_tasks()[1]
        elif task_type == 'involved':
            return flow_task_request_for_current_user.get_involved_tasks()[1]
        else:
            raise AssertionError('There is no this kind of type %s' % task_type)

    # 将任务提交到一审，即调查通过
    def commit_to_first_verify(self, verify_user_real_name,  *task_nick_names):
        self._commit_to_next_verify_status(AuditUserStatusEnum.INQUIRE_SUCCESS, verify_user_real_name, 0, *task_nick_names)

    # 调查补件
    def commit_to_verify_fail(self, verify_user_real_name,  *task_nick_names):
        self._commit_to_next_verify_status(AuditUserStatusEnum.VERIFY_FAIL, verify_user_real_name, 0, *task_nick_names)

    # 将任务提交到二审，即一审通过
    def commit_to_second_verify(self, verify_user_real_name,  *task_nick_names):
        self._commit_to_next_verify_status(AuditUserStatusEnum.FIRST_VERIFY_SUCCESS, verify_user_real_name, 0, *task_nick_names)

    # 提交到一审退回
    def commit_to_first_verify_back(self, verify_user_real_name,  *task_nick_names):
        self._commit_to_next_verify_status(AuditUserStatusEnum.FIRST_SEND_BACK, verify_user_real_name, 0, *task_nick_names)

    # 将任务提交二审通过，具体是通过审核，还是上签，由二审金额决定
    def commit_to_pass_second_verify(self, verify_user_real_name, amount,  *task_nick_names):
        amount = int(amount)
        self._commit_to_next_verify_status(AuditUserStatusEnum.SECOND_VERIFY_SUCCESS, verify_user_real_name, amount, *task_nick_names)

    # 提交到二审退回
    def commit_to_second_verify_back(self, verify_user_real_name,  *task_nick_names):
        self._commit_to_next_verify_status(AuditUserStatusEnum.SECOND_SEND_BACK, verify_user_real_name, 0, *task_nick_names)

    # 将任务提交三审通过
    def commit_to_pass_third_verify(self, verify_user_real_name, amount,  *task_nick_names):
        amount = int(amount)
        self._commit_to_next_verify_status(AuditUserStatusEnum.VERIFY_SUCCESS, verify_user_real_name, amount, *task_nick_names)

    # 上签退件
    def commit_to_refuse(self, verify_user_real_name, *task_nick_names):
        self._commit_to_next_verify_status(AuditUserStatusEnum.VERIFY_REJECT, verify_user_real_name, 0, *task_nick_names)

    def _commit_to_next_verify_status(self, audit_user_status, verify_user_real_name, second_verify_amount=1000,  *task_nick_names):
        self.built_in.log('Encoding for task nick name ' + str(task_nick_names))
        task_nick_names_encode = [i.encode('utf-8') for i in task_nick_names]

        self.built_in.log('Getting user id by nick name')
        with DBHelper() as db_helper:
            user_ids = [db_helper.get_user_id_by_nick_name(i) for i in task_nick_names_encode]

        self.built_in.log('Getting verify user email by real name')
        with DBHelper() as db_helper:
            verify_user_email = db_helper.get_verify_user_email_by_real_name(verify_user_real_name.encode('utf-8'))

        self.built_in.log('Using verify user {0} to log in'.format(verify_user_email))
        current_user_request = verify.VerifyRequest(self.base_URL, verify_user_email)
        current_user_request.login()

        for user_id in user_ids:
            self.built_in.log('Using user_id = {0} to commit to {1}'.format(user_id, audit_user_status))
            if audit_user_status == AuditUserStatusEnum.INQUIRE_SUCCESS:
                inv_rets = current_user_request.get_all_valid_investigate_result()
                response = current_user_request.commit_to_first_verify(user_id, 12, '调查备注', **inv_rets)
            elif audit_user_status == AuditUserStatusEnum.VERIFY_FAIL:
                inv_rets = current_user_request.get_all_notmatch_investigate_result()
                response = current_user_request.commit_to_verify_fail(user_id, 12, '补件调查', **inv_rets)
            elif audit_user_status == AuditUserStatusEnum.FIRST_VERIFY_SUCCESS:
                response = current_user_request.commit_to_second_verify(user_id, 1000, 1, 12, '一审备注')
            elif audit_user_status == AuditUserStatusEnum.FIRST_SEND_BACK:
                response = current_user_request.commit_to_first_verify_sendback(user_id, '一审退回')
            elif audit_user_status == AuditUserStatusEnum.SECOND_VERIFY_SUCCESS:
                response = current_user_request.commit_to_pass_second_verify(user_id, second_verify_amount, 1, 12, '二审备注')
            elif audit_user_status == AuditUserStatusEnum.SECOND_SEND_BACK:
                response = current_user_request.commit_to_second_verify_sendback(user_id, '二审退回')
            elif audit_user_status == AuditUserStatusEnum.VERIFY_SUCCESS:
                response = current_user_request.commit_to_pass_signed_approval(user_id, second_verify_amount, 1, 12, '最终审核通过')
            elif audit_user_status == AuditUserStatusEnum.VERIFY_REJECT:
                response = current_user_request.commit_to_refuse(user_id, 'A01', '退件')
            else:
                raise AssertionError('Can not handle this kind of status!!')
            self.built_in.log('Response = {0}'.format(response.json()))

    # 比较审核流水中个人信息部分
    def compare_user_info_for_verify_log(self, nick_name):
        nick_name = nick_name.encode('utf-8')
        with DBHelper() as db_helper:
            user_id = db_helper.get_user_id_by_nick_name(nick_name)
        self.request_utils.login()
        result_from_api = self.request_utils.get_user_verify_logs(user_id)
        user_info_from_api = result_from_api.json()['data']['userInfo']
        with DBHelper() as db_helper:
            user_info_from_db = db_helper.get_user_info_for_verify_log(nick_name)
        self.built_in.should_be_equal_as_strings(user_info_from_api['nickName'], user_info_from_db[0], 'Compare nick name for user info in verify log')
        self.built_in.should_be_equal_as_strings(user_info_from_api['realName'], user_info_from_db[1], 'Compare real name for user info in verify log')
        self.built_in.should_be_equal_as_strings(user_info_from_api['mobile'], user_info_from_db[2], 'Compare mobile for user info in verify log')
        self.built_in.should_be_equal_as_strings(user_info_from_api['idNo'], user_info_from_db[3], 'Compare idNo for user info in verify log')
        self.built_in.should_be_equal_as_strings(user_info_from_api['userType'], unicode(Channel.get_value(user_info_from_db[4]), 'utf-8'), 'Compare channel for user info in verify log')
        self.built_in.should_be_equal_as_strings(user_info_from_api['verifyUserStatus'], unicode(VerifyUserStatus.get_value(user_info_from_db[5]), 'utf-8'), 'Compare verify user status for user info in verify log')

    # 比较审核流水中每个审核阶段的结果
    def compare_verify_log(self, nick_name, index, operation, operation_result, verify_user=None, note=None, amount=None, level=None, cash_draw_ratio=None):
        nick_name = nick_name.encode('utf-8')
        index = int(index)

        with DBHelper() as db_helper:
            user_id = db_helper.get_user_id_by_nick_name(nick_name)
        self.request_utils.login()
        result_from_api = self.request_utils.get_user_verify_logs(user_id)
        verify_logs_from_api = result_from_api.json()['data']['userVerifyLog']

        self.built_in.log("User verify log: " + str(verify_logs_from_api))
        self.built_in.should_be_equal_as_strings(verify_logs_from_api[index]['operation'], operation, 'Compare operation for verify log')
        self.built_in.should_be_equal_as_strings(verify_logs_from_api[index]['operationResult'], operation_result, 'Compare operationResult for verify log')

        if verify_user is not None:
            self.built_in.should_be_equal_as_strings(verify_logs_from_api[index]['verifyUser'], verify_user, 'Compare verify user for verify log')
        if note is not None:
            self.built_in.should_be_equal_as_strings(verify_logs_from_api[index]['note'], note, 'Compare note for verify log')
        if amount is not None:
            self.built_in.should_be_equal_as_strings(verify_logs_from_api[index]['amount'], amount, 'Compare amount for verify log')
        if level is not None:
            self.built_in.should_be_equal_as_strings(verify_logs_from_api[index]['level'], level, 'Compare level for verify log')
        if cash_draw_ratio is not None:
            self.built_in.should_be_equal_as_strings(verify_logs_from_api[index]['cashDrawRatio'], cash_draw_ratio, 'Compare cashDrawRatio for verify log')

    # 获取审核流水中条目数
    def get_verify_log_count(self, nick_name):
        nick_name = nick_name.encode('utf-8')
        with DBHelper() as db_helper:
            user_id = db_helper.get_user_id_by_nick_name(nick_name)
        self.request_utils.login()
        result_from_api = self.request_utils.get_user_verify_logs(user_id)
        return len(result_from_api.json()['data']['userVerifyLog'])

    # 更新用户类型为个人
    def update_user_channel_type_to_personal_register(self, nick_name):
        with DBHelper() as db_helper:
            user_id = db_helper.get_user_id_by_nick_name(nick_name.encode('utf-8'))
            db_helper.update_user_channel_by_user_id(user_id, Channel.PERSONAL_REGISTER)

    # 更新用户类型为BD导入
    def update_user_channel_type_to_db_import(self, nick_name):
        with DBHelper() as db_helper:
            user_id = db_helper.get_user_id_by_nick_name(nick_name.encode('utf-8'))
            db_helper.update_user_channel_by_user_id(user_id, Channel.BD_IMPORT)

    # 获取接口返回的待办任务
    def get_pending_task(self, index):
        return self.flow_task_request_utils.get_pending_tasks()[0][index]


if __name__ == "__main__":
    verify_library = VerifyLibrary('http://172.16.2.38:15081', 'admin@renrendai.com')
    verify_library.update_verify_user_role('auto_permission_tes@rernedai.com', 26, 12)
    verify_library.compare_user_search_result({'userType': u'\u666e\u901a\u7528\u6237', 'idNo': u'130521199307091000', 'operateTime': u'2015-12-08 15:45', 'verifyUserStatus': u'\u7b49\u5f85\u4e00\u5ba1', 'realName': u'\u65bd\u65ed\u5b81', 'mobile': u'13146865530', 'nickName': u'auto_01', 'userId': u'100034832', 'operator': u'\u5218\u9e4f\u6d4b\u8bd5'},
                                              0,
                                              'auto')
