# -*- coding: utf-8 -*-

from ..request_utils import coupon
from ..DB_utils import utils
from .. import helper
from nose import tools
import datetime
import time
from enum import Enum


class CouponBatchType(Enum):
    FixedTime = 1,
    FixedLength = 2


class TestCoupon:

    def __init__(self):
        self.request = None
        self.coupon_name = None
        self.nick_name = None
        self.user_key = None
        self.job_class_name = None

    def setup(self):
        self.request = coupon.CouponRequest('http://172.16.2.38:12081/')
        self.request.login()
        self.coupon_name = 'test_at'
        self.nick_name = 'auto_01'
        self.job_class_name = 'systemGrantCouponJob'
        self.user_key = utils.get_user_key_by_nick_name(self.nick_name)

    def teardown(self):
        utils.delete_coupon_batch_by_name(self.coupon_name)
        utils.delete_user_from_system_grant_coupon(self.user_key)
        utils.delete_all_system_grant_coupon()

    def test_create_fixed_time_coupon_batch(self):
        self._test_create_coupon_batch(CouponBatchType.FixedTime)

    def test_create_fixed_length_coupon_batch(self):
        self._test_create_coupon_batch(CouponBatchType.FixedLength)

    def _test_create_coupon_batch(self, batch_type):
        if batch_type == CouponBatchType.FixedTime:
            now = datetime.datetime.now()
            three_days_later = (now + datetime.timedelta(days=3)).strftime('%Y-%m-%d')
            now = now.strftime('%Y-%m-%d')
            response = self.request.create_fixed_time_system_coupon_batch(self.coupon_name, 12, 1000, now, three_days_later)
        if batch_type == CouponBatchType.FixedLength:
            response = self.request.create_fixed_length_system_coupon_batch(self.coupon_name, 12, 1000, 30, 'DAY')
        assert response.text is not None

        batch_key = utils.get_coupon_batch_key_by_name(self.coupon_name)
        batch_id = utils.get_coupon_batch_id_by_name(self.coupon_name)
        assert batch_key is not None
        assert batch_id is not None

        helper.log("Get batch from request")
        response = self.request.get_coupon_batch_detail(batch_id)
        coupon_batch_response = response.json()['data']['rows']
        tools.eq_(coupon_batch_response['batchStatus'], 1)
        tools.eq_(coupon_batch_response['couponsAmount'], 12.0)
        tools.eq_(coupon_batch_response['couponsCnt'], 1000)
        tools.eq_(coupon_batch_response['department'], 'MARKETING')
        tools.eq_(coupon_batch_response['grantType'], 'SYSTEM')
        tools.eq_(coupon_batch_response['id'], batch_id)
        tools.eq_(coupon_batch_response['name'], self.coupon_name)
        if batch_type == CouponBatchType.FixedTime:
            tools.eq_(coupon_batch_response['startTime'], now)
            tools.eq_(coupon_batch_response['endTime'], three_days_later)
        tools.eq_(coupon_batch_response['type'], 'VOUCHER')
        tools.eq_(coupon_batch_response['userScope'], ['ALL_TYPES'])
        response = self.request.get_coupon_receive_detail(batch_id)
        coupon_receive_detail_response = response.json()['data']['rows']
        tools.eq_(len(coupon_receive_detail_response), 0)

    def test_system_fixed_time_coupon_grant(self):
        self._test_grant_coupon(CouponBatchType.FixedTime)

    def test_system_fixed_length_coupon_grant(self):
        self._test_grant_coupon(CouponBatchType.FixedLength)

    def test_disable_and_in_time_range_system_fixed_length_coupon_grant(self):
        self._test_grant_coupon(CouponBatchType.FixedLength, True)

    def test_disable_and_not_in_time_range_system_fixed_length_coupon_grant(self):
        self._test_grant_coupon(CouponBatchType.FixedLength, True, False)

    def test_disable_and_in_time_range_system_fixed_time_coupon_grant(self):
        self._test_grant_coupon(CouponBatchType.FixedTime, True)

    def test_disable_and_not_in_time_range_system_fixed_time_coupon_grant(self):
        self._test_grant_coupon(CouponBatchType.FixedTime, True, False)

    def _test_grant_coupon(self, batch_type, disable_coupon_batch=False, need_to_grant_coupon=True):
        now = datetime.datetime.now()
        if batch_type == CouponBatchType.FixedTime:
            three_days_later = (now + datetime.timedelta(days=3)).strftime('%Y-%m-%d')
            now = now.strftime('%Y-%m-%d')
            response = self.request.create_fixed_time_system_coupon_batch(self.coupon_name, 12, 1000, now, three_days_later)
        if batch_type == CouponBatchType.FixedLength:
            thirty_days_later = (now + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
            now = now.strftime('%Y-%m-%d')
            response = self.request.create_fixed_length_system_coupon_batch(self.coupon_name, 12, 1000, 30, 'DAY')
        assert response.text is not None

        batch_key = utils.get_coupon_batch_key_by_name(self.coupon_name)
        batch_id = utils.get_coupon_batch_id_by_name(self.coupon_name)

        if disable_coupon_batch:
            # Disable coupon batch
            time.sleep(10)
            self.request.disable_coupon_batch_by_batch_id(batch_id)
            response = self.request.get_coupon_batch_detail(batch_id)
            coupon_batch_response = response.json()['data']['rows']
            tools.eq_(coupon_batch_response['batchStatus'], 0)

        if need_to_grant_coupon:
            register_time = (utils.get_start_time_in_coupon_activity_by_batch_key(batch_key) + datetime.timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            register_time = (utils.get_end_time_in_coupon_activity_by_batch_key(batch_key) + datetime.timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')

        user_key = utils.get_user_key_by_nick_name(self.nick_name)
        utils.update_user_register_time_to_current_by_user_key(register_time, user_key)
        utils.populate_user_into_system_grant_coupon(user_key)

        wait_time_for_job = utils.get_admin_job_interval_time_by_job_class_name(self.job_class_name)
        time.sleep(wait_time_for_job/1000)

        response = self.request.get_coupon_receive_detail(batch_id)
        user_entry = utils.get_user_entry_by_user_key(user_key)
        coupon_receive_detail_response = response.json()['data']['rows']
        if need_to_grant_coupon:
            tools.eq_(len(coupon_receive_detail_response), 1)
            tools.eq_(coupon_receive_detail_response[0]['couponsStatus'], 'UNUSED')
            tools.eq_(coupon_receive_detail_response[0]['startTime'], now)
            tools.eq_(coupon_receive_detail_response[0]['endTime'], three_days_later if batch_type == CouponBatchType.FixedTime else thirty_days_later)
            tools.eq_(coupon_receive_detail_response[0]['userId'], user_entry[0])
            tools.eq_(coupon_receive_detail_response[0]['mobile'], user_entry[6])
            tools.eq_(coupon_receive_detail_response[0]['nickName'], self.nick_name)
        else:
            tools.eq_(len(coupon_receive_detail_response), 0)

        response = self.request.get_coupon_batch_report(batch_id)
        batch_report_response = response.json()['data']['rows']
        tools.eq_(batch_report_response['grantAmount'], 12 if need_to_grant_coupon else 0)
        tools.eq_(batch_report_response['grantedNum'], 1 if need_to_grant_coupon else 0)
        tools.eq_(batch_report_response['invalidAmount'], 0)
        tools.eq_(batch_report_response['invalidCnt'], 0)
        tools.eq_(batch_report_response['name'], self.coupon_name)
        tools.eq_(batch_report_response['realUsedAmount'], 0)
        tools.eq_(batch_report_response['usedAmount'], 0)
        tools.eq_(batch_report_response['usedNum'], 0)

        response = self.request.get_coupon_batch_report_by_date(batch_id)
        batch_report_response_by_date = response.json()['data']['rows']
        if need_to_grant_coupon:
            tools.eq_(len(batch_report_response_by_date), 1)
            tools.eq_(batch_report_response_by_date[0]['grantAmount'], 12)
            tools.eq_(batch_report_response_by_date[0]['grantCnt'], 1)
            tools.eq_(batch_report_response_by_date[0]['invalidAmount'], 0)
            tools.eq_(batch_report_response_by_date[0]['invalidCnt'], 0)
            tools.eq_(batch_report_response_by_date[0]['realUsedAmount'], 0)
            tools.eq_(batch_report_response_by_date[0]['unusedCnt'], 1)
            tools.eq_(batch_report_response_by_date[0]['usedAmount'], 0)
            tools.eq_(batch_report_response_by_date[0]['usedNum'], 0)
        else:
            tools.eq_(len(batch_report_response_by_date), 0)
