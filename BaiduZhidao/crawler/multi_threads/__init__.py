__author__ = 'xwk'

from threading import Thread
from Queue import Queue

global my_queue
my_queue = Queue()
class MyThread1(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):

        put_data = "you producer data"
        my_queue.put(put_data)
        # write this thread task
        pass

class MyThread2(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        get_data = my_queue.get()
        print get_data
        # write this thread task
        pass

def test(i, t):
    print i == 1

if __name__ == '__main__':
    """
    thread1 = MyThread1()
    thread2 = MyThread2()
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    """

    import threadpool
    pool = threadpool.ThreadPool(10)
    requests = threadpool.makeRequests(test, [([1,2], None), ([2,3], None)])
    [pool.putRequest(req) for req in requests]
    pool.wait()











