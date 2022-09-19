import multiprocessing
import time

class Err(Exception):
    pass

def wrapper(n):
    for i in range(n):
        print(i)
        if i==8:
            raise Err
        time.sleep(1)

if __name__ == '__main__':
    p = multiprocessing.Process(target=wrapper, name="Test", args=(600,))

    try:
        p.start()
        time.sleep(600)
    except Err:
        pass

    p.terminate()
    p.join()