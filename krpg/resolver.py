
def resolve_dependencies(modules: dict[str, list[str]]) -> list[str]:
    # FIXed: this returns a list of lists, not a list of strings
    # def resolve(module):
    #     for dependency in modules[module]:
    #         yield from resolve(dependency)
    #     yield module
    # 
    # return list(set([resolve(module) for module in modules]))
    def resolve(module):
        for dependency in modules[module]:
            yield from resolve(dependency)
        yield module
    seq = list([module for module in modules for module in resolve(module)])
    res = []
    for module in seq:
        if module not in res:
            res.append(module)
    return res
