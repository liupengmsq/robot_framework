import inspect
from datetime import datetime
import subprocess



def log(content):
    caller = inspect.getframeinfo(inspect.currentframe().f_back)[2]
    print "[%s] [%s] %s" % (str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), caller, content)


def log_error(content):
    caller = inspect.getframeinfo(inspect.currentframe().f_back)[2]
    print "[***ERROR***][%s] [%s] %s" % (str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), caller, content)


def _exec_command(command):
    """ Run command from args, and return a tuple (returned code, stdout, stderr) """

    log("Run command for '%s'" % command)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    p_status = p.wait()
    return p_status, output


def current_data_time_str():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
