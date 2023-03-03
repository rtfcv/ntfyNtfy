import time
import datetime as dt
import re
import logging
import logging.handlers
import sys
import json
import subprocess

sys.dont_write_bytecode = True
import pyNotify
import settings


# Creating a Logger Instance
class LogWrapper:
    def __init__(self, file_name):
        self.myLog = logging.Logger(file_name, level=logging.INFO)

        self.logMaxBytes = 10**5

        self.myLog_file = logging.handlers.RotatingFileHandler(
                f'logs/{file_name}',
                maxBytes=10*self.logMaxBytes,
                backupCount=5)
        self.myLog_file.setLevel(logging.INFO)
        self.myLog_file.terminator = ''

        self.myLog_stdout = logging.StreamHandler()
        self.myLog_stdout.setStream(sys.stderr)
        self.myLog_stdout.terminator = ''

        self.myLog.addHandler(self.myLog_file)
        self.myLog.addHandler(self.myLog_stdout)

    def info(self, msg, *args, **kwargs):
        self.myLog_file.maxBytes = 10*self.logMaxBytes
        self.myLog.info(msg, *args, **kwargs)

    def infoNewLine(self):
        self.myLog_file.maxBytes = self.logMaxBytes
        self.myLog.info('\n')
        self.myLog_file.maxBytes = 10*self.logMaxBytes

    def warning(self, msg, *args, **kwargs):
        self.myLog_file.maxBytes = 10*self.logMaxBytes
        self.myLog.warning(msg, *args, **kwargs)

    def warningNewLine(self):
        self.myLog_file.maxBytes = self.logMaxBytes
        self.myLog.warning('\n')
        self.myLog_file.maxBytes = 10*self.logMaxBytes

    def fatal(self, msg, *args, **kwargs):
        self.myLog_file.maxBytes = 10*self.logMaxBytes
        self.myLog.fatal(msg, *args, **kwargs)

    def fatalNewLine(self):
        self.myLog_file.maxBytes = self.logMaxBytes
        self.myLog.fatal('\n')
        self.myLog_file.maxBytes = 10*self.logMaxBytes


myLog = LogWrapper('gachalab.log')


def logFatal(myLog, e):
    myLog.fatalNewLine()
    myLog.fatal(
        f'{dateText()}:\tERROR:\t{e.__class__.__name__}: ``{e}\'\'',
        exc_info=True)
    myLog.fatalNewLine()
    myLog.fatalNewLine()


# Creating a notification Instance
notific = pyNotify.PyNotify()


# prefix for logs
def dateText():
    return dt.datetime.now().isoformat("_", "seconds")

# https://qiita.com/megmogmog1965/items/5f95b35539ed6b3cfa17
def get_lines():
    '''
    :param cmd: list 実行するコマンド.
    :rtype: generator
    :return: 標準出力 (行毎).
    '''
    cmd=f'ntfy sub {settings.TOPICTOKEN}'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        assert proc.stdout is not None
        line = proc.stdout.readline()
        if line:
            yield line

        if not line and proc.poll() is not None:
            break


if __name__ == '__main__':
    for lineBytes in get_lines():
        lineStr = lineBytes.decode('utf-8')
        if len(lineStr)==0:
            continue

        lineData = dict()

        try:
            lineData = json.loads(lineStr)
        except BaseException as e:
            print(f'{e.__class__.__name__}: {e}')
            continue

        sys.stdout.write(str(lineData))

        title = lineData['title'] if 'title' in lineData else ''
        message = lineData['message'] if 'message' in lineData else 'No Message'
        notific.notify('ntfy', title, message)
