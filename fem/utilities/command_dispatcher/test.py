import inspect


def check_types(*args):

    def check_args(func, *args2):
        types = tuple(map(type, args2))

        for i in range(len(types)):
            if not isinstance(types[i], args[i]):
                raise TypeError("Argument types for %s%s do not match! %s" % (func.__name__, str(args), str(types)))

    def add_args_checking(func):
        def _func(*args2):
            check_args(func, *args2)
            return func(*args2)

        return _func

    return add_args_checking


class Dummy(object):

    @check_types(object, int, int, float)
    def func1(self, a, b, c):
        print(a, b, c)



print(type((int, int, float)))