import time

def retry(maxTries: int, sleepSeconds: int, func, *arg) -> None:
    for i in range(1, maxTries + 1):
        time.sleep(sleepSeconds)
        err = None
        try:
            return func(*arg)
        except Exception as ex:
            print(f'Tried {i} - {ex}')
            err = str(ex)

    raise RuntimeError(f"{err} - exhausted {maxTries} retries")