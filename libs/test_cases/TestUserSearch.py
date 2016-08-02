# -*- coding: utf-8 -*-

from ..DB_utils import utils
from .. import helper
from nose import tools
from ..global_enum import *
from ..model import user_search_result


class TestUserSearch:

    def __init__(self):
        pass

    def test_user_search(self):
        user_verify_status = utils.search_user(SearchType.NickName, '后台', VerifyUserStatus.VERIFY_SUCCESS.name)
        user_search_results = []
        for i in user_verify_status:
            usr = user_search_result.UserSearchResult()
            usr.user_id = i[0]
            usr.nick_name = i[1]
            usr.real_name = i[2]
            usr.mobile = i[3]
            usr.id_no = i[4]
            usr.channel = Channel.get_value(i[5])
            usr.verify_user_status = VerifyUserStatus.get_value(i[6])
            (operator, operate_time) = utils.get_latest_verify_user_status_log(usr.user_id)
            usr.operator = operator
            usr.operate_time = operate_time.strftime('%Y-%m-%d %H:%M')
            user_search_results.append(usr)
