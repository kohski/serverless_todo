import pytest
import sys
import os
from datetime import datetime
import uuid


sys.path.append(os.path.abspath(os.path.dirname(
    os.path.abspath(__file__)) + "/../../src/user/"))


@ pytest.fixture()
def context():
    # id = str(uuid.uuid4())
    stream = str(uuid.uuid4()).replace("-", "")
    func_name = "test_function"
    account = "999999999999"
    yyyymmdd = datetime.now().strftime("%Y/%m/%d")

    class context():
        def __init__(self):
            self.aws_request_id = str(uuid.uuid4())
            self.log_group_name = '/aws/lambda/' + func_name
            self.log_stream_name = yyyymmdd + '/[$LATEST]' + stream
            self.function_name = 'print_context'
            self.memory_limit_in_mb = '128'
            self.function_version = '$LATEST'
            self.invoked_function_arn = 'arn:aws:lambda:ap-northeast-1:' + \
                account + ':function:' + func_name
            self.client_context = None
            self.identity = '999'
    return context()
