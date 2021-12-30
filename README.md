![Turing Machine Emulator](https://socialify.git.ci/StardustDL/turing-machine-emulator/image?description=1&font=Bitter&forks=1&issues=1&language=1&owner=1&pulls=1&stargazers=1&theme=Light)

![CI](https://github.com/StardustDL/turing-machine-emulator/workflows/CI/badge.svg) ![](https://img.shields.io/github/license/StardustDL/turing-machine-emulator.svg)

An emulator for multi-tape deterministic turing machine.

## Turing Machine Description Language

### Metadata

Each line of metadata is in form `#<name> = <value>` where `<name>` is the metadata id, and `<value>` is the metadata value.

```
; the finite set of states
#Q = {0,cp,cmp,mh,accept,halt_accept,reject,halt_reject}

; the finite set of input symbols
#S = {0,1}

; the complete set of tape symbols
#G = {0,1,_,T,r,u,e,F,a,l,s}

; the start state
#q0 = 0

; the blank symbol
#B = _

; the set of final states
#F = {halt_accept}

; the number of tapes
#N = 2 
```

The metadata can be inferred (replaced) by transfer edges using auto mode in parser.

- Use `0` as start state if not defined.
- Use `_` as blank symbol if not defined.
- Any state starting with 'halt', eg. halt, halt-accept, will be a final state.

### Transfer Edges

- Each line of transfer edge should contain one tuple of the form `<current state> <current symbol> <new symbol> <direction> <new state>`.
- You can use any number or word for `<current state>` and `<new state>`, eg. 10, a, state1. State labels are case-sensitive.
- You can use almost any character for `<current symbol>` and `<new symbol>`, or `_` to represent blank (space). Symbols are case-sensitive.
- You can't use `;`, `*`, `_` or whitespace as symbols.
<direction> should be `l`, `r` or `*`, denoting 'move left', 'move right' or 'do not move', respectively.
- Anything after a `;` is a comment and is ignored.
- `*` can be used as a wildcard in `<current symbol>` or `<current state>` to match any character or state.
- `*` can be used in `<new symbol>` or `<new state>` to mean 'no change'.
- `!` can be used at the end of a line to set a breakpoint, eg. `1 a b r 2 !`.

## Parser

The parser will parse the text in the description language, and check the semantic:

- All states are declared in Q
- All symbols are declared in G
- S is a subset of Q
- q0 is in Q
- B is in G
- F is a subset of Q
- N is a positive integer

## Emulator

It emulates a multi-tape deterministic turing machine.

## Build

```sh
$ cd ./turing-project
$ chmod +x ./build.sh
$ bash -c ./build.sh
```

## Run

```sh
./turing <file to description text> <input string> <flags>
```

Possible flags:

- `-v/--verbose` Details about error in parser and execution states in emulator.
- `-a/--auto` Use the metadata inferred from transfer edges when parsing.
- `-d/--debug` Pause the emulator when a breakpoint hits.

```sh
$ ./turing ./samples/gcd.tm 11110111111
11
$ ./turing ./samples/gcd.tm 11110111111 -v
Input: 11110111111
==================== RUN ====================
Step   : 0
Index0 : 0 1 2 3 4 5 6 7 8 9 10
Tape0  : 1 1 1 1 0 1 1 1 1 1 1 
Head0  : ^                     
Index1 : 0
Tape1  : _
Head1  : ^
Index2 : 0
Tape2  : _
Head2  : ^
State  : 0
---------------------------------------------
Step   : 1
Index0 : 0 1 2 3 4 5 6 7 8 9 10
Tape0  : 1 1 1 1 0 1 1 1 1 1 1 
Head0  : ^                     
Index1 : 0
Tape1  : _
Head1  : ^
Index2 : 0
Tape2  : _
Head2  : ^
State  : pre1
---------------------------------------------
Step   : 2
Index0 : 0 1 2 3 4 5 6 7 8 9 10
Tape0  : 1 1 1 1 0 1 1 1 1 1 1 
Head0  :   ^                   
Index1 : 0 1
Tape1  : 1 _
Head1  :   ^
Index2 : 0
Tape2  : _
Head2  : ^
State  : pre1
---------------------------------------------
...
---------------------------------------------
Step   : 150
Index0 : 0 1 2
Tape0  : 1 1 _
Head0  :     ^
Index1 : 0 1 2 3
Tape1  : 1 1 1 1
Head1  :       ^
Index2 : 0 1 2 3 4 5 6
Tape2  : 1 1 1 1 1 1 _
Head2  :             ^
State  : test2
---------------------------------------------
Step   : 151
Index0 : 0 1
Tape0  : 1 1
Head0  :   ^
Index1 : 0 1 2 3
Tape1  : 1 1 1 1
Head1  :       ^
Index2 : 0 1 2 3 4 5
Tape2  : 1 1 1 1 1 1
Head2  :           ^
State  : final
---------------------------------------------
Result: 11
==================== END ====================
```

## Samples

`/samples` contains some sample turing machines.

> Some of the samples are from [jsturing](https://github.com/awmorp/jsturing). These samples need to use `auto` mode to parse.
