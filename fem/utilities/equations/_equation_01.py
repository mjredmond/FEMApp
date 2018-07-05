"""
Project.x

Author: Michael Redmond

"""

from __future__ import print_function, absolute_import
from six import iteritems
from six.moves import range


import ast

from types import ModuleType, FunctionType

# noinspection PyUnresolvedReferences
from six.moves import builtins
import math
import keyword


_builtins = dir(builtins)
_builtins.extend(dir(math))
_builtins.extend(keyword.kwlist)
_builtins = set(_builtins)


def parse_equation_01(eqn_str, func_name='function_name'):
    eqn_str = eqn_str.replace("'", "").replace('{', '').replace('}', '').replace('=', '').replace('^', '**')

    vars = [
        node.id for node in ast.walk(ast.parse(eqn_str))
        if isinstance(node, ast.Name)
        ]

    vars_ = list(vars)

    for var in vars_:
        if var in _builtins:
            vars.remove(var)

    eqn_str = """from math import *\ndef %s%s:\n    return %s""" % (func_name, str(tuple(vars)).replace("'", ""), eqn_str)

    # print(eqn_str)

    try:
        compiled = compile(eqn_str, '', 'exec')
    except Exception:
        print(1)
        return None, None

    module = ModuleType(func_name)

    try:
        exec(compiled, module.__dict__)
    except Exception:
        print(2)
        return None, None

    _function = getattr(module, func_name)

    if not isinstance(_function, FunctionType):
        print(3)
        return None, None

    return _function, vars


if __name__ == '__main__':
    eqn = "max(0, 1)"

    print(parse_equation_01(eqn)[0]())
