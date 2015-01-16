from itertools import permutations
from operator import add, sub, mul, truediv as div

def paren(obj):
    if isinstance(obj, Carta):
        return obj
    return "(%s)" % obj

class Carta():
    def __init__(self, a):
        self.a = a

    def __repr__(self):
        return "Carta(%d)" % self.a

    def __str__(self):
        return "%d" % self.a

    def __eq__(self, other):
        return self.a == other.a

    def __hash__(self):
        return hash(self.a)

    def v(self):
        return self.a

class Operacion():
    pass

class OperacionBin(Operacion):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __repr__(self):
        return "%s(%s,%s)" % (self.__class__.__name__, repr(self.a), repr(self.b))

    def __str__(self):
        return "%s%s%s" % (paren(self.a), self.sym, paren(self.b))

    def __eq__(self, other):
        return (self.a == other.a) and (self.b == other.b)

    def __hash__(self):
        return hash((self.a, self.b))

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
    op = add
    sym = '+'


class Resta(OperacionBin):
    op = sub
    sym = '-'


class Producto(OperacionBinConmuta):
    op = mul
    sym = '*'


class Cociente(OperacionBin):
    op = div
    sym = '/'

class SumaAlgebraica(Operacion):
    pos = ()
    neg = ()

    def __init__(self, pos, neg):
        self.pos = tuple(p for p in sorted(pos, reverse=True))
        self.neg = tuple(n for n in sorted(neg, reverse=True))

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
        return (self.pos == other.pos) and (self.neg == other.neg)

    def __hash__(self):
        return hash((self.pos, self.neg))

    def v(self):
        return sum(self.pos) - sum(self.neg)

def es_pura_suma(op):
    if not isinstance(op, (Carta, Suma, Resta, SumaAlgebraica)):
        return False

    if isinstance(op, OperacionBin):
        return es_pura_suma(op.a) and es_pura_suma(op.b)

    return True

def desarma_suma_posneg(op):
    # requiere es_pura_suma(op)

    if isinstance(op, Carta):
        return (op.a,), ()

    if isinstance(op, OperacionBin):
        ap, an = desarma_suma_posneg(op.a)
        bp, bn = desarma_suma_posneg(op.b)

        if isinstance(op, Suma):
            return ap+bp, an+bn

        if isinstance(op, Resta):
            return ap+bn, an+bp

    if isinstance(op, SumaAlgebraica):
        return op.pos, op.neg

def precedes(op1, op2):
    order = {
            Suma: 0,
            Resta: 0,
            SumaAlgebraica: 0,
            Producto: 1,
            Cociente: 1,
            }

    return order[op1.__class__] > order[op2.__class__]

def cuentas(a, b):
    sumas = (Suma(a, b), Resta(a, b), Resta(b, a))

    if es_pura_suma(a) and es_pura_suma(b):
        for su in sumas:
            yield SumaAlgebraica(*desarma_suma_posneg(su))
    else:
        yield from sumas

    yield Producto(a, b)

    if b.v() != 0:
        yield Cociente(a, b)

    if a.v() != 0:
        yield Cociente(b, a)

def o(va, vb):
    for a in va:
        for b in vb:
            yield from cuentas(a,b)

def tupla_1_carta(n):
    return (Carta(int(n)), )

formas = (
        lambda a, b, c, d: o(o(o(a, b), c), d),
        lambda a, b, c, d: o(o(a, b), o(c, d)),
)

def s(a, b, c, d, t=24):
    ns = a, b, c, d
    cartas = map(tupla_1_carta, ns)
    for p in permutations(cartas):
        for f in formas:
            for raiz in f(*p):
                if raiz.v() == t:
                    yield raiz

if __name__ == '__main__':
    import sys

    if not 5 <= len(sys.argv) <= 6:
        print ("usage: " + sys.argv[0] + " A B C D [RESULT]")
        exit()

    args = sys.argv[1:5]
    kwargs = {}

    if len(sys.argv) == 6:
        kwargs[t] = sys.argv[5]

    sol = set(s(*args, **kwargs))

    for each in sol:
        print (each)

    for each in sol:
        print (repr(each))
