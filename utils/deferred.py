class Deferred(object):
    def __init__(self):
        self.callbacks = []
    
    def callback(self, func):
        self.callbacks.append(func)

    def set(self, value):
        for func in self.callbacks:
            func(value)


def monadic(func):
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        def continuation(res):
            try:
                dfr2 = gen.send(res)
            except StopIteration:
                pass
            else:
                dfr2.callback(continuation)
        continuation(None)
    return wrapper




