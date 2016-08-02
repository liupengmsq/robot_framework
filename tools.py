# -*- coding: utf-8 -*-  
import sys

import libs.helper
from libs.DB_utils.utils import *
from libs.request_utils.verify import *
from libs.request_utils.flow_task_manage import *
from datetime import datetime
from libs.model import verify_job_input_info


def help_info():
    print "将指定的user_id置为待调查状态\n" \
          "\tpython tools.py init user_id列表 "


def user_login(username):
    libs.helper.log("使用用户名'%s'登陆" % username)
    request_util = VerifyRequest('http://172.16.2.38:15081', username)
    request_util.login()
    return request_util


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        help_info()
        sys.exit(0)

    # request_util = VerifyRequest('http://172.16.2.38:15081/')
    request_util = VerifyRequest('http://172.16.2.111:9096/heika-verify/')

    if sys.argv[1] == 'init':
        for user_id in sys.argv[2:]:
            libs.helper.log('将user_id为%s的用户置为待调查状态' % user_id)
            update_user_to_inquireing_status(user_id)

            libs.helper.log('删除审核状态表原有数据')
            delete_verify_user_status_by_user_id(user_id)

            libs.helper.log('调用接口模拟初始化审核状态')
            libs.helper.log(request_util.init_user_from_mobile(user_id))

            libs.helper.log('调用接口模拟提交审核')
            libs.helper.log(request_util.commit_user_from_mobile(user_id))
        sys.exit(0)

    if sys.argv[1] == 'init_dubbo':
        for user_id in sys.argv[2:]:
            libs.helper.log('调用接口模拟init审核')
            libs.helper.log(request_util.init_user_from_mobile(user_id))
        sys.exit(0)

    if sys.argv[1] == 'commit_dubbo':
        for user_id in sys.argv[2:]:
            libs.helper.log('调用接口模拟提交审核')
            libs.helper.log(request_util.commit_user_from_mobile(user_id))
        sys.exit(0)

    if sys.argv[1] == 'cleanup_by_user_id':
        for user_id in sys.argv[2:]:
            libs.helper.log('将user_id为%s的用户任务清除' % user_id)
            verify_user_status_id = get_verify_user_status_id_by_user_id(user_id)

            if verify_user_status_id is None:
                libs.helper.log_error('未找到user_id=%s对应的verify_user_status数据' % user_id)
                pass

            libs.helper.log('verify_user_status_id = %s' % verify_user_status_id)
            libs.helper.log('删除verify_process_task表中的数据, verify_user_status_id为%s' % verify_user_status_id)
            delete_verify_process_task_by_verify_user_status_id(verify_user_status_id)
        sys.exit(0)

    if sys.argv[1] == 'cleanup_by_executor_name':
        for real_name in sys.argv[2:]:
            libs.helper.log('将real_name为%s的用户任务清除' % real_name)
            with DBHelper() as db_helper:
                verify_user_id = db_helper.get_verify_user_id_by_real_name(real_name)

            if verify_user_id is None:
                libs.helper.log_error('未找到real_name=%s的verify_user数据' % real_name)
                pass

            libs.helper.log('verify_user_id = %s' % verify_user_id)
            libs.helper.log('删除verify_process_task表中的数据, executor为%s' % verify_user_id)
            with DBHelper() as db_helper:
                db_helper.delete_verify_process_task_by_executor_id(verify_user_id)
        sys.exit(0)


    if sys.argv[1] == 'cleanup_by_executor_name_and_user_key':
        executor_name = sys.argv[2]
        user_key = sys.argv[3]
        libs.helper.log('清空相关数据开始，审核人：%s，user_key：%s' % (executor_name, user_key))

        with DBHelper() as db_helper:
            verify_user_id = db_helper.get_verify_user_id_by_real_name(executor_name)
            libs.helper.log('删除verify_process_task表中的数据, executor为%s' % verify_user_id)
            db_helper.delete_verify_process_task_by_executor_id(verify_user_id)

            libs.helper.log('删除verify_application_status, verify_application_status_log'
                            '与verify_application_user_info表中的数据, user_key为%s' % user_key)
            db_helper.delete_application_status_and_user_info_by_user_key(user_key)

        sys.exit(0)

    if sys.argv[1] == 'inv_pass':
        request_util = user_login(sys.argv[2])
        for user_id in sys.argv[3:]:
            libs.helper.log('将user_id为%s的用户通过调查' % user_id)
            inv_rets = request_util.get_all_valid_investigate_result()
            response = request_util.commit_to_first_verify(user_id, 12, '调查备注', **inv_rets)

            libs.helper.log(response.text)
        sys.exit(0)

    if sys.argv[1] == 'first_verify_pass':
        request_util = user_login(sys.argv[2])
        for user_id in sys.argv[3:]:
            libs.helper.log('将user_id为%s的用户通过一审' % user_id)
            response = request_util.commit_to_second_verify(user_id, 123, 3, 56, '一审备注')

            libs.helper.log(response.text)
        sys.exit(0)

    if sys.argv[1] == 'second_verify_pass':
        request_util = user_login(sys.argv[2])
        for user_id in sys.argv[3:]:
            libs.helper.log('将user_id为%s的用户通过二审' % user_id)
            response = request_util.commit_to_pass_second_verify(user_id, 321, 2, 78, '二审备注')

            libs.helper.log(response.text)
        sys.exit(0)

    if sys.argv[1].startswith('grant_coupon'):
        count_of_user = sys.argv[2]
        user_nick_name_prefix = sys.argv[3]
        register_time = sys.argv[4]
        sent_status = sys.argv[5:]
        user_keys = get_user_keys_by_nick_name_prefix(user_nick_name_prefix, count_of_user)

        time = None
        if register_time == 'current':
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            time = register_time

        if sys.argv[1].endswith('cleanup'):
            delete_user_from_system_grant_coupon(*user_keys)
        else:
            coupon_sent_user_keys = get_user_keys_from_system_grant_coupon(*sent_status)
            coupon_not_sent_user_keys = []
            for i in user_keys:
                if i[0] not in coupon_sent_user_keys:
                    coupon_not_sent_user_keys.append(i[0])
            update_user_register_time_to_current_by_user_key(time, *coupon_not_sent_user_keys)
            populate_user_into_system_grant_coupon(*coupon_not_sent_user_keys)

    if sys.argv[1] == 'prepare_verify_test_data':
        user_key = sys.argv[2]
        external_csv_file_path = sys.argv[3]
        channel_id = sys.argv[4]
        line_number = int(sys.argv[5])

        libs.helper.log('解析csv文件')
        user_info = verify_job_input_info.VerifyJobInputInfo.parse_from_external_csv(external_csv_file_path, line_number)
        libs.helper.log('读取数据内容如下： \n%s' % user_info)

        libs.helper.log('更新测试数据')
        with DBHelper() as db_helper:
            db_helper.update_user_by_user_key(user_key, user_info.mobile)
            db_helper.update_idcard_info_by_user_key(user_key, user_info.id_number, user_info.real_name)
            db_helper.update_or_insert_edu_card_info_by_id_number(user_info.id_number, user_info.real_name)
            db_helper.update_user_bank_card_info_by_user_key(user_key, user_info.bank_number, user_info.bank_name, user_info.real_name, user_info.id_number, user_info.reserve_mobile)

        # libs.helper.log('提交进件')
        # request_util.login()
        # response = request_util.submit_application(user_key, 'false', channel_id)
        # libs.helper.log(str.format('返回结果： {0}, {1}', response.result_code, response.application_id))

        libs.helper.log('Done')


    if sys.argv[1] == 'test':
        # delete_user_info_result(1)
        # populate_user_info_result(1, 'PENDING')
        # update_verify_user_status_to_inquire_success(100034833, 1, 'investigate note', 12)
        # ret = get_latest_verify_user_status_log(100034832)
        # if ret is not None:
        #     print ret[0], ret[1]
        # flow_task_request = FlowTaskManage('http://172.16.2.38:15081/', username='liupeng@renrendai.com')
        # flow_task_request.login()
        # response = flow_task_request.flow_setup('PEOPLE', 3, 69, 73)
        # response = flow_task_request.get_pending_tasks()
        # print response
        ret = get_incorrect_user_ids()

        print ret;
