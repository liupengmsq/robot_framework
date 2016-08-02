import requests
import verify


class CouponRequest(verify.VerifyRequest):

    def create_coupon_batch(self, name, department, discount_type, amount, coupon_count, user_scope, time_type, start_time, end_time, validity_period, validity_type, grant_type, active_action):
        post_data = {"name": name,
                     "department": department,
                     "discountType": discount_type,
                     "amount": amount,
                     "couponsCnt": coupon_count,
                     "userScope": user_scope,
                     "timeType": time_type,
                     "startTime": start_time,
                     "endTime": end_time,
                     "validityPeriod": validity_period,
                     "validityType": validity_type,
                     "grantType": grant_type}
        if grant_type == 'SYSTEM':
            post_data["activeAction"] = active_action
        response = requests.post(self.base_URL + "/coupons/addBatch", data=post_data, headers=self.headers)
        response.raise_for_status()
        return response

    def create_fixed_time_coupon_batch(self, name, amount, coupon_count, start_time, end_time, grant_type, active_action):
        return self.create_coupon_batch(name, 'MARKETING', 'FIXED_VALUE', amount, coupon_count, 'ALL_TYPES',
                                        'FIXED_TIME_PERIOD', start_time, end_time, 0, 'DAY', grant_type, active_action)

    def create_fixed_length_coupon_batch(self, name, amount, coupon_count, validity_period, validity_type, grant_type, active_action):
        return self.create_coupon_batch(name, 'MARKETING', 'FIXED_VALUE', amount, coupon_count, 'ALL_TYPES',
                                        'FIXED_LENGTH', '', '', validity_period, validity_type, grant_type, active_action)

    def create_fixed_time_system_coupon_batch(self, name, amount, coupon_count, start_time, end_time):
        return self.create_fixed_time_coupon_batch(name, amount, coupon_count, start_time, end_time, 'SYSTEM', 'REGISTER_VERIFY')

    def create_fixed_length_system_coupon_batch(self, name, amount, coupon_count, validity_period, validity_type):
        return self.create_fixed_length_coupon_batch(name, amount, coupon_count, validity_period, validity_type, 'SYSTEM', 'REGISTER_VERIFY')

    def create_fixed_time_manual_coupon_batch(self, name, amount, coupon_count, start_time, end_time):
        return self.create_fixed_time_coupon_batch(name, amount, coupon_count, start_time, end_time, 'MANUAL', '')

    def create_fixed_length_manual_coupon_batch(self, name, amount, coupon_count, validity_period, validity_type):
        return self.create_fixed_length_coupon_batch(name, amount, coupon_count, validity_period, validity_type, 'MANUAL', '')

    def get_coupon_batch_detail(self, batch_id):
        post_data = {'batchId': batch_id}
        response = requests.post(self.base_URL + "/coupons/getBatchDetail", data=post_data, headers=self.headers)
        response.raise_for_status()
        return response

    def get_coupon_receive_detail(self, batch_id, page_num=1, page_size=200, key='', value='', coupons_status=''):
        post_data = {'pageNum': page_num, 'pageSize': page_size, 'batchId': batch_id, 'key': key, 'value': value, 'couponsStatus': coupons_status}
        response = requests.post(self.base_URL + "/coupons/getCouponsReceiveDetail", data=post_data, headers=self.headers)
        response.raise_for_status()
        return response

    def get_coupon_batch_report(self, batch_id):
        post_data = {'batchId': batch_id}
        response = requests.post(self.base_URL + "/coupons/getBatchReport", data=post_data, headers=self.headers)
        response.raise_for_status()
        return response

    def get_coupon_batch_report_by_date(self, batch_id, page_num=1, page_size=200, start_time='', end_time=''):
        post_data = {'pageNum': page_num, 'pageSize': page_size, 'batchId': batch_id, 'start_time': start_time, 'end_time': end_time}
        response = requests.post(self.base_URL + "/coupons/getBatchReportByDate", data=post_data, headers=self.headers)
        response.raise_for_status()
        return response

    def disable_coupon_batch_by_batch_id(self, batch_id):
        post_data = {'batchId': batch_id}
        response = requests.post(self.base_URL + "/coupons/disableBatch", data=post_data, headers=self.headers)
        response.raise_for_status()
        return response
