# CS6120 Assignment 2: Simple Pass with Bril

## Description
`memory_footprint.py` implements a single pass that calculate how much memory is allocated in a program. 

## Run

Test with `turnt`: 
```
$ turnt test/*.bril
```

Run the Python script:
```
$ bril2json < test/*.bril | python memory_footprint.py
```