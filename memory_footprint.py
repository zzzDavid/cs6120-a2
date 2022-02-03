"""
A simple analysis pass to calculate how much memory
is allocated in the program. We first look into which
function allocates how much memory, then calculate
how much memory it allocates by multiplying the number
of times it is called.
"""

from itertools import count
from operator import indexOf
import sys
import json

size = {'int': 4, 'float': 8}

def find_const_local(func, target):
    """
    Hunt for const instructions in a function
    and return its value
    We assume SSA.
    """
    for instr in func['instrs']:
        if 'op' in instr and instr['op'] == "const":
            name = instr['dest']
            if name == target:
                return instr['value']
    return None

def find_const_global (prog, call_graph, target, func):
    """
    Find the value of a const in the global scope.
    If `target` const instr is in `func`, then returns teh value.
    If it is passed as function argument, hunt for its value
    in the caller function.
    """
    local_value = find_const_local(func, target)
    if local_value is not None:
        return local_value
    else: # the const is passed from function arg
        # find out which arg it is
        func_args = [arg['name'] for arg in func['args']]
        assert target in func_args
        argidx = func_args.index(target)
        for caller, callees in call_graph.items():
            if func['name'] not in callees:
                continue
            name_in_parent = callees[func['name']]['args'][argidx]
            parent_func = None
            for f in prog['functions']:
                if 'name' in f and f['name'] == caller:
                    parent_func = f
            assert parent_func is not None
            return find_const_local(parent_func, name_in_parent)
    return None

def build_call_graph(prog):
    """
    Global analysis
    Count the number of times functions are called
    """
    call_graph = dict()
    for func in prog['functions']:
        call_count = dict()
        for instr in func['instrs']:
            if 'op' in instr and instr['op'] == "call":
                callee = instr['funcs'][0]
                if callee not in call_count:
                    call_count[callee] = dict()
                    call_count[callee]['count'] = 0
                    call_count[callee]['args'] = instr['args']
                call_count[callee]['count'] += 1
        call_graph[func['name']] = call_count
    return call_graph

def count_call_times(call_graph, entry, target):
    """
    Counts how many times `target` is called
    """
    def DFS(visiting, curr, count=0):
        for callee in call_graph[curr]:
            if callee == target:
                count += call_graph[curr][callee]['count']
        visiting.remove(curr)
        visiting += list(call_graph[curr].keys())
        if len(visiting) == 0:
            return count
        else:
            return DFS(visiting, visiting[0], count)
    count = DFS(['main'], 'main')    
    return count

def profile_memory_footprint(prog, call_graph):
    # Find out how much memory each function allocates
    alloc_dict = dict()
    for func in prog['functions']:
        for instr in func['instrs']:
            if 'op' in instr and instr['op'] == 'alloc':
                unit_size = size[instr['type']['ptr']]
                argname = instr['args'][0]
                # We only support alloc with constant argument
                count = find_const_global(prog, call_graph, argname, func)
                if count is None:
                    raise RuntimeError("Doesn't support alloc with size of type expr...")
                memory_size = unit_size * count
                print(f"Function {func['name']} allocates {memory_size} bytes")
                alloc_dict[func['name']] = memory_size
    # traverse the call graph and count total memory footprint
    memory_footprint = 0
    for func_name, mem_size in alloc_dict.items():
        # find out how many time it is called
        times = 1 if func_name == "main" else count_call_times(call_graph, 'main', func_name)
        print(f"Function {func_name} is called {times} times")
        memory_footprint += times * mem_size
    return memory_footprint

def main(prog):
    call_graph = build_call_graph(prog)
    footprint = profile_memory_footprint(prog, call_graph)
    print(f"memory footprint analysis: {footprint} bytes are allocated in total.")

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    main(prog)