from locust import HttpUser, between, task
from locust import events
import os

@events.test_start.add_listener
def on_test_start(**kw):
    print(">>> a new test is starting")


class WebsiteUser(HttpUser):
    wait_time = between(1, 2)
    host = os.getenv('PLT_TEST_HOST', 'http://www.google.com')
        
    
    @task
    def root(self):
        print('>>> task invoked')
        self.client.get("/")