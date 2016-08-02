# -*- coding: utf-8 -*-
from enum import Enum


class SearchType(Enum):
    NickName = "昵称"
    Mobile = "手机号"
    IdNum = "身份证"
    RealName = "姓名"

    @staticmethod
    def get_enum(value):
        for i, j in SearchType.__members__.items():
            if j.value == value:
                return j
        return None


class VerifyUserStatus(Enum):
    UNCOMMIT = "等待提交"
    INQUIREING = "等待调查"
    INQUIRE_SUCCESS = "等待一审"
    VERIFY_FAIL = "补件"
    FIRST_VERIFY_SUCCESS = "等待二审"
    FIRST_SEND_BACK = "一审退回"
    SECOND_SEND_BACK = "二审退回"
    VERIFY_REJECT = "退件"
    VERIFY_SUCCESS = "审核通过"

    @staticmethod
    def get_value(key):
        for i, j in VerifyUserStatus.__members__.items():
            if i == key:
                return j.value
        return None

    @staticmethod
    def get_enum(value):
        for i, j in VerifyUserStatus.__members__.items():
            if j.value == value:
                return j
        return None


class Channel(Enum):
    BD_IMPORT = "BD渠道用户"
    PERSONAL_REGISTER = "普通用户"

    @staticmethod
    def get_value(key):
        for i, j in Channel.__members__.items():
            if i == key:
                return j.value
        return None

    @staticmethod
    def get_enum(value):
        for i, j in VerifyUserStatus.__members__.items():
            if j.value == value:
                return j
        return None


class AuditUserStatusEnum(Enum):
    UNCOMMIT = "等待提交"
    INQUIREING = "首次调查"
    FIRST_SEND_BACK = "退回调查"
    VERIFY_FAIL = "补件"
    VERIFY_FAIL_INQUIREING = "补件调查"
    INQUIRE_SUCCESS = "待一审"
    SECOND_SEND_BACK = "退回一审"
    FIRST_VERIFY_SUCCESS = "二审"
    SECOND_VERIFY_SUCCESS = "上签"
    VERIFY_REJECT = "退件"
    VERIFY_SUCCESS = "审核通过"

    @staticmethod
    def get_value(key):
        for i, j in VerifyUserStatus.__members__.items():
            if i == key:
                return j.value
        return None

    @staticmethod
    def get_enum(value):
        for i, j in VerifyUserStatus.__members__.items():
            if j.value == value:
                return j
        return None


class VerifyJobInputType(Enum):
    SYSTEM_APPROVED = "0"
    HIT_QIANHAI_SYSTEM_REJECTED= "1"
    HIT_JUXINLI_SYSTEM_REJECTED= "2"
    HIT_QIANHAI_JUXINLI_SYSTEM_REJECTED= "3"
    GUOZHENGTONG_NO_INFO= "4"

    @staticmethod
    def get_enum(value):
        for i, j in VerifyJobInputType.__members__.items():
            if j.value == value:
                return j
        return None


class VerifyThirdPartyTypeEnum(Enum):
    # 国政通注册手机号-电信信息核查接口
    ID5_REGISTER_MOBILE = 5
    # 聚信立身份证黑名单
    JUXINLI_IDCARD = 6
    # 聚信立注册手机号黑名单
    JUXINLI_REGISTER_MOBILE = 7
    # 聚信立预留手机号黑名单
    JUXINLI_RESERVED_MOBILE = 8
    # 国政通预留手机号-电信信息核查接口
    ID5_OBLIGATE_MOBILE = 9
    # 前海征信身份证号数据接口
    QHZX_CARD_NUMBER = 10
    # 中诚注册手机在线时长
    ZCX_REGISTER_ONLINE_TIME = 11
    # 中诚信预留手机在线时长
    ZCX_RESVERE_ONLINE_TIME = 12
    # 中诚信注册手机号实名制认证
    ZCX_REGISTER_REAL_NAME = 13
    # 中诚信预留手机号实名制认证
    ZCX_RESVERE_REAL_NAME = 14
    # 银联智惠用户画像关系认证
    UNION_PAY_SMART_USER_NATURE_24 = 15
    # 有信黑名单
    YOUXIN_BLACK_LIST = 16

    @staticmethod
    def get_value(key):
        for i, j in VerifyThirdPartyTypeEnum.__members__.items():
            if i == key:
                return j.value
        return None

    @staticmethod
    def get_enum(value):
        for i, j in VerifyThirdPartyTypeEnum.__members__.items():
            if j.value == value:
                return j
        return None

    @staticmethod
    def get_string(value):
        for i, j in VerifyThirdPartyTypeEnum.__members__.items():
            if j == value:
                return i
        return None

if __name__ == "__main__":
    print VerifyThirdPartyTypeEnum.get_string(VerifyThirdPartyTypeEnum.JUXINLI_IDCARD)
