from functools import reduce
# $Id: pyutils.py 45 2013-10-06 15:57:20Z korsnack $
#!/bin/python

#===================
def iif(x, y = True, z = False):
    """
    Example:
    >>> iif(3 in range(10), range(10))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    if x: return y
    else: return z

#===================
def ior(x, *y):
    """
    example
    """
    if x: return x
    elif y: return ior(*y)
    else: return x

#===================
def foldList(data_list,       # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
             function = "add" # possibilities: ["add", "subtract",
                              #                 "divide", "multiply"]
             ):
    """
    Example:
    >>> foldList(range(10), "subtract")
    -45.0
    """
    if function == "add":
        def add(x, y): return float(x) + float(y)
        return reduce(add, data_list)
    elif function == "subtract":
        def subtract(x, y): return float(x) - float(y)
        return reduce(subtract, data_list)
    elif function == "divide":
        def divide(x, y): return float(x) / float(y)
        return reduce(divide, data_list)
    elif function == "multiply":
        def multiply(x, y): return float(x) * float(y)
        return reduce(multiply, data_list)

#===================
def flatten(list):
   """
   Returns a single, flat list which contains all elements retrieved
   from the sequence and all recursively contained sub-sequences
   (iterables).

   Example:
   >>> flatten([[[1, 2, 3], (42, None)], [4, 5], [6], 7, (8, 9, 10)])
   [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]
   """
   result = []
   for element in list:
       #if isinstance(element, (list, tuple)):
       if hasattr(element, "__iter__") and not isinstance(element, str):
           result.extend(flatten(element))
       else:
           result.append(element)
   return result

#===================
def listCombinations(seq, length):
    if not length: return [[]]
    else:
        l = []
        for i in range(len(seq)):
            for result in listCombinations(seq[i + 1:], length - 1):
                l += [[seq[i]] + result]
        return l
