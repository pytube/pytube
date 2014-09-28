import re


class JSVM(object):

    _memory = {}
    _program = []
    _js_methods = {}

    def __init__(self, code=""):
        # TODO: parse automatically the 'swap' method
        # function Bn(a,b){var c=a[0];a[0]=a[b%a.length];a[b]=c;return a};
        def _swap(args):
            a = list(args[0])
            b = int(args[1])
            c = a[0]
            a[0] = a[b % len(a)]
            a[b] = c
            return "".join(a)

        def _split(args):
            return ""

        def _slice(args):
            return args[0][int(args[1]):]

        def _reverse(args):
            return args[0][::-1]

        def _join(args):
            return "".join(args[0])

        def _assign(args):
            return args[0]

        def _get(args):
            return self._memory[args[0]]

        self._js_methods = {
            "split": _split,
            "slice": _slice,
            "reverse": _reverse,
            "join": _join,
            "$swap": _swap,
            "$assign": _assign,
            "$get": _get
        }

        if code != "":
            self.compile(code)

    def compile(self, code):
        self._program = []
        regex = re.compile(r"(\w+\.)?(\w+)\(([^)]*)\)")
        code = code.replace("return ", "return=")
        for instruction in code.split(";"):
            #print instruction
            var, method = instruction.split("=")
            m = regex.match(method)
            if m is None:
                arguments = [method[1:-1]]
                method = "$assign"
            else:
                m = m.groups()
                #print m
                arguments = []
                pre_args = [m[0][:-1]] if m[0] is not None else []
                pre_args += m[2].split(",")
                for a in pre_args:
                    if a is None or a == "":
                        continue
                    # Replace variables with his value
                    arguments += [JSMethod(self._js_methods["$get"], a) if not a[0] == '"' and not a[0] == '' and not a.isdigit() else a]
                # Suppose that an undefined method is '$swap' method
                method = "$swap" if m[1] not in self._js_methods.keys() else m[1]
            self._program += [(var, JSMethod(self._js_methods[method], arguments))]
        return self._program

    def setPreinterpreted(self, program):
        self._program = program

    def run(self):
        for ins in self._program:
            #print "%s(%s)" % (ins[1]._m.__name__, ins[1]._a)
            if ins[0] not in self._memory:
                self._memory[ins[0]] = None
            self._memory[ins[0]] = ins[1].run()
        return self._memory


class JSMethod(object):

    def __init__(self, method, args):
        self._m = method
        self._a = args

    def run(self):
        args = [a.run() if isinstance(a, JSMethod) else a for a in self._a]
        return self._m(args)

    def __repr__(self):
        return "%s(%s)" % (self._m.__name__, self._a)
