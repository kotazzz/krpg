class DependObject:
    name = "name"
    version = "0.0.0"
    requires = []

    @staticmethod
    def from_dict(data: dict):
        obj = DependObject()
        obj.name = data["name"]
        obj.version = data["version"]
        obj.requires = data["requires"]
        return obj


def compare_versions(v1, v2) -> int:
    """
    Return 1 if v1 > v2
    Return 0 if v1 == v2
    Return -1 if v1 < v2
    """
    v1 = v1.split(".")
    v2 = v2.split(".")
    for i in range(0, max(len(v1), len(v2))):
        try:
            a = int(v1[i])
        except IndexError:
            a = 0
        try:
            b = int(v2[i])
        except IndexError:
            b = 0
        if a > b:
            return 1
        elif a < b:
            return -1
    return 0


def parse_require(require):
    # module_name>=0.1.0 -> ("module_name", ">=", "0.1.0")
    ops = [">=", "<=", ">", "<", "="]
    for op in ops:
        if op in require:
            module_name, version = require.split(op)
            return module_name, version, op
    else:
        raise Exception(f"Invalid require: {require}")


def check_versions(v1, v2, op):
    ops = {
        ">=": lambda c: c >= 0,
        "<=": lambda c: c <= 0,
        ">": lambda c: c > 0,
        "<": lambda c: c < 0,
        "=": lambda c: c == 0,
    }
    return ops[op](compare_versions(v1, v2))


def resolve_dependencies(modules: list[DependObject]) -> list[DependObject]:
    # resolved: list[DependObject] = []
    def find_by_name(name):
        for module in modules:
            if module.name == name:
                return module
        else:
            raise Exception(f"Module {name} not found")

    # checking for versions
    for resolving_module in modules:
        for require in resolving_module.requires:
            required_name, r_version, op = parse_require(require)
            required_module = find_by_name(required_name)
            if not check_versions(required_module.version, r_version, op):
                raise Exception(
                    f"Module {required_module.name} version {required_module.version} does not match {require} for module {resolving_module.name}"
                )
    # resolving dependencies
    # need to build a dependency tree
    # then resolve it

    # building a dependency tree
    deptree = {}
    for module in modules:
        deptree[module.name] = []
        for require in module.requires:
            deptree[module.name].append(parse_require(require)[0])
    # resolving the dependency tree
    def resolve(module):
        for dependency in deptree[module]:
            yield from resolve(dependency)
        yield module

    seq = list([module for module in deptree for module in resolve(module)])
    res = []
    for module in seq:
        if module not in res:
            res.append(module)
    # converting the list of module names to a list of DependObjects
    return [find_by_name(module) for module in res]
