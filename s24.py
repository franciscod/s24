#!/usr/bin/python

import itertools
import functools
import operator

def prod(factors):
    return functools.reduce(operator.mul, factors, 1)

class Valor():
    def __lt__(self, other):
        return self.v() < other.v()

class Carta(Valor):
    def __init__(self, a):
        self.a = a

    def __repr__(self):
        return "C(%d)" % self.a

    def __str__(self):
        return "%d" % self.a

    def __eq__(self, other):
        return self.a == other.a

    def __hash__(self):
        return hash(self.a)

    def v(self):
        return self.a

class Operacion(Valor):
    pass

class OperacionBin(Operacion):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __repr__(self):
        return "%s(%s,%s)" % (self.__class__.__name__, repr(self.a), repr(self.b))

    def __str__(self):
        return "%s%s%s" % (self.paren(self.a), self.sym, self.paren(self.b))

    def __eq__(self, other):
        return (self.a == other.a) and (self.b == other.b)

    def __hash__(self):
        return hash((self.a, self.b))

    def paren(self, other):
        p = True

        if isinstance(other, Carta):
            p = False

        if p:
            return "(%s)" % other
        return other

    def v(self):
        return self.op(self.a.v(), self.b.v())


class OperacionBinConmuta(OperacionBin):
    def __init__(self, a, b):
        if b.v() > a.v():
            a, b = b, a
        super(OperacionBinConmuta, self).__init__(a, b)

    def __eq__(self, other):
        return ((self.a == other.a) and (self.b == other.b)) or ((self.a == other.b) and (self.b == other.a))

    def __hash__(self):
        return hash((self.a, self.b)) + hash((self.b, self.a))


class Suma(OperacionBinConmuta):
    op = operator.add
    sym = '+'


class Resta(OperacionBin):
    op = operator.sub
    sym = '-'


class Producto(OperacionBinConmuta):
    op = operator.mul
    sym = '*'


class Cociente(OperacionBin):
    op = operator.truediv
    sym = '/'

class SumaAlgebraica(Operacion):
    pos = ()
    neg = ()

    def __init__(self, op):
        pos, neg = self._decompose(op)
        self.pos = tuple(p for p in sorted(pos, reverse=True))
        self.neg = tuple(n for n in sorted(neg, reverse=True))

    def _decompose(self, op):
        if isinstance(op, (Suma, Resta)):
            ap, an = self._decompose(op.a)
            bp, bn = self._decompose(op.b)

            if isinstance(op, Suma):
                return ap+bp, an+bn

            if isinstance(op, Resta):
                return ap+bn, an+bp

        if isinstance(op, SumaAlgebraica):
            return op.pos, op.neg

        return (op,), ()

    def __repr__(self):
        return "%s(%s,%s)" % (self.__class__.__name__, repr(self.pos), repr(self.neg))

    def __str__(self):
        s = ""

        sign = {False: "+", True: ""}
        first = True
        for i in self.pos:
            s += sign[first] + str(i)
            if first:
                first = False

        for i in self.neg:
            s += "-" + str(i)

        return s

    def __eq__(self, other):

        if not isinstance(other, SumaAlgebraica):
            return False

        return (self.pos == other.pos) and (self.neg == other.neg)

    def __hash__(self):
        return hash((self.pos, self.neg))

    def v(self):
        return sum((p.v() for p in self.pos)) - sum((n.v() for n in self.neg))

class Fraccion(Operacion):
    num = ()
    den = ()

    def __init__(self, op):
        num, den = self._decompose(op)
        self.num = tuple(n for n in sorted(num, reverse=True))
        self.den = tuple(d for d in sorted(den, reverse=True))

    def _decompose(self, op):
        if isinstance(op, (Producto, Cociente)):
            ap, an = self._decompose(op.a)
            bp, bn = self._decompose(op.b)

            if isinstance(op, Producto):
                return ap+bp, an+bn

            if isinstance(op, Cociente):
                return ap+bn, an+bp

        if isinstance(op, Fraccion):
            return op.num, op.den

        return (op,), ()


    def __repr__(self):
        return "%s(%s,%s)" % (self.__class__.__name__, repr(self.num), repr(self.den))

    def __str__(self):
        s = ""

        sign = {False: "*", True: ""}
        first = True
        for i in self.num:
            si = self.paren(i)
            s += sign[first] + si
            if first:
                first = False


        if self.den:
            s += "/"

            sign = {False: "*", True: ""}
            first = True
            for i in self.den:
                si = self.paren(i)
                s += sign[first] + si
                if first:
                    first = False

        return s

    def paren(self, other):
        p = True

        if isinstance(other, Carta):
            p = False

        if p:
            return "(%s)" % other
        return str(other)

    def __eq__(self, other):

        if not isinstance(other, Fraccion):
            return False

        return (self.num == other.num) and (self.den == other.den)

    def __hash__(self):
        return hash((self.num, self.den))

    def v(self):
        return prod((p.v() for p in self.num)) / prod((n.v() for n in self.den))

def cuentas(a, b):

    for op in (Suma(a, b), Resta(a, b), Resta(b, a)):
        yield SumaAlgebraica(op)


    def fracs():
        yield Producto(a, b)

        if b.v() != 0:
            yield Cociente(a, b)

        if a.v() != 0:
            yield Cociente(b, a)

    for op in fracs():
        yield Fraccion(op)


def o(ga, gb):
    sa = set(ga)
    sb = set(gb)

    for a in sa:
        for b in sb:
            yield from cuentas(a, b)

def tupla_1_carta(n):
    return (Carta(int(n)), )

formas = (
        lambda a, b, c, d: o(o(o(a, b), c), d),
        lambda a, b, c, d: o(o(a, b), o(c, d)),
)

def solve(ns, target=24):
    cartas = map(tupla_1_carta, ns)

    for p in itertools.permutations(cartas):
        for f in formas:
            for raiz in f(*p):
                if raiz.v() == target:
                    yield raiz

if __name__ == '__main__':
    import sys

    if not 5 <= len(sys.argv) <= 6:
        print ("usage: " + sys.argv[0] + " n1 n2 n3 n4 [target]")
        exit()

    ns = sys.argv[1:5]
    kwargs = {}

    if len(sys.argv) == 6:
        kwargs['target'] = int(sys.argv[5])

    sol = set(solve(ns, **kwargs))

    for each in sol:
        print (each)

    for each in sol:
        print (repr(each))
