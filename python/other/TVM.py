from math import log
from lib.LogFile import LogFile

class TVM (object):
    '''
    A Time Value of Money object works like a financial calculator. (Literally,
    I implemented this using the Texas Instruments BAII Plus Financial Calculator's
    instruction manual.) Given any four of {n, i, pmt, pv, fv} TVM object can
    calculate the fifth. For example:

    Example: What is the annual interest rate on a $6,000, 3 year loan, paying $200/month?
    >>> TVM(n=12*3, pv=6000, pmt=-200, fv=0).i*12
    0.122489388032796
    '''

    def __init__(
        self,
        n = None,
        i = None,
        pv = None,
        pmt = None,
        fv = None,
        beginning = False
    ):
        self.lg = LogFile()
        self.__n = n
        self.__i = i
        self.__pv = pv
        self.__pmt = pmt
        self.__fv = fv
        self.__g = 1+i if beginning else 1

    def __repr__(self):
        return "TVM(n={}, i={}, pv={}, pmt={}, fv={})".format(
            self.__n, self.__i, self.__pv, self.__pmt, self.__fv
        )

    def get_n(self):
        if not self.__i:
            self.__n = -(self.__pv+self.__fv)/self.__pmt
        else:
            self.__n = log(
                (self.__pmt*self.__g-self.__fv*self.__i)/
                (self.__pmt*self.__g+self.__pv*self.__i)
            )/log(1+self.__i)
        return self.__n
    def set_n(self, value):
        self.__n = value
    n = property(get_n, set_n, None, 'number of payments')

    def get_i(self):
        INTTOL = 1e-7
        ITERLIMIT = 1e3
        if self.__i:
            i0 = self.__i
        else:
            i0 = 0.01
        i1 = 1.1*i0
        def f(tvm, i):
            if not i:
                return  -(tvm.__pv+tvm.__fv)/self.__n
            return -(i/self.__g)*(
                tvm.__pv+(tvm.__pv+tvm.__fv)/((1+i)**self.__n-1)
            )-tvm.__pmt
        fi0 = f(self, i0)
        if abs(fi0) < INTTOL:
            self.__i = i0
            return i0
        else:
            n = 0
            while True:
                fi1 = f(self, i1)
                if abs(fi1) < INTTOL:
                    break
                if n > ITERLIMIT:
                    self.lg.warning(
                        "Failed to converge; exceeded iteration limit"
                    )
                    break
                slope = (fi1-fi0)/(i1-i0)
                i2 = i0-fi0/slope
                fi0 = fi1
                i0 = i1
                i1 = i2
                n += 1
            self.__i = i1
            return self.__i
    def set_i(self, value):
        self.__i = value
    i = property(get_i, set_i, None, 'interest rate')

    def get_pv(self):
        if not self.__i:
            self.__pv = -(self.__fv+self.__pmt*self.__n)
        else:
            x = self.__pmt*self.__g/self.__i
            self.__pv = (x-self.__fv)/(1+self.__i)**self.__n-x
        return self.__pv
    def set_pv(self, value):
        self.__pv = value
    pv = property(get_pv, set_pv, None, 'present value')

    def get_pmt(self):
        if not self.__i:
            self.__pmt = -(self.__pv+self.__fv)/self.__n
        else:
            self.__pmt = -(self.__i/self.__g)*(
                self.__pv+(self.__pv+self.__fv)/((1+self.__i)**self.__n-1)
            )
        return self.__pmt
    def set_pmt(self, value):
        self.__pmt = value
    pmt = property(get_pmt, set_pmt, None, 'payment')

    def get_fv(self):
        if not self.__i:
            self.__fv = -(self.__pv+self.__pmt*self.__n)
        else:
            x = self.__pmt*self.__g/self.__i
            self.__fv = x-(1+self.__i)**self.__n*(self.__pv+x)
        return self.__fv
    def set_fv(self, value):
        self.__fv = value
    fv = property(get_fv, set_fv, None, 'future value')
