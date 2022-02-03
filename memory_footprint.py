"""
A simple analysis pass to calculate how much memory
is allocated in the program. We first look into which
function allocates how much memory, then calculate
how much memory it allocates by multiplying the number
of times it is called.
"""

from itertools import count
import sys
import json

size = {'int': 4, 'float': 8}

def find_const(func, target):
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

def count_call(prog):
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
                    call_count[callee] = 0
                call_count[callee] += 1
        call_graph[func['name']] = call_count
    return call_graph

def profile_memory_footprint(prog, call_graph):
    # Find out how much memory each function allocates
    for func in prog['functions']:
        for instr in func['instrs']:
            if 'op' in instr and instr['op'] == 'alloc':
                unit_size = size[instr['type']['ptr']]
                argname = instr['args'][0]
                # We only support alloc with constant argument
                find_const(func, argname)


def main(prog):
    # count = 0
    # for func in prog['functions']:
    #     for instr in func['instrs']:
    #         if 'op' in instr and instr['op'] == "alloc":
    #             print(instr)
    #             print(func['name'])
    #             count += 1
    #         elif 'op' in instr and instr['op'] == "call":
    #             print(instr)
    call_graph = count_call(prog)
    profile_memory_footprint(prog, call_graph)
        

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    main(prog)