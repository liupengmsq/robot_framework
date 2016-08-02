from Selenium2Library import Selenium2Library
from selenium.common.exceptions import StaleElementReferenceException
import time


def _get_table_field_value(element, field):
    return element.find_element_by_xpath("./td[@field='" + field + "']").text.strip()


class CustomSeleniumLibrary(Selenium2Library):
    def get_table_row_count(self, table_locator):
        attempts = 0
        while True:
            try:
                table = self._table_element_finder.find(self._current_browser(), table_locator)
                return len(table.find_elements_by_xpath("./tbody/tr"))
            except StaleElementReferenceException:
                time.sleep(1)
                if attempts >= 1:
                    raise AssertionError("Cell in table %s could not be found." % table_locator)
                else:
                    pass
            attempts += 1

    def get_user_search_results(self, table_locator, row_index):
        table = self._table_element_finder.find(self._current_browser(), table_locator)
        ret = []
        if table is not None:
            rows = table.find_elements_by_xpath("./tbody/tr")
            if len(rows) <= 0:
                return None
            row_index = int(row_index)
            if len(rows)-1 < row_index:
                raise AssertionError("The row index '%s' is large than row length '%s'." % (row_index, len(rows)))
            for row in rows:
                dic = {
                    'userId': _get_table_field_value(row, 'userId'),
                    'nickName': _get_table_field_value(row, 'nickName'),
                    'realName': _get_table_field_value(row, 'realName'),
                    'mobile': _get_table_field_value(row, 'mobile'),
                    'idNo': _get_table_field_value(row, 'idNo'),
                    'userType': _get_table_field_value(row, 'userType'),
                    'verifyUserStatus': _get_table_field_value(row, 'verifyUserStatus'),
                    'operator': _get_table_field_value(row, 'operater'),
                    'operateTime': _get_table_field_value(row, 'operateTime'),
                }
                ret.append(dic)
            return ret[row_index]
        else:
            return None

    def get_flow_task_results(self, table_locator, row_index):
        table = self._table_element_finder.find(self._current_browser(), table_locator)
        ret = []
        if table is not None:
            rows = table.find_elements_by_xpath("./tbody/tr")
            if len(rows) <= 0:
                return None
            row_index = int(row_index)
            if len(rows)-1 < row_index:
                raise AssertionError("The row index '%s' is large than row length '%s'." % (row_index, len(rows)))
            for row in rows:
                dic = {
                    'userId': _get_table_field_value(row, 'userId'),
                    'nickName': _get_table_field_value(row, 'nickName'),
                    'realName': _get_table_field_value(row, 'realName'),
                    'idCardNum': _get_table_field_value(row, 'idCardNum'),
                    'mobile': _get_table_field_value(row, 'mobile'),
                    'userType': _get_table_field_value(row, 'userType'),
                    'taskName': _get_table_field_value(row, 'taskName'),
                    'taskCreatedTime': _get_table_field_value(row, 'taskCreatedTime'),
                }
                ret.append(dic)
            return ret[row_index]
        else:
            return None

