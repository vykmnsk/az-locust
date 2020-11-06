import time
import random
import time



def rand_number(length: int) -> str:
    return str(random.randint(pow(10, length - 1), pow(10, length) - 1))


def retry(maxTries: int, sleepSeconds: int, func, *args, **kwargs):
    for i in range(1, maxTries + 1):
        time.sleep(sleepSeconds)
        err = None
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            print(f'Tried {i} - {ex}')
            err = str(ex)

    raise RuntimeError(f"{err} - exhausted {maxTries} retries")
