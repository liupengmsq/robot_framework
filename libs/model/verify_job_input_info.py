# -*- coding: utf-8 -*-
import csv
from ..global_enum import *


class VerifyJobInputInfo(object):

    def __init__(self, id_number, mobile, real_name, reserve_mobile, bank_name, bank_number, type=None):
        self.id_number = id_number
        self.mobile = mobile
        self.real_name = real_name
        self.reserve_mobile = reserve_mobile
        self.bank_name = bank_name
        self.bank_number = bank_number
        if type is not None:
            self.type = VerifyJobInputType.get_enum(type)
        else:
            self.type = ''

    def __unicode__(self):
        return str.format('type:%s, id_number: %s, mobile: %s, real_name: %s, reserve_mobile: %s, '
                          'bank_name: %s, bank_number: %s\n' %
                          (self.type, self.id_number, self.mobile, self.real_name, self.reserve_mobile, self.bank_name, self.bank_number))

    def __str__(self):
        return self.__unicode__()

    @staticmethod
    def parse_from_csv(csvfile_path):
        ret = []
        with open(csvfile_path, 'rb') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                input_info = VerifyJobInputInfo(row[1], row[2], row[3], row[4], row[5], row[6], row[0])
                ret.append(input_info)
        return ret

    @staticmethod
    def parse_from_external_csv(csvfile_path, line_number):
        ret = []
        with open(csvfile_path, 'rb') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                input_info = VerifyJobInputInfo(row[0].strip(), row[1].strip(), row[3].strip(), row[4].strip(), row[6].strip(), row[8].strip())
                ret.append(input_info)
        return ret[line_number]


if __name__ == "__main__":
    ret = VerifyJobInputInfo.parse_from_csv('/home/peng/Desktop/test.csv')
    print ret[0]
