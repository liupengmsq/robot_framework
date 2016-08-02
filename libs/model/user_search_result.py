from robot.libraries.BuiltIn import BuiltIn

class UserSearchResult:
    def __init__(self):
        self.user_id = ''
        self.nick_name = ''
        self.real_name = ''
        self.mobile = ''
        self.id_no = ''
        self.channel = ''
        self.verify_user_status = ''
        self.operator = ''
        self.operate_time = ''
        self.built_in = BuiltIn()

    def __eq__(self, other):
        if self.user_id != other.user_id:
            self.built_in.fatal_error('user id is different!!')
            return False
        if self.nick_name != other.nick_name:
            self.built_in.fatal_error('nick name is different!!')
            return False
        if self.real_name != other.real_name:
            self.built_in.fatal_error('real name is different!!')
            return False
        if self.mobile != other.mobile:
            self.built_in.fatal_error('mobile is different!!')
            return False
        if self.id_no != other.id_no:
            self.built_in.fatal_error('id no is different!!')
            return False
        if self.channel != other.channel:
            self.built_in.fatal_error('channel is different!!')
            return False
        if self.verify_user_status!= other.verify_user_status:
            self.built_in.fatal_error('verify user status is different!!')
            return False
        if self.operator != other.operator:
            self.built_in.fatal_error('operator is different!!')
            return False
        if self.operate_time != other.operate_time:
            self.built_in.fatal_error('operate time is different!!')
            return False
        return True
