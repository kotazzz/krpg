import ast
import datetime
import math
import operator as op
import random
import time
from functools import reduce

import lark


def register(name):
    def decorator(func):
        return Function(name, func)

    return decorator


class Lib:
    def other_data(self):
        return {}

    def export(self):
        return {
            i.name: i.func
            for i in [getattr(self, i) for i in dir(self)]
            if i.__class__.__name__ == "Function"
        } | self.other_data()


class Function:
    def __init__(self, name, func):
        self.name = name
        self.func = func


class Value:
    def __init__(self, data):
        self.data = data

    def value(self, env):
        return env.get(self.name(), None)

    def name(self):
        return self.data["v"]


class Environment(dict):
    def extract(self, obj):
        return obj.value(self) if isinstance(obj, Value) else obj

    def extracts(self, *objs):
        return [self.extract(i) for i in objs]


class EvalProcessor:
    def __init__(self, environment_master):
        self.avaliable_operators = {
            ast.Add: op.add,
            ast.Sub: op.sub,
            ast.Mult: op.mul,
            ast.Div: op.truediv,
            ast.Pow: op.pow,
            ast.BitXor: op.xor,
            ast.USub: op.neg,
            ast.MatMult: op.matmul,
            ast.LShift: op.lshift,
            ast.RShift: op.rshift,
            ast.BitOr: op.or_,
            ast.BitAnd: op.and_,
            ast.FloorDiv: op.floordiv,
            ast.Mod: op.mod,
            ast.Invert: op.invert,
            ast.Not: op.not_,
            ast.Eq: op.eq,
            ast.NotEq: op.ne,
            ast.Lt: op.lt,
            ast.LtE: op.le,
            ast.Gt: op.gt,
            ast.GtE: op.ge,
            ast.Is: op.is_,
            ast.IsNot: op.is_not,
            ast.In: op.contains,
            ast.NotIn: lambda a, b: not op.contains(a, b),
            ast.And: lambda *args: all(args),
            ast.Or: lambda *args: any(args),
            ast.UAdd: op.pos,
            ast.USub: op.neg,
        }

        self.environment_master = environment_master

    @property
    def env(self):
        return self.environment_master()

    def node_eval(self, node, env: dict):
        operators = self.avaliable_operators
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.BinOp):
            return operators[type(node.op)](
                self.node_eval(node.left, env=env),
                self.node_eval(node.right, env=env),
            )
        elif isinstance(node, ast.BoolOp):
            return operators[type(node.op)](
                *[self.node_eval(value, env=env) for value in node.values]
            )
        elif isinstance(node, ast.Compare):
            return operators[type(node.ops[0])](
                self.node_eval(node.left, env=env),
                self.node_eval(node.comparators[0], env=env),
            )
        elif isinstance(node, ast.UnaryOp):
            return operators[type(node.op)](self.node_eval(node.operand, env=env))
        elif isinstance(node, ast.Name):
            return env[node.id]
        elif isinstance(node, ast.Call):
            return self.node_eval(node.func, env=env)(
                *[self.node_eval(arg, env=env) for arg in node.args]
            )
        elif isinstance(node, ast.Subscript):
            return self.node_eval(node.value, env)[self.node_eval(node.slice, env)]
        else:
            raise Exception("invalid eval type: ", node)

    def eval_expression(self, expr: str, env=None):
        if env is None:
            env = self.env
        return self.node_eval(ast.parse(expr, mode="eval").body, env)


class KotazyTransformer(lark.Transformer):
    start = lambda s, items: {"i": items[0], "b": items[1]}
    full_import = lambda s, items: {
        "w": [i[1][0] for i in items if i[0] == "w"],
        "p": {i[1]: i[2] for i in items if i[0] == "p"},
    }
    whole_import = lambda s, items: ["w", [i["v"] for i in items]]
    partial_import = lambda s, items: ["p", items[0]["v"], [i["v"] for i in items][1:]]
    module = lambda s, items: {"t": "m", "b": list(items)}
    call = lambda s, items: {"t": "c", "n": items[0]["v"], "a": items[1:]}
    expr = lambda s, items: items[0]
    identifier = lambda s, items: {"t": "i", "v": items[0].value}
    string = lambda s, items: {"t": "s", "v": items[0].value}
    number = lambda s, items: {"t": "n", "v": items[0].value}
    estring = lambda s, items: {"t": "e", "v": items[0].value}


class KotazyParser:
    def __init__(self):
        grammar = r"""
        start: full_import module

        module: "{" "}"
            | "{" call (";" call)* "}"
        
        full_import: (import_stmt ("|" import_stmt)*)?

        import_stmt: identifier -> whole_import
              | identifier ":" identifier("," identifier)*  -> partial_import

        call: identifier "(" ")"
            | identifier "(" expr ("," expr)* ")"

        expr: identifier
            | string
            | number
            | call
            | module
            | estring
        
        estring: "`" /[^\`]+/ "`"

        identifier: CNAME
        string: ESCAPED_STRING
        number: SIGNED_NUMBER

        %import common.CNAME
        %import common.ESCAPED_STRING
        %import common.SIGNED_NUMBER
        %import common.WS
        
        %ignore "/" /(.|\n)*?/ "/"
        %ignore WS
        
        """
        self.parser = lark.Lark(grammar, start="start", parser="lalr")

    def parse(self, program):
        tree = self.parser.parse(program)
        return KotazyTransformer().transform(tree)


class KotazyRunner:
    def __init__(self):
        self.parser = KotazyParser()
        self.evalproc = EvalProcessor(lambda: self.environment)
        self.libs = {
            "std": StandartLib,
        }

    def execute_expr(self, expr):
        transforms = {
            "i": lambda data: Value(data),
            "s": lambda data: data["v"].strip('"'),
            "n": lambda data: float(data["v"]) if "." in data["v"] else int(data["v"]),
            "m": lambda data: lambda *a: self.execute_module(data, *a),
            "c": lambda data: self.execute_call(data),
            "e": lambda data: self.evalproc.eval_expression(data["v"]),
        }
        return transforms[expr["t"]](expr)

    def execute_call(self, call, *args):
        args = [self.execute_expr(arg) for arg in call["a"]] + list(args)
        try:
            return self.environment[call["n"]](self.environment, *args)
        except KeyError:
            raise RuntimeError(f"Function {call['n']} not found") from None

    def execute_module(self, module, *args):
        last = None
        for call in module["b"]:
            if call["n"] in self.environment:
                self.environment |= {"args": args}
                last = self.execute_call(call)
            else:
                raise Exception(f"Function {call['n']} not found")
        return last

    def build_environment(self, imports):
        env = {}
        for lib in imports["w"]:
            try:
                env |= self.libs[lib]().export()
            except KeyError:
                raise Exception(f"Library {lib} not found") from None
        for lib, funcs in imports["p"].items():
            try:
                module = self.libs[lib]().export()
                try:
                    funcs = {k: v for k, v in module.items() if k in funcs}
                except KeyError:
                    raise Exception(f"Error in importing {funcs} from {lib}") from None
                else:
                    env |= funcs
            except KeyError:
                raise Exception(f"Library {lib} not found") from None

        self.environment = Environment(env)

    def run(self, program):
        tree = self.parser.parse(program)
        self.build_environment(tree["i"])
        return self.execute_module(tree["b"])


class StandartLib(Lib):
    @register("out")
    def out(env, *texts):
        texts = env.extracts(*texts)
        print(*texts)

    @register("in")
    def inp(env):
        return input()

    @register("set")
    def set(env, name, value):
        name = name.name()
        value = env.extract(value)
        env[name] = value
        return value

    @register("ext")
    def ext(env, obj, index):
        obj = env.extract(obj)
        index = env.extract(index)
        return obj[index]

    @register("ret")
    def ret(env, value):
        return env.extract(value)

    @register("env")
    def env(env):
        for k in env:
            v = env[k]
            if callable(v):
                print(k, "function", sep="\t")
            else:
                print(k, v, sep="\t")

    @register("if")
    def if_(env, condition, true, false):
        condition = env.extract(condition)
        if condition:
            return env.extract(true)()
        else:
            return env.extract(false)()

    @register("while")
    def while_(env, condition, body):
        condition = env.extract(condition)
        body = env.extract(body)
        while condition():
            body()

    @register("for")
    def for_(env, name, iterable, body):
        name = name.name()
        iterable = env.extract(iterable)
        body = env.extract(body)
        for i in iterable:
            env[name] = i
            body()

    @register("try")
    def try_(env, body, catch, else_stmt=None, finally_stmt=None):
        body = env.extract(body)
        catch = env.extract(catch)
        else_stmt = env.extract(else_stmt) if else_stmt else lambda: 0
        finally_stmt = env.extract(finally_stmt) if finally_stmt else lambda: 0
        try:
            body()
        except Exception as e:
            catch(e)
        else:
            else_stmt()
        finally:
            finally_stmt()

    @register("red")
    def reduce(env, func, iterable):
        func = env.extract(func)
        iterable = env.extract(iterable)
        return reduce(func, iterable)

    @register("map")
    def map_(env, func, iterable):
        func = env.extract(func)
        iterable = env.extract(iterable)
        return map(func, iterable)

    @register("flr")
    def filter_(env, func, iterable):
        func = env.extract(func)
        iterable = env.extract(iterable)
        return filter(func, iterable)

    @register("lst")
    def list_(env, *items):
        return env.extracts(*items)

    @register("rng")
    def range_(env, *args):
        args = env.extracts(*args)
        return range(*args)

    def other_data(self):
        x = lambda e, v: e.extract(v)
        xs = lambda e, *vs: e.extracts(*vs)
        return {
            "int": lambda e, a, b=10: int(x(e, a), x(e, b)),
            "oct": lambda e, a: oct(x(e, a)),
            "hex": lambda e, a: hex(x(e, a)),
            "bin": lambda e, a: bin(x(e, a)),
            "chr": lambda e, a: chr(x(e, a)),
            "ord": lambda e, a: ord(x(e, a)),
            "float": lambda e, a: float(x(e, a)),
            "str": lambda e, a: str(x(e, a)),
            "bool": lambda e, a: bool(x(e, a)),
            "len": lambda e, a: len(x(e, a)),
            "type": lambda e, a: type(x(e, a)),
            "sum": lambda e, *a: sum(xs(e, *a)),
            "min": lambda e, *a: min(xs(e, *a)),
            "max": lambda e, *a: max(xs(e, *a)),
            "abs": lambda e, a: abs(x(e, a)),
            "round": lambda e, a: round(x(e, a)),
        }


class MathLib(Lib):
    def other_data(self):
        x = lambda e, v: e.extract(v)
        xs = lambda e, *vs: e.extracts(*vs)

        return {
            "pow": lambda e, a, b: x(e, a) ** x(e, b),
            "mod": lambda e, a, b: x(e, a) % x(e, b),
            "sqrt": lambda e, a: x(e, a) ** 0.5,
            "log": lambda e, a, b: math.log(x(e, a), x(e, b)),
            "ln": lambda e, a: math.log(x(e, a)),
            "lg": lambda e, a: math.log(x(e, a), 10),
            "exp": lambda e, a: math.exp(x(e, a)),
            "sin": lambda e, a: math.sin(x(e, a)),
            "cos": lambda e, a: math.cos(x(e, a)),
            "tan": lambda e, a: math.tan(x(e, a)),
            "asin": lambda e, a: math.asin(x(e, a)),
            "acos": lambda e, a: math.acos(x(e, a)),
            "atan": lambda e, a: math.atan(x(e, a)),
            "atan2": lambda e, a, b: math.atan2(x(e, a), x(e, b)),
            "sinh": lambda e, a: math.sinh(x(e, a)),
            "cosh": lambda e, a: math.cosh(x(e, a)),
            "tanh": lambda e, a: math.tanh(x(e, a)),
            "asinh": lambda e, a: math.asinh(x(e, a)),
            "acosh": lambda e, a: math.acosh(x(e, a)),
            "atanh": lambda e, a: math.atanh(x(e, a)),
            "hypot": lambda e, a, b: math.hypot(x(e, a), x(e, b)),
            "degrees": lambda e, a: math.degrees(x(e, a)),
            "radians": lambda e, a: math.radians(x(e, a)),
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,
            "ceil": lambda e, a: math.ceil(x(e, a)),
            "floor": lambda e, a: math.floor(x(e, a)),
            "trunc": lambda e, a: math.trunc(x(e, a)),
            "copysign": lambda e, a, b: math.copysign(x(e, a), x(e, b)),
            "factorial": lambda e, a: math.factorial(x(e, a)),
            "gamma": lambda e, a: math.gamma(x(e, a)),
            "lgamma": lambda e, a: math.lgamma(x(e, a)),
            "isfinite": lambda e, a: math.isfinite(x(e, a)),
            "isinf": lambda e, a: math.isinf(x(e, a)),
            "isnan": lambda e, a: math.isnan(x(e, a)),
        }


class RandomLib(Lib):
    def other_data(self):
        x = lambda e, v: e.extract(v)
        xs = lambda e, *vs: e.extracts(*vs)
        return {
            "randint": lambda e, a, b: random.randint(x(e, a), x(e, b)),
            "choice": lambda e, a: random.choice(x(e, a)),
            "choices": lambda e, a, k: random.choices(x(e, a), k=x(e, k)),
            "sample": lambda e, a, k: random.sample(x(e, a), k=x(e, k)),
            "shuffle": lambda e, a: random.shuffle(x(e, a)),
            "random": lambda e: random.random(),
            "uniform": lambda e, a, b: random.uniform(x(e, a), x(e, b)),
            "triangular": lambda e, a, b, c: random.triangular(
                x(e, a), x(e, b), x(e, c)
            ),
            "betavariate": lambda e, a, b: random.betavariate(x(e, a), x(e, b)),
            "expovariate": lambda e, a: random.expovariate(x(e, a)),
            "gammavariate": lambda e, a, b: random.gammavariate(x(e, a), x(e, b)),
            "gauss": lambda e, a, b: random.gauss(x(e, a), x(e, b)),
            "lognormvariate": lambda e, a, b: random.lognormvariate(x(e, a), x(e, b)),
            "normalvariate": lambda e, a, b: random.normalvariate(x(e, a), x(e, b)),
            "vonmisesvariate": lambda e, a, b: random.vonmisesvariate(x(e, a), x(e, b)),
            "paretovariate": lambda e, a: random.paretovariate(x(e, a)),
            "weibullvariate": lambda e, a, b: random.weibullvariate(x(e, a), x(e, b)),
            "seed": lambda e, a: random.seed(x(e, a)),
        }


class TimeLib(Lib):
    def other_data(self):
        x = lambda e, v: e.extract(v)
        xs = lambda e, *vs: e.extracts(*vs)
        return {
            "time": lambda e: time.time(),
            "ctime": lambda e, a: time.ctime(x(e, a)),
            "gmtime": lambda e, a: time.gmtime(x(e, a)),
            "localtime": lambda e, a: time.localtime(x(e, a)),
            "asctime": lambda e, a: time.asctime(x(e, a)),
            "mktime": lambda e, a: time.mktime(x(e, a)),
            "sleep": lambda e, a: time.sleep(x(e, a)),
            "strftime": lambda e, a, b: time.strftime(x(e, a), x(e, b)),
            "strptime": lambda e, a, b: time.strptime(x(e, a), x(e, b)),
            "clock": lambda e: time.clock(),
            "perf_counter": lambda e: time.perf_counter(),
            "process_time": lambda e: time.process_time(),
            "time_ns": lambda e: time.time_ns(),
            "monotonic": lambda e: time.monotonic(),
            "monotonic_ns": lambda e: time.monotonic_ns(),
            "thread_time": lambda e: time.thread_time(),
            "thread_time_ns": lambda e: time.thread_time_ns(),
        }


class DatetimeLib(Lib):
    def other_data(self):
        x = lambda e, v: e.extract(v)
        xs = lambda e, *vs: e.extracts(*vs)
        return {
            "date": lambda e, a, b, c: datetime.date(x(e, a), x(e, b), x(e, c)),
            "datetime": lambda e, a, b, c, d, e2, f: datetime.datetime(
                x(e, a), x(e, b), x(e, c), x(e, d), x(e, e2), x(e, f)
            ),
            "time": lambda e, a, b, c, d: datetime.time(
                x(e, a), x(e, b), x(e, c), x(e, d)
            ),
            "timedelta": lambda e, a, b, c, d, e2, f: datetime.timedelta(
                x(e, a), x(e, b), x(e, c), x(e, d), x(e, e2), x(e, f)
            ),
            "timezone": lambda e, a, b: datetime.timezone(x(e, a), x(e, b)),
            "tzinfo": lambda e, a, b, c, d, e2, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z: datetime.tzinfo(
                x(e, a),
                x(e, b),
                x(e, c),
                x(e, d),
                x(e, e2),
                x(e, f),
                x(e, g),
                x(e, h),
                x(e, i),
                x(e, j),
                x(e, k),
                x(e, l),
                x(e, m),
                x(e, n),
                x(e, o),
                x(e, p),
                x(e, q),
                x(e, r),
                x(e, s),
                x(e, t),
                x(e, u),
                x(e, v),
                x(e, w),
                x(e, x),
                x(e, y),
                x(e, z),
            ),
        }


class PrintLib(Lib):
    def other_data(self):
        x = lambda e, v: e.extract(v)
        xs = lambda e, *vs: e.extracts(*vs)
        return {
            "print": lambda e, *text, sep, end, file, flush: print(
                *xs(e, *text),
                sep=x(e, sep),
                end=x(e, end),
                file=x(e, file),
                flush=x(e, flush),
            ),
            "fmt": lambda e, text, *args: text.format(*xs(e, *args)),
        }


def get_runner():
    runner = KotazyRunner()
    runner.libs = {
        "std": StandartLib,
        "math": MathLib,
        "rnd": RandomLib,
        "time": TimeLib,
        "dt": DatetimeLib,
        "print": PrintLib,
    }
    return runner


if __name__ == "__main__":
    runner = get_runner()
    funcount = len(
        reduce(lambda a, b: a | b, [x().export() for x in runner.libs.values()])
    )
    stdcount = len(StandartLib().export())
    text = [
        f"Functions: {funcount} ({stdcount} from std)",
        f'Libs: {len(runner.libs)} - {", ".join(runner.libs.keys())}',
    ]
    print(*text, sep="\n")
    print("-" * len(max(text, key=len)))

    program = open(input("File: "), "r").read()
    """
    std{
        / factorial(n) /
        set(factorial, {
            set(arg1, ext(args, 1));
            if(`arg1 == 0`, 
                {set(res, 1)},
                {
                    set(res, red(
                        {ret(`args[0] * args[1]`)}, 
                        rng(1, `arg1+1`)
                    ))
                }
            );
            ret(res)
        });
        out("Давай посчитаем факториал от твоего числа: ");
        set(i, in());
        set(t, "!:");
        out("Твой факториал", `i+t` , factorial(int(i)))
    }
    """
    r = runner.run(program)
    if r is not None:
        print("Return:", r)
    input("Waiting for exit...")
