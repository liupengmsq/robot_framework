# -*- coding: utf-8 -*-

import mysql.connector
from .. import global_config
from .. import helper
import json


class MockDataBase(object):

    def __init__(self, data_type, card_num, mock_response='', need_sleep=0, sleep_time=0):
        self.data_type = data_type
        self.mock_response = mock_response
        self.need_sleep = need_sleep
        self.sleep_time = sleep_time
        self.card_num = card_num

    def query_db(self, query):
        conn = mysql.connector.connect(
            user=global_config.mock_db_user_name,
            password=global_config.mock_db_password,
            host=global_config.mock_db_host,
            port=global_config.mock_db_port,
            database=global_config.mock_db_database,
            charset='utf8',
            buffered=True)
        conn.autocommit = True
        cursor = conn.cursor()

        try:
            cursor.execute(query)
            conn.commit()
        except Exception, e:
            helper.log_error('\n\n执行sql语句时出错: %s，回滚\n' % (e,))
            conn.rollback()
        finally:
            conn.close()

    def delete_data(self):
        self.query_db("delete from usernature where data_type = %s and card = '%s'" % (self.data_type, self.card_num))

    def insert_data(self):
        self.query_db(
            """
            INSERT INTO `usernature` (`card`, `data_type`, `response`, `need_sleep`, `sleep_time`) VALUES ('%s', %s, '%s', %s, %s)
            """
            % (self.card_num, self.data_type, self.mock_response, self.need_sleep, self.sleep_time))

    def update_response(self, mock_response):
        self.mock_response = mock_response
        self.delete_data()
        self.insert_data()


class JuxinliIdCard(MockDataBase):

    def __init__(self, id_card_num):
        MockDataBase.__init__(self, 5, id_card_num)

    def write_query_error_black_list_response(self):
        mock_data = {
              "status": "fail",
              "update_time": helper.current_data_time_str(),
              "request_args": [ { "org": "juxinli" }, { "id_card": self.card_num}, { "name": "陈殿铎" } ],
              "error_code": 123,
              "error_msg": "接口返回异常" }
        self.update_response(json.dumps(mock_data, ensure_ascii=False))

    def write_hit_black_list_response(self):
        mock_data = {
            "status": "success",
            "update_time": helper.current_data_time_str(),
            "request_args": [ { "org": "juxinli" }, { "id_card": self.card_num }, { "name": "陈殿铎" }],
            "error_code": 31200,
            "error_msg": "查询成功",
            "result": {
                "update_time": helper.current_data_time_str(),
                "name": "mock测试",
                "id_card": self.card_num,
                "channel_key": "31e220029b96c90e2ee414e24432469ad487922a",
                "create_time": helper.current_data_time_str(),
                "categories": [ "银行", "拍拍贷", "网贷" ],
                "others": { "地址": "浙江", "累计借入本金": "¥1,000.00", "性别": "男", "最大逾期天数": "40 天" },
                "debt": 1000,
                "mobiles": [ "18668930619" ]}}
        self.update_response(json.dumps(mock_data, ensure_ascii=False))

    def write_not_hit_black_list_response(self):
        mock_data = {
            "status": "success",
            "update_time": helper.current_data_time_str(),
            "request_args": [ { "org": "juxinli" }, { "id_card": self.card_num }, { "name": "李馨浩" }],
            "error_code": 31200,
            "error_msg": "此人不在黑名单",
            "result": {}}
        self.update_response(json.dumps(mock_data, ensure_ascii=False))


class JuxinliMobile(MockDataBase):

    def __init__(self, cell_phone_num):
        MockDataBase.__init__(self, 4, cell_phone_num)

    def write_hit_black_list_response(self):
        mock_data = {
            "status": "success",
            "update_time": helper.current_data_time_str(),
            "request_args": [{"mobile": self.card_num}, {"org": "juxinli"}, { "name": "郑春美子" }],
            "error_code": 31200,
            "error_msg": "查询成功",
            "result": {
                "mobile": self.card_num,
                "update_time": helper.current_data_time_str(),
                "create_time": helper.current_data_time_str(),
                "name": "郑春美子",
                "categories": [ "银行", "法院" ]}}
        self.update_response(json.dumps(mock_data, ensure_ascii=False))

    def write_not_hit_black_list_response(self):
        mock_data = {
            "status": "success",
            "update_time": helper.current_data_time_str(),
            "request_args": [ { "mobile": self.card_num }, { "org": "juxinli" }, { "name": "郑春美" } ],
            "error_code": 31200,
            "error_msg": "此人不在黑名单",
            "result": {}}
        self.update_response(json.dumps(mock_data, ensure_ascii=False))

    def write_query_error_black_list_response(self):
        mock_data = {
            "status": "fail",
            "update_time": helper.current_data_time_str(),
            "request_args": [ { "org": "juxinli" }, { "id_card": "37***219840406*635" }, { "name": "陈殿铎" } ],
            "error_code": 123,
            "error_msg": "接口返回异常"}
        self.update_response(json.dumps(mock_data, ensure_ascii=False))


class ZhongchengxinOnlineStatus(MockDataBase):

    def __init__(self, id_card_num):
        MockDataBase.__init__(self, 3, id_card_num)
