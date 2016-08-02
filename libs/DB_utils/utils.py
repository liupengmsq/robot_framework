# -*- coding: utf-8 -*-

from .. import global_config
from .. import helper
from datetime import datetime
import mysql.connector
from .. import global_enum


class DBHelper(object):

    def __enter__(self):
        self.conn = mysql.connector.connect(
            user=global_config.db_user_name,
            password=global_config.db_password,
            host=global_config.db_host,
            port=global_config.db_port,
            database=global_config.db_database,
            charset='utf8',
            buffered=True)
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def commit(self, query):
        try:
            self.cursor.execute(query)
            self.conn.commit()
            helper.log("执行sql语句：\n%s\n影响行数：%d\n" % (query, self.cursor.rowcount))
            return self.cursor.rowcount
        except Exception, e:
            helper.log_error('\n\n执行sql语句%s时出错: %s，回滚\n' % (query, e))
            self.conn.rollback()

    def fetch_one(self, query):
        self.cursor.execute(query)
        ret = self.cursor.fetchone()
        if ret is not None and len(ret) > 0:
            return ret[0]
        return None

    def get_all_user(self):
        query = 'select * from user'
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_user_id_by_nick_name(self, nick_name):
        self.cursor.execute("select * from user where nick_name = '%s' " % nick_name)
        ret = self.cursor.fetchone()
        if ret is not None:
            return ret[0]
        return None

    def get_verify_user_id_by_email(self, email):
        self.cursor.execute("select id from verify_user where email = '%s' " % email)
        ret = self.cursor.fetchone()
        if ret is not None:
            return ret[0]
        return None

    def get_verify_user_name_by_email(self, email):
        self.cursor.execute("select real_name from verify_user where email = '%s' " % email)
        ret = self.cursor.fetchone()
        if ret is not None:
            return ret[0]
        return None

    def get_verify_user_email_by_real_name(self, real_name):
        self.cursor.execute("select email from verify_user where real_name = '%s' " % real_name)
        ret = self.cursor.fetchone()
        if ret is not None:
            return ret[0]
        return None

    def get_dept_id_by_dept_name(self, dept_name):
        self.cursor.execute("select id from verify_departments where department_name = '%s' " % dept_name)
        ret = self.cursor.fetchone()
        if ret is not None:
            return ret[0]
        return None

    def update_nick_name_by_user_id(self, user_id, nick_name):
        self.cursor.execute("update user set nick_name='%s' where user_id='%s'" % (nick_name, user_id))
        self.conn.commit()

    def update_nick_name_by_original_nick_name(self, original_nick_name, nick_name):
        self.cursor.execute("update user set nick_name='%s' where user_id='%s'" % (nick_name, original_nick_name))
        self.conn.commit()

    def update_nick_name(self, *original_nick_names):
        for nick_name in original_nick_names:
            user_id = self.get_user_id_by_nick_name(nick_name)
            if user_id is None:
                pass
            helper.log('获取一个user_id：%d' % user_id)
            if nick_name.startswith('rrd_'):
                new_nick_name = nick_name.replace('rrd_', '审核测试')
                helper.log('更新userId为%s的用户的昵称从%s更新为%s' % (user_id, nick_name, new_nick_name))
                self.update_nick_name_by_user_id(user_id, new_nick_name)

    def get_verify_user_status_id_by_user_id(self, user_id):
        helper.log('获取user_id为%s的verify_user_status表的主键id' % user_id)
        sql = "SELECT id from verify_user_status where user_id = %s" % user_id
        return self.fetch_one(sql)

    def get_verify_user_id_by_real_name(self, real_name):
        helper.log('获取real_name为%s的verify_user表的主键id' % real_name)
        sql = "SELECT id from verify_user where real_name = '%s'" % real_name
        return self.fetch_one(sql)

    def get_start_time_in_coupon_activity_by_batch_key(self, batch_key):
        sql = "SELECT start_time from admin_coupon_activity where batch_key = '%s'" % batch_key
        return self.fetch_one(sql)

    def get_end_time_in_coupon_activity_by_batch_key(self, batch_key):
        sql = "SELECT end_time from admin_coupon_activity where batch_key = '%s'" % batch_key
        return self.fetch_one(sql)

    def delete_verify_user_status_by_user_id(self, user_id):
        helper.log('删除verify_user_status表中的数据')
        delete_sql = "DELETE from verify_user_status where user_id = %s" % user_id
        self.commit(delete_sql)

    def delete_verify_process_task_by_verify_user_status_id(self, id):
        helper.log('按照verify_user_status_id删除verify_process_task表中的记录')
        delete_sql = "DELETE from verify_process_task where verify_user_status_id = %s" % id
        self.commit(delete_sql)

    def delete_verify_process_task_by_executor_id(self, verify_user_id):
        helper.log('按照executor删除verify_process_task表中的记录')
        delete_sql = "DELETE from verify_process_task where executor = %s" % verify_user_id
        self.commit(delete_sql)

    #等待提交
    def update_user_to_uncommit_status(self, user_id):
        self.update_verify_user_status_to_uncommit(user_id)
        self.delete_user_info_result(user_id)
        self.cleanup_verify_log(user_id)

    #提交完成，等待调查
    def update_user_to_inquireing_status(self, user_id):
        self.update_verify_user_status_to_inquireing(user_id)
        self.delete_user_info_result(user_id)
        self.populate_user_info_result(user_id, 'PENDING')
        self.cleanup_verify_log(user_id)

    #调查通过，等待一审
    def update_user_to_inquire_success_status(self, user_id):
        self.update_verify_user_status_to_inquire_success(user_id, 1, 'inv note', 12)
        self.delete_user_info_result(user_id)
        self.populate_user_info_result(user_id, 'VALID', 1)

    #调查不通过，补件
    def update_user_to_verify_fail_status(self, user_id):
        self.update_verify_user_status_to_verify_fail(user_id, 1, 'inv note', 12)
        self.delete_user_info_result(user_id)
        #将所有调查结果置为调查不符
        self.populate_user_info_result(user_id, 'NOTMATCH', 1)

    #一审通过，等待二审
    def update_user_to_first_verify_success_status(self, user_id):
        self.update_verify_user_status_to_first_verify_success(user_id, 1, 'inv note', 12, 1, 'first verify note', 10000, 1, 30.00)
        self.delete_user_info_result(user_id)
        self.populate_user_info_result(user_id, 'VALID', 1)

    #一审退回
    def update_user_to_first_verify_sendback_status(self, user_id):
        self.update_verify_user_status_to_first_verify_sendback(user_id, 1, 'inv note', 12, 1, 'first verify note')
        self.delete_user_info_result(user_id)
        self.populate_user_info_result(user_id, 'VALID', 1)

    #审核通过
    def update_user_to_second_verify_success_status(self, user_id):
        self.update_verify_user_status_to_second_verify_success(user_id, 1, 'inv note', 12, 1, 'first verify note', 10000, 1, 30.00,
                                                           1, 'second verify note', 20000, 1, 50.00)
        self.delete_user_info_result(user_id)
        self.populate_user_info_result(user_id, 'VALID', 1)

    #二审退回
    def update_user_to_second_verify_sendback(self, user_id):
        self.update_verify_user_status_to_second_verify_sendback(user_id, 1, 'inv note', 12, 1, 'first verify note', 10000, 1, 30.00, 1, 'second verify note')
        self.delete_user_info_result(user_id)
        self.populate_user_info_result(user_id, 'VALID', 1)

    #二审退件
    def update_user_to_second_verify_reject(self, user_id):
        self.update_verify_user_status_to_second_verify_reject(user_id, 1, 'inv note', 12, 1, 'first verify note', 10000, 1, 30.00, 1, 'second verify note')
        self.delete_user_info_result(user_id)
        self.populate_user_info_result(user_id, 'VALID', 1)

    def cleanup_verify_log(self, user_id):
        self.delete_user_status_log(user_id)
        self.delete_strategy_output(user_id)
        self.delete_verify_user_info_refine(user_id)

    def update_verify_user_status_to_inquireing(self, user_id):
        helper.log('将verify_user_status表的数据置为待调查')
        update_status_sql = "UPDATE verify_user_status SET " \
                            "verify_user_status='INQUIREING'," \
                            "reject_operation=NULL," \
                            "investigate_time=NULL," \
                            "first_verify_time=NULL," \
                            "second_verify_time=NULL," \
                            "investigate_user_id=NULL," \
                            "first_verify_user_id=NULL," \
                            "second_verify_user_id=NULL," \
                            "investigate_note=NULL," \
                            "first_verify_note=NULL," \
                            "second_verify_note=NULL," \
                            "first_verify_amount=NULL," \
                            "first_verify_card_product_id=NULL," \
                            "second_verify_amount=NULL," \
                            "second_verify_card_product_id=NULL," \
                            "online_time=NULL," \
                            "reject_reason_list=NULL," \
                            "in_youxin_back_list=NULL," \
                            "first_cash_draw_ratio=NULL," \
                            "cash_draw_ratio=NULL," \
                            "version='0'," \
                            "audit_user_status='INQUIREING' " \
                            "WHERE user_id = %s" % user_id
        self.commit(update_status_sql)

    def update_verify_user_status_to_uncommit(self, user_id):
        helper.log('将verify_user_status表的数据置为未提交')
        update_status_sql = "UPDATE verify_user_status SET " \
                            "verify_user_status='UNCOMMIT'," \
                            "reject_operation=NULL," \
                            "investigate_time=NULL," \
                            "first_verify_time=NULL," \
                            "second_verify_time=NULL," \
                            "investigate_user_id=NULL," \
                            "first_verify_user_id=NULL," \
                            "second_verify_user_id=NULL," \
                            "investigate_note=NULL," \
                            "first_verify_note=NULL," \
                            "second_verify_note=NULL," \
                            "first_verify_amount=NULL," \
                            "first_verify_card_product_id=NULL," \
                            "second_verify_amount=NULL," \
                            "second_verify_card_product_id=NULL," \
                            "online_time=NULL," \
                            "reject_reason_list=NULL," \
                            "in_youxin_back_list=NULL," \
                            "first_cash_draw_ratio=NULL," \
                            "cash_draw_ratio=NULL," \
                            "version='0'," \
                            "audit_user_status='UNCOMMIT' " \
                            "WHERE user_id = %s" % user_id
        self.commit(update_status_sql)

    def update_verify_user_status_to_inquire_success(self, user_id, investigate_user_id, investigate_note, online_time):
        helper.log('将verify_user_status表的数据置为待一审，即调查通过状态')
        update_status_sql = "UPDATE `verify_user_status` SET " \
                            "`verify_user_status` = 'INQUIRE_SUCCESS'," \
                            "`audit_user_status` = 'INQUIRE_SUCCESS', " \
                            "`create_time` = %s, " \
                            "`update_time` = %s, " \
                            "`commit_time` = %s, " \
                            "`reject_operation` = NULL, " \
                            "`reject_reason_list` = NULL, " \
                            "`investigate_time` = %s, " \
                            "`first_verify_time` = NULL, " \
                            "`second_verify_time` = NULL, " \
                            "`investigate_user_id` = %s, " \
                            "`first_verify_user_id` = NULL, " \
                            "`second_verify_user_id` = NULL, " \
                            "`investigate_note` = %s, " \
                            "`first_verify_note` = NULL, " \
                            "`second_verify_note` = NULL, " \
                            "`first_verify_amount` = NULL, " \
                            "`second_verify_amount` = NULL, " \
                            "`first_verify_card_product_id` = NULL, " \
                            "`second_verify_card_product_id` = NULL, " \
                            "`in_youxin_back_list` = 'UNCHECK', " \
                            "`version` = 0, " \
                            "`online_time` = %s, " \
                            "`first_cash_draw_ratio` = NULL, " \
                            "`cash_draw_ratio` = NULL, " \
                            "`second_cash_ratio` = NULL, " \
                            "`third_user_id` = NULL, " \
                            "`third_verify_date` = NULL, " \
                            "`third_verify_note` = NULL, " \
                            "`third_verify_card_product_id` = NULL, " \
                            "`third_verify_amount` = NULL " \
                            "WHERE user_id = %s"
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute(update_status_sql, (now, now, now, now, investigate_user_id, investigate_note, online_time, user_id))
        self.conn.commit()

    def update_verify_user_status_to_verify_fail(self, user_id, investigate_user_id, investigate_note, online_time):
        helper.log('将verify_user_status表的数据置为补件')
        update_status_sql = "UPDATE `verify_user_status` SET " \
                            "`verify_user_status` = 'VERIFY_FAIL'," \
                            "`audit_user_status` = 'VERIFY_FAIL', " \
                            "`create_time` = %s, " \
                            "`update_time` = %s, " \
                            "`commit_time` = %s, " \
                            "`reject_operation` = NULL, " \
                            "`reject_reason_list` = NULL, " \
                            "`investigate_time` = %s, " \
                            "`first_verify_time` = NULL, " \
                            "`second_verify_time` = NULL, " \
                            "`investigate_user_id` = %s, " \
                            "`first_verify_user_id` = NULL, " \
                            "`second_verify_user_id` = NULL, " \
                            "`investigate_note` = %s, " \
                            "`first_verify_note` = NULL, " \
                            "`second_verify_note` = NULL, " \
                            "`first_verify_amount` = NULL, " \
                            "`second_verify_amount` = NULL, " \
                            "`first_verify_card_product_id` = NULL, " \
                            "`second_verify_card_product_id` = NULL, " \
                            "`in_youxin_back_list` = 'UNCHECK', " \
                            "`version` = 0, " \
                            "`online_time` = %s, " \
                            "`first_cash_draw_ratio` = NULL, " \
                            "`cash_draw_ratio` = NULL, " \
                            "`second_cash_ratio` = NULL, " \
                            "`third_user_id` = NULL, " \
                            "`third_verify_date` = NULL, " \
                            "`third_verify_note` = NULL, " \
                            "`third_verify_card_product_id` = NULL, " \
                            "`third_verify_amount` = NULL " \
                            "WHERE user_id = %s"
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute(update_status_sql, (now, now, now, now, investigate_user_id, investigate_note, online_time, user_id))
        self.conn.commit()

    def update_verify_user_status_to_first_verify_success(self, user_id, investigate_user_id, investigate_note, online_time,
                                                          first_verify_user_id, first_verify_note, first_verify_amount,
                                                          first_verify_card_product_id, first_cash_draw_ratio):
        helper.log('将verify_user_status表的数据置为待二审，即一审通过状态')
        update_status_sql = "UPDATE `verify_user_status` SET " \
                            "`verify_user_status` = 'FIRST_VERIFY_SUCCESS'," \
                            "`audit_user_status` = 'FIRST_VERIFY_SUCCESS', " \
                            "`create_time` = %s, " \
                            "`update_time` = %s, " \
                            "`commit_time` = %s, " \
                            "`reject_operation` = NULL, " \
                            "`reject_reason_list` = NULL, " \
                            "`investigate_time` = %s, " \
                            "`first_verify_time` = %s, " \
                            "`second_verify_time` = NULL, " \
                            "`investigate_user_id` = %s, " \
                            "`first_verify_user_id` = %s, " \
                            "`second_verify_user_id` = NULL, " \
                            "`investigate_note` = %s, " \
                            "`first_verify_note` = %s, " \
                            "`second_verify_note` = NULL, " \
                            "`first_verify_amount` = %s, " \
                            "`second_verify_amount` = NULL, " \
                            "`first_verify_card_product_id` = %s, " \
                            "`second_verify_card_product_id` = NULL, " \
                            "`in_youxin_back_list` = 'UNCHECK', " \
                            "`version` = 0, " \
                            "`online_time` = %s, " \
                            "`first_cash_draw_ratio` = %s, " \
                            "`cash_draw_ratio` = NULL, " \
                            "`second_cash_ratio` = NULL, " \
                            "`third_user_id` = NULL, " \
                            "`third_verify_date` = NULL, " \
                            "`third_verify_note` = NULL, " \
                            "`third_verify_card_product_id` = NULL, " \
                            "`third_verify_amount` = NULL " \
                            "WHERE user_id = %s"
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute(update_status_sql, (now, now, now, now, now, investigate_user_id, first_verify_user_id,
                                           investigate_note, first_verify_note, first_verify_amount, first_verify_card_product_id,
                                           online_time, first_cash_draw_ratio, user_id))
        self.conn.commit()

    def update_verify_user_status_to_first_verify_sendback(self, user_id, investigate_user_id, investigate_note, online_time,
                                                           first_verify_user_id, first_verify_note):
        helper.log('将verify_user_status表的数据置为一审退回状态')
        update_status_sql = "UPDATE `verify_user_status` SET " \
                            "`verify_user_status` = 'FIRST_SEND_BACK'," \
                            "`audit_user_status` = 'FIRST_SEND_BACK', " \
                            "`create_time` = %s, " \
                            "`update_time` = %s, " \
                            "`commit_time` = %s, " \
                            "`reject_operation` = NULL, " \
                            "`reject_reason_list` = NULL, " \
                            "`investigate_time` = %s, " \
                            "`first_verify_time` = %s, " \
                            "`second_verify_time` = NULL, " \
                            "`investigate_user_id` = %s, " \
                            "`first_verify_user_id` = %s, " \
                            "`second_verify_user_id` = NULL, " \
                            "`investigate_note` = %s, " \
                            "`first_verify_note` = %s, " \
                            "`second_verify_note` = NULL, " \
                            "`first_verify_amount` = NULL, " \
                            "`second_verify_amount` = NULL, " \
                            "`first_verify_card_product_id` = NULL, " \
                            "`second_verify_card_product_id` = NULL, " \
                            "`in_youxin_back_list` = 'UNCHECK', " \
                            "`version` = 0, " \
                            "`online_time` = %s, " \
                            "`first_cash_draw_ratio` = NULL, " \
                            "`cash_draw_ratio` = NULL, " \
                            "`second_cash_ratio` = NULL, " \
                            "`third_user_id` = NULL, " \
                            "`third_verify_date` = NULL, " \
                            "`third_verify_note` = NULL, " \
                            "`third_verify_card_product_id` = NULL, " \
                            "`third_verify_amount` = NULL " \
                            "WHERE user_id = %s"
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute(update_status_sql, (now, now, now, now, now, investigate_user_id, first_verify_user_id,
                                           investigate_note, first_verify_note, online_time, user_id))
        self.conn.commit()


    def update_verify_user_status_to_second_verify_success(self, user_id, investigate_user_id, investigate_note, online_time,
                                                           first_verify_user_id, first_verify_note, first_verify_amount,
                                                           first_verify_card_product_id, first_cash_draw_ratio,
                                                           second_verify_user_id, second_verify_note, second_verify_amount,
                                                           second_verify_card_product_id, second_cash_draw_ratio):
        helper.log('将verify_user_status表的数据置为审核通过状态')
        update_status_sql = "UPDATE `verify_user_status` SET " \
                            "`verify_user_status` = 'VERIFY_SUCCESS'," \
                            "`audit_user_status` = 'VERIFY_SUCCESS', " \
                            "`create_time` = %s, " \
                            "`update_time` = %s, " \
                            "`commit_time` = %s, " \
                            "`reject_operation` = NULL, " \
                            "`reject_reason_list` = NULL, " \
                            "`investigate_time` = %s, " \
                            "`first_verify_time` = %s, " \
                            "`second_verify_time` = %s, " \
                            "`investigate_user_id` = %s, " \
                            "`first_verify_user_id` = %s, " \
                            "`second_verify_user_id` = %s, " \
                            "`investigate_note` = %s, " \
                            "`first_verify_note` = %s, " \
                            "`second_verify_note` = %s, " \
                            "`first_verify_amount` = %s, " \
                            "`second_verify_amount` = %s, " \
                            "`first_verify_card_product_id` = %s, " \
                            "`second_verify_card_product_id` = %s, " \
                            "`in_youxin_back_list` = 'UNCHECK', " \
                            "`version` = 0, " \
                            "`online_time` = %s, " \
                            "`first_cash_draw_ratio` = %s, " \
                            "`cash_draw_ratio` = NULL, " \
                            "`second_cash_ratio` = %s, " \
                            "`third_user_id` = NULL, " \
                            "`third_verify_date` = NULL, " \
                            "`third_verify_note` = NULL, " \
                            "`third_verify_card_product_id` = NULL, " \
                            "`third_verify_amount` = NULL " \
                            "WHERE user_id = %s"
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute(update_status_sql, (now, now, now, now, now, now, investigate_user_id, first_verify_user_id, second_verify_user_id,
                                           investigate_note, first_verify_note, second_verify_note, first_verify_amount,
                                           second_verify_amount, first_verify_card_product_id, second_verify_card_product_id,
                                           online_time, first_cash_draw_ratio, second_cash_draw_ratio, user_id))
        self.conn.commit()

    def update_verify_user_status_to_second_verify_sendback(self, user_id, investigate_user_id, investigate_note, online_time,
                                                            first_verify_user_id, first_verify_note, first_verify_amount,
                                                            first_verify_card_product_id, first_cash_draw_ratio,
                                                            second_verify_user_id, second_verify_note):
        helper.log('将verify_user_status表的数据置为二审退回状态')
        update_status_sql = "UPDATE `verify_user_status` SET " \
                            "`verify_user_status` = 'SECOND_SEND_BACK'," \
                            "`audit_user_status` = 'SECOND_SEND_BACK', " \
                            "`create_time` = %s, " \
                            "`update_time` = %s, " \
                            "`commit_time` = %s, " \
                            "`reject_operation` = NULL, " \
                            "`reject_reason_list` = NULL, " \
                            "`investigate_time` = %s, " \
                            "`first_verify_time` = %s, " \
                            "`second_verify_time` = %s, " \
                            "`investigate_user_id` = %s, " \
                            "`first_verify_user_id` = %s, " \
                            "`second_verify_user_id` = %s, " \
                            "`investigate_note` = %s, " \
                            "`first_verify_note` = %s, " \
                            "`second_verify_note` = %s, " \
                            "`first_verify_amount` = %s, " \
                            "`second_verify_amount` = NULL, " \
                            "`first_verify_card_product_id` = %s, " \
                            "`second_verify_card_product_id` = NULL, " \
                            "`in_youxin_back_list` = 'UNCHECK', " \
                            "`version` = 0, " \
                            "`online_time` = %s, " \
                            "`first_cash_draw_ratio` = %s, " \
                            "`cash_draw_ratio` = NULL, " \
                            "`second_cash_ratio` = NULL, " \
                            "`third_user_id` = NULL, " \
                            "`third_verify_date` = NULL, " \
                            "`third_verify_note` = NULL, " \
                            "`third_verify_card_product_id` = NULL, " \
                            "`third_verify_amount` = NULL " \
                            "WHERE user_id = %s"
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute(update_status_sql, (now, now, now, now, now, now, investigate_user_id, first_verify_user_id, second_verify_user_id,
                                           investigate_note, first_verify_note, second_verify_note, first_verify_amount,
                                           first_verify_card_product_id, online_time, first_cash_draw_ratio, user_id))
        self.conn.commit()

    def update_verify_user_status_to_second_verify_reject(self, user_id, investigate_user_id, investigate_note, online_time,
                                                          first_verify_user_id, first_verify_note, first_verify_amount,
                                                          first_verify_card_product_id, first_cash_draw_ratio,
                                                          second_verify_user_id, second_verify_note):
        helper.log('将verify_user_status表的数据置为审核通过状态')
        update_status_sql = "UPDATE `verify_user_status` SET " \
                            "`verify_user_status` = 'VERIFY_REJECT'," \
                            "`audit_user_status` = 'VERIFY_REJECT', " \
                            "`create_time` = %s, " \
                            "`update_time` = %s, " \
                            "`commit_time` = %s, " \
                            "`reject_operation` = NULL, " \
                            "`reject_reason_list` = NULL, " \
                            "`investigate_time` = %s, " \
                            "`first_verify_time` = %s, " \
                            "`second_verify_time` = %s, " \
                            "`investigate_user_id` = %s, " \
                            "`first_verify_user_id` = %s, " \
                            "`second_verify_user_id` = %s, " \
                            "`investigate_note` = %s, " \
                            "`first_verify_note` = %s, " \
                            "`second_verify_note` = %s, " \
                            "`first_verify_amount` = %s, " \
                            "`second_verify_amount` = NULL, " \
                            "`first_verify_card_product_id` = %s, " \
                            "`second_verify_card_product_id` = NULL, " \
                            "`in_youxin_back_list` = 'UNCHECK', " \
                            "`version` = 0, " \
                            "`online_time` = %s, " \
                            "`first_cash_draw_ratio` = %s, " \
                            "`cash_draw_ratio` = NULL, " \
                            "`second_cash_ratio` = NULL, " \
                            "`third_user_id` = NULL, " \
                            "`third_verify_date` = NULL, " \
                            "`third_verify_note` = NULL, " \
                            "`third_verify_card_product_id` = NULL, " \
                            "`third_verify_amount` = NULL " \
                            "WHERE user_id = %s"
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute(update_status_sql, (now, now, now, now, now, now, investigate_user_id, first_verify_user_id, second_verify_user_id,
                                           investigate_note, first_verify_note, second_verify_note, first_verify_amount, first_verify_card_product_id,
                                           online_time, first_cash_draw_ratio, user_id))
        self.conn.commit()

    def populate_user_info_result(self, user_id, result, verify_user_id=None):
        helper.log('初始化verify_user_info_result表\n')
        result_keys = ['ADDRESS', 'CHILD_STATUS', 'COMPANY', 'CREDIT_CARD_NUMBER', 'CREDIT_REPORT', 'GRADUATE_YEAR',
                       'GRADUATION', 'HASCAR', 'HASHOUSE', 'MARRIAGE_STATUS', 'MONTHLY_SALARY', 'PHONE', 'REAL_NAME',
                       'UNIVERSITY', 'URGENT_MOBILE', 'URGENT_NAME', 'URGENT_RELATION', 'WORK_PHONE', 'WORK_POSITION']
        insert_sql = '''INSERT INTO `verify_user_info_result`
               (`user_id`, `key_`, `value_`, `verify_user_id`, `create_time`, `update_time`, `version`)
                VALUES (%s, %s, %s, %s, %s, %s, %s)'''
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for key in result_keys:
            self.cursor.execute(insert_sql, (user_id, key, result, verify_user_id, now, now, 0))
            self.conn.commit()

    def get_incorrect_user_ids(self):
        query = '''SELECT DISTINCT
              v1.user_id
            FROM
              verify_user_status v1,
              verify_user_info_result
            WHERE v1.user_id NOT IN
              (SELECT
                user_id
              FROM
                verify_user_info_result)
              AND v1.verify_user_status <> 'UNCOMMIT' ;'''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def delete_user_info_result(self, user_id):
        helper.log('将verify_user_info_result表清空\n')
        delete_sql = "DELETE FROM `verify_user_info_result` where `user_id` = %s" % user_id
        self.commit(delete_sql)

    def update_user_info_result_to_pending(self, user_id):
        helper.log('将verify_user_info_result表置为PENDING\n')
        update_user_info_result = "UPDATE `verify_user_info_result` SET `value_` = 'PENDING', `verify_user_id` = NULL WHERE `user_id` = %s" % user_id
        self.commit(update_user_info_result)

    def delete_user_status_log(self, user_id):
        helper.log('将verify_user_status_log表中的数据删除\n')
        delete_user_status_log = "delete from `verify_user_status_log` where `user_id` = %s" % user_id
        self.commit(delete_user_status_log)

    def delete_strategy_output(self, user_id):
        helper.log('将verify_strategy_output表中的数据删除\n')
        delete_strategy_output = "delete from `verify_strategy_output` where `user_id` = %s" % user_id
        self.commit(delete_strategy_output)

    def delete_verify_user_info_refine(self, user_id):
        helper.log('将verify_user_info_refine表中的数据删除\n')
        delete_user_info_refine = "delete from `verify_user_info_refine` where `user_id` = %s" % user_id
        self.commit(delete_user_info_refine)

    def get_user_key_by_nick_name(self, nick_name):
        self.cursor.execute("select user_key from user where nick_name = '%s'" % nick_name)
        ret = self.cursor.fetchone()
        if ret is None:
            return None
        return ret[0]

    def get_user_entry_by_user_key(self, key):
        self.cursor.execute("select * from user where user_key = '%s'" % key)
        ret = self.cursor.fetchone()
        if ret is None:
            return None
        return ret

    def get_user_keys_by_nick_name_prefix(self, prefix, count):
        query = "select user_key from user where nick_name like '%s' order by nick_name LIMIT %s" % (prefix + '%', count)
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_user_keys_from_system_grant_coupon(self, *status):
        query = "select `user_key`, `status` from `admin_system_grant_coupon_users`"
        self.cursor.execute(query)
        user_keys = self.cursor.fetchall()
        ret = []
        for row in user_keys:
            if str(row[1]) in status:
                ret.append(row[0])
        return ret

    def populate_user_into_system_grant_coupon(self, *user_keys):
        for key in user_keys:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute("""INSERT INTO `admin_system_grant_coupon_users` (`user_key`, `status`, `create_time`, `update_time`,
            `active_action`, `version`) VALUES (%s, 1, %s, %s, 'REGISTER_VERIFY', 0)""",
                           (key, str(now), str(now)))
            self.conn.commit()

    def populate_coupon_batch_into_active_ref(self, *batch_keys):
        for key in batch_keys:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute("""INSERT INTO `coupon_batch_active_status_ref` (`active_action`, `coupon_batch_key`, `create_time`,
            `update_time`) VALUES ('REGISTER_VERIFY', %s, %s, %s)""", (key, str(now), str(now)))
            self.conn.commit()

    def delete_all_system_grant_coupon(self):
        self.cursor.execute("""delete from `admin_system_grant_coupon_users`""")
        self.conn.commit()

    def delete_user_from_system_grant_coupon(self, *user_keys):
        for key in user_keys:
            self.cursor.execute("""delete from `admin_system_grant_coupon_users` where `user_key` = %s""", (key[0],))
            self.conn.commit()

    def get_coupon_batch_key_by_name(self, name):
        self.cursor.execute("select batch_key from `coupon_batch` where `name` = '%s'" % name)
        ret = self.cursor.fetchone()
        if ret is None:
            return None
        return ret[0]

    def get_coupon_batch_id_by_name(self, name):
        self.cursor.execute("select id from `coupon_batch` where `name` = '%s'" % name)
        ret = self.cursor.fetchone()
        if ret is None:
            return None
        return ret[0]

    def delete_coupon_batch_by_key(self, batch_key):
        self.cursor.execute("""delete from `coupon` where `coupon_batch_key` = %s""", (batch_key,))
        self.cursor.execute("""delete from `coupon_batch_log` where `batch_key` = %s""", (batch_key,))
        self.cursor.execute("""delete from `coupon_batch` where `batch_key` = %s""", (batch_key,))
        self.cursor.execute("""delete from `admin_coupon_activity` where `batch_key` = %s""", (batch_key,))
        self.conn.commit()

    def delete_coupon_batch_by_name(self, name):
        batch_key = self.get_coupon_batch_key_by_name(name)
        if batch_key is None:
            return
        self.delete_coupon_batch_by_key(batch_key)

    def delete_all_system_coupon_batch(self):
        self.cursor.execute("select batch_key from `coupon_batch` where `grant_type` = 'SYSTEM'")
        batch_keys = self.cursor.fetchall()
        for key in batch_keys:
            self.delete_coupon_batch_by_key(key[0])

    def update_user_register_time_to_current_by_user_key(self, time, *user_key):
        for key in user_key:
            self.cursor.execute("update user set register_time = %s where user_key = %s", (time, key))
            self.conn.commit()

    def get_admin_job_interval_time_by_job_class_name(self, name):
        self.cursor.execute(
            "select param_value from admin_task_timer inner join admin_task_timer_param on admin_task_timer.id = admin_task_timer_param.task_id where task_class = '%s'" % name)
        values = self.cursor.fetchall()
        total = 0
        for value in values:
            total += int(value[0])
        return total

    def get_verify_job_interval_time_by_job_class_name(self, name):
        self.cursor.execute(
            "select param_value from verify_task_timer inner join verify_task_timer_param on verify_task_timer.id = verify_task_timer_param.task_id where task_class = '%s'" % name)
        values = self.cursor.fetchall()
        total = 0
        for value in values:
            total += int(value[0])
        return total

    def search_user(self, type, key, *verify_status):
        sql = '''
    select
        user.user_id,
        user.nick_name,
        user_info.real_name,
        user.mobile,
        user_info.id_no,
        user.channel,
        verify_user_status.verify_user_status
    from
        user
            inner join
        user_info ON user.user_id = user_info.user_id
            inner join
        verify_user_status ON user.user_id = verify_user_status.user_id
    where '''

        if type == global_enum.SearchType.NickName:
            sql += 'user.nick_name like \'%s' % key
        elif type == global_enum.SearchType.Mobile:
            sql += 'user.mobile like \'%s' % key
        elif type == global_enum.SearchType.IdNum:
            sql += 'user_info.id_no like \'%s' % key
        elif type == global_enum.SearchType.RealName:
            sql += 'user_info.real_name like \'%s' % key
        sql += '%\''

        if len(verify_status) > 0:
            verify_status = ['\'' + status + '\'' for status in verify_status]
            sql += ' and verify_user_status.verify_user_status in (' + ','.join(verify_status) + ')'

        sql += ' order by user.register_time desc , user_id asc;'

        helper.log('执行sql：' + sql)
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_real_name_in_verify_user(self, verify_user_id):
        return self.fetch_one('select real_name from verify_user where id = %s' % verify_user_id)

    def get_latest_verify_user_status_log(self, user_id):
        sql ='select verify_user_id, create_time from verify_user_status_log where user_id = %s order by create_time desc limit 0,1' % user_id
        self.cursor.execute(sql)
        ret = self.cursor.fetchone()
        if ret is not None:
            if ret[0] is not None:
                return self.get_real_name_in_verify_user(ret[0]), ret[1]
            else:
                return '', ret[1]
        return None

    def get_user_info_for_verify_log(self, nick_name):
        sql = "select nick_name, real_name, mobile, id_no, channel, vus.verify_user_status from user " \
              "inner join user_info on user.user_id = user_info.user_id " \
              "inner join verify_user_status as vus on user.user_id = vus.user_id " \
              "where nick_name = '%s'" % nick_name
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def update_user_channel_by_user_id(self, user_id, channel_type):
        if channel_type == global_enum.Channel.BD_IMPORT:
            sql = "UPDATE `user` SET `channel`='%s' WHERE `user_id`='%s'" % ('BD_IMPORT', user_id)
        elif channel_type == global_enum.Channel.PERSONAL_REGISTER:
            sql = "UPDATE `user` SET `channel`='%s' WHERE `user_id`='%s'" % ('PERSONAL_REGISTER', user_id)
        else:
            raise AssertionError('No code can handle this kind of channel type')
        self.commit(sql)

    def delete_application_status_and_user_info_by_user_key(self, user_key):
        self.cursor.execute("""delete from verify_application_status where user_key = %s""", (user_key,))
        self.cursor.execute("""delete from verify_application_status_log where user_key = %s""", (user_key,))
        self.cursor.execute("""delete from verify_application_user_info where user_key = %s""", (user_key,))
        self.cursor.execute("""delete from verify_application_submit_info where user_key = %s""", (user_key,))
        self.conn.commit()

    def get_application_id_by_user_key(self, user_key):
        return self.fetch_one("select application_id from verify_application_status where user_key = '%s'" % user_key)

    def get_application_pk_id_by_user_key(self, user_key):
        return self.fetch_one("select id from verify_application_status where user_key = '%s'" % user_key)

    def update_user_by_user_key(self, user_key, mobile):
        self.cursor.execute("update user set mobile='%s' where user_key='%s'" % (mobile, user_key))
        self.conn.commit()

    def update_idcard_info_by_user_key(self, user_key, id_number, real_name):
        self.cursor.execute("update idcard_info set idcard_number='%s',idcard_name='%s' where user_key='%s'" % (id_number, real_name, user_key))
        self.conn.commit()

    def update_verify_application_status(self, user_key, status):
        self.cursor.execute("update verify_application_status set current_verify_status='%s' where user_key='%s'" % (status, user_key))
        self.conn.commit()

    def update_or_insert_edu_card_info_by_id_number(self, id_number, real_name):
        ret = self.fetch_one("select id_card_name from edu_card_info where id_card_number='%s'" % id_number)
        if ret is not None:
            self.cursor.execute("update edu_card_info set id_card_name='%s',id_card_number='%s' where id_card_number='%s'" % (real_name, id_number, id_number))
        else:
            self.cursor.execute("""
            INSERT INTO `edu_card_info`(`create_time`, `education_degree`, `enrol_date`, `graduate`, `graduate_time`, `id_card_name`,
                            `id_card_number`, `photo_url`, `speciality_name`, `study_result`, `study_style`, `update_time`)
            VALUES('2016-05-09 14:45:04', '专科', '2000', '老九门', '2005', '%s', '%s',
                   '/11b3464c-0f02-419f-a29d-bdb5494fb187.jpg', '削土豆111', '结业', '普通', '2016-05-16 14:10:51');
            """ % (real_name, id_number))
        self.conn.commit()

    def update_user_bank_card_info_by_user_key(self, user_key, bank_card_number, bank_name, real_name, id_number, reserve_mobile):
        self.cursor.execute("update user_bank_card_info set "
                       "bank_card_no='%s',"
                       "bank_name='%s',"
                       "bind_status='BIND_SUCCESS',"
                       "idcard_name='%s',"
                       "mobile='%s',"
                       "idcard_number='%s' where user_key='%s'"
                       % (bank_card_number, bank_name, real_name, reserve_mobile, id_number, user_key))
        self.conn.commit()

    def delete_policy_detail_by_application_id(self, application_id):
        self.cursor.execute("delete from verify_policy_detail where application_id = '%s'" % (application_id,))
        self.conn.commit()

    def delete_third_party_result_and_log_by_application_pk_id(self, id):
        self.cursor.execute("delete from verify_third_party_result where verify_application_id='%s'" % (id,))
        self.cursor.execute("delete from verify_third_party_request_log where verify_application_id='%s'" % (id,))
        self.conn.commit()

    def get_third_party_result_by_type(self, type, application_pk_id):
        third_party_type_in_str = global_enum.VerifyThirdPartyTypeEnum.get_string(type)
        if third_party_type_in_str is not None:
            self.cursor.execute("select res_status, res_detail from verify_third_party_result where verify_application_id=%s" % application_pk_id)
            ret = self.cursor.fetchone()
            if ret is not None:
                return ret
        return None
