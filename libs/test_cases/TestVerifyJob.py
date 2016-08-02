# -*- coding: utf-8 -*-

from ..request_utils import verify
from ..DB_utils.utils import *
from .. import helper
from nose import tools
import time
from ..model import verify_job_input_info
from ..global_enum import *


class TestSystemApprovedJob:

    def __init__(self):
        self.request = None
        self.init_job_name = 'applicationUserInitJob'
        self.income_job_name = 'incomeProcessingJob'
        self.policy_job_name = 'systemPolicyVerifyJob'
        self.credit_job_name = 'systemCreditVerifyJob'
        self.user_key = '5025375D22C426B987E1A9D67E03E01L'
        self.input_info_csv_file_path = '/home/peng/Desktop/test.csv'
        self.base_url = 'http://172.16.2.37:9080'
        self.executor_id = 69
        self.channel_id = 25

    def setup(self):
        self.request = verify.VerifyRequest(self.base_url)
        self._cleanup_application_data()

    def teardown(self):
        pass

    def test_verify_approved(self):
        user_info = self._get_input_info_by_type(VerifyJobInputType.SYSTEM_APPROVED)
        helper.log('读取用户信息，内容如下： %s' % user_info)

        helper.log('更改数据库中的用户信息')
        self._prepare_test_data(user_info)

        helper.log('提交进件')
        response = self.request.submit_application(self.user_key, 'false', self.channel_id)

        helper.log('检查提交进件的接口响应')
        tools.eq_(response.result_code, 'OK')
        tools.assert_not_equal(response.application_id, '')
        application_id = response.application_id

        helper.log('等待所有job运行完成')
        self._wait_for_job_done()

        response = self.request.load_application_status(application_id)
        helper.log('检查进件审核状态')
        tools.eq_(response.result_code, 'OK')
        tools.eq_(response.current_application_status, 'FAIL')
        tools.eq_(response.current_application_verify_status, 'SYSTEM_REJECT')
        tools.eq_(response.user_key, self.user_key)

        helper.log('更改状态为审核通过')
        with DBHelper() as db_helper:
            db_helper.update_verify_application_status(self.user_key, 'INIT_OK')
        self.request.change_application_status(application_id, self.user_key, 'SYSTEM_VERIFY', 'SYSTEM_VERIFY_PASS')
        self._wait_for_credit_job_done()

        response = self.request.load_application_status(application_id)
        helper.log('检查进件审核状态')
        tools.eq_(response.result_code, 'OK')
        tools.eq_(response.card_product_id, 5)
        tools.eq_(response.cash_amount_ratio, 0.0)
        tools.eq_(response.credit_limit , 3000.0)
        tools.eq_(response.current_application_status, 'SUCCESS')
        tools.eq_(response.current_application_verify_status, 'SYSTEM_APPROVED')
        tools.eq_(response.user_key, self.user_key)

        # helper.log('检查第三方接口调用结果')
        with DBHelper() as db_helper:
            application_pk_id = db_helper.get_application_pk_id_by_user_key(self.user_key)
        TestSystemApprovedJob._check_third_party_result_for_approved_user(application_pk_id)

    def _get_input_info_by_type(self, type):
        ret = verify_job_input_info.VerifyJobInputInfo.parse_from_csv(self.input_info_csv_file_path)
        for i in ret:
            if i.type == type:
                return i

    def _cleanup_application_data(self):
        helper.log('删除verify_process_task表中的数据, executor为%s' % self.executor_id)
        with DBHelper() as db_helper:
            db_helper.delete_verify_process_task_by_executor_id(self.executor_id)
            helper.log('获取进件主键id与进件id, 使用user_key: %s' % self.user_key)
            application_pk_id = db_helper.get_application_pk_id_by_user_key(self.user_key)
            application_id = db_helper.get_application_id_by_user_key(self.user_key)

            helper.log('删除verify_application_status, verify_application_status_log'
                            '与verify_application_user_info表中的数据, user_key为%s' % self.user_key)
            db_helper.delete_application_status_and_user_info_by_user_key(self.user_key)

            if application_id is not None:
                helper.log('删除策略输出表verify_policy_detail中application_id为%s' % application_id.encode('utf-8'))
                db_helper.delete_policy_detail_by_application_id(application_id.encode('utf-8'))

            if application_pk_id is not None:
                helper.log('删除第三方接口调用结果，进件主键id为%s' % application_pk_id)
                db_helper.delete_third_party_result_and_log_by_application_pk_id(application_pk_id)

    def _prepare_test_data(self, user_info):
        with DBHelper() as db_helper:
            db_helper.update_user_by_user_key(self.user_key, user_info.mobile)
            db_helper.update_idcard_info_by_user_key(self.user_key, user_info.id_number, user_info.real_name)
            db_helper.update_or_insert_edu_card_info_by_id_number(user_info.id_number, user_info.real_name)
            db_helper.update_user_bank_card_info_by_user_key(self.user_key, user_info.bank_number, user_info.bank_name, user_info.real_name, user_info.id_number, user_info.reserve_mobile)

    def _wait_for_job_done(self):
        with DBHelper() as db_helper:
            wait_time_for_job = db_helper.get_verify_job_interval_time_by_job_class_name(self.init_job_name)
            wait_time_for_job = wait_time_for_job + db_helper.get_verify_job_interval_time_by_job_class_name(self.income_job_name)
            wait_time_for_job = wait_time_for_job + db_helper.get_verify_job_interval_time_by_job_class_name(self.credit_job_name)
            wait_time_for_job = wait_time_for_job + db_helper.get_verify_job_interval_time_by_job_class_name(self.policy_job_name)
            time.sleep(wait_time_for_job/1000)

    def _wait_for_credit_job_done(self):
        with DBHelper() as db_helper:
            wait_time_for_job = db_helper.get_verify_job_interval_time_by_job_class_name(self.policy_job_name)
        time.sleep(wait_time_for_job/1000)

    @staticmethod
    def _check_third_party_result_for_approved_user(application_pk_id):
        with DBHelper() as db_helper:
            ret = db_helper.get_third_party_result_by_type(VerifyThirdPartyTypeEnum.JUXINLI_IDCARD, application_pk_id)
        tools.assert_is_not_none(ret)
        tools.assert_equal(2, len(ret))
        tools.assert_equal(ret[0], 'EXCHANGE_SUCCESS')
        tools.assert_equal(ret[1], """{"error_code":"31200","error_msg":"此人不在黑名单","result":"{}"}""")
