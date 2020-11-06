import time


class FuncExecClient(object):
    _locust_environment = None    

    def __init__(self, req_type, req_name):
        self.type = req_type
        self.name = req_name
        
    def exec(self, func, *args, **kwargs):
        result = None
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
        except Exception as ex: 
            test_time = int((time.time() - start_time) * 1000)
            self._locust_environment.events.request_failure.fire(
                request_type=self.type, 
                name=self.name, 
                response_time=test_time, 
                response_length=0, 
                exception=ex)
        else:
            test_time = int((time.time() - start_time) * 1000)
            self._locust_environment.events.request_success.fire(
                request_type=self.type, 
                name=self.name, 
                response_time=test_time, 
                response_length=0)

        return result