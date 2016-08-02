from libs.test_cases.TestCoupon import *


class VerifyCoupon(object):

    def __init__(self):
        self.test_coupon = TestCoupon()

    def my_setup(self):
        self.test_coupon.setup()

    def my_cleanup(self):
        self.test_coupon.teardown()

    def create_fixed_time_coupon_batch(self):
        self.test_coupon.test_create_fixed_time_coupon_batch()

    def create_fixed_length_coupon_batch(self):
        self.test_coupon.test_create_fixed_length_coupon_batch()

    def system_fixed_time_coupon_grant(self):
        self.test_coupon.test_system_fixed_time_coupon_grant()

    def system_fixed_length_coupon_grant(self):
        self.test_coupon.test_system_fixed_length_coupon_grant()

    def disable_and_in_time_range_system_fixed_length_coupon_grant(self):
        self.test_coupon.test_disable_and_in_time_range_system_fixed_length_coupon_grant()

    def disable_and_not_in_time_range_system_fixed_length_coupon_grant(self):
        self.test_coupon.test_disable_and_not_in_time_range_system_fixed_length_coupon_grant()

    def disable_and_in_time_range_system_fixed_time_coupon_grant(self):
        self.test_coupon.test_disable_and_in_time_range_system_fixed_time_coupon_grant()

    def disable_and_not_in_time_range_system_fixed_time_coupon_grant(self):
        self.test_coupon.test_disable_and_not_in_time_range_system_fixed_time_coupon_grant()
