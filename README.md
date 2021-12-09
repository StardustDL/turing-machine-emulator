# Turing Machine Emulator

- Author: StardustDL
- [Source Code](https://github.com/StardustDL/turing-machine-emulator)

## Build

```sh
$ cd ./turing-project
$ bash -c ./build.sh
```

## Run

```sh
$ ./turing ../programs/gcd.tm 11110111111
11
$ ./turing ../programs/gcd.tm 11110111111 -v
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
