import time
import traceback
import logging


class FuncExecClient(object):
    _locust_environment = None

    def __init__(self, req_type: str, req_name: str, add_args: int = 0):
        self.req_type = req_type
        self.req_name = req_name
        self.add_args = add_args

    def exec(self, func, *args, **kwargs):
        result = 'Error'
        report_line = self.req_name
        if self.add_args:
            suffix = ','.join(args[0:self.add_args])
            report_line = f"{report_line} {suffix}"
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
        except RuntimeError as ex:
            logging.debug(traceback.format_exc())
            test_time = int((time.time() - start_time) * 1000)
            self._locust_environment.events.request_failure.fire(
                request_type=self.req_type,
                name=f'{report_line}: {result}',
                response_time=test_time,
                response_length=0,
                exception=ex)
        else:
            test_time = int((time.time() - start_time) * 1000)
            self._locust_environment.events.request_success.fire(
                request_type=self.req_type,
                name=f'{report_line}: {result}',
                response_time=test_time,
                response_length=0)

        return result
