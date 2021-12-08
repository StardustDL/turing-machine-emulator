#!/usr/bin/python3

import argparse
import enum
import pathlib
from dataclasses import dataclass, field
from functools import cmp_to_key

from typing import Dict, List, Optional, Set, Tuple
from enum import Enum

DEBUG = False

Symbol = str
State = str
SymbolSet = Set[Symbol]
StateSet = Set[State]


STAR_SYMBOL: Symbol = "*"


class Direction(Enum):
    Empty = 0
    Left = 1
    Right = 2


class TMStatus(Enum):
    Created = 0
    Booted = 1
    Start = 2
    Running = 3
    Halt = 4
    Accepted = 5
    Error = 6


class ParserException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class RunnerException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


@dataclass
class Argument:
    file: pathlib.Path
    input: str
    verbose: bool


@dataclass
class TransferEdge:
    old: State
    oldsyms: List[Symbol]
    new: State
    newsyms: List[Symbol]
    dirs: List[Direction]

    def __str__(self) -> str:
        return f"({self.old}, {''.join(self.oldsyms)}) -> ({self.new}, {''.join(self.newsyms)}, {''.join((d.name[0] for d in self.dirs))})"


@dataclass
class TuringMachineDescription:
    states: StateSet = field(default_factory=set)
    initial: State = "0"
    finals: StateSet = field(default_factory=set)
    inputs: SymbolSet = field(default_factory=set)
    tapes: SymbolSet = field(default_factory=set)
    blank: Symbol = "_"
    n: int = 1
    trans: List[TransferEdge] = field(default_factory=list)

    def _ensureLegalSymbol(self, s: Symbol):
        if s.isprintable() and any((c not in s for c in [' ', ',', ';', '{', '}', '*', '_'])):
            pass
        else:
            raise Exception(f"Illegal symbol: '{s}'.")

    def _ensureLegalState(self, s: State):
        if all(c.isalnum() or c == "_" for c in s):
            pass
        else:
            raise Exception(f"Illegal state: '{s}'.")

    def addState(self, s: State):
        self._ensureLegalState(s)
        self.states.add(s)

    def addInputSymbol(self, s: Symbol):
        self._ensureLegalSymbol(s)
        self.inputs.add(s)

    def addTapeSymbol(self, s: Symbol):
        self._ensureLegalSymbol(s)
        self.tapes.add(s)

    def addFinalState(self, s: Symbol):
        self._ensureLegalState(s)
        self.finals.add(s)

    def addTransferEdge(self, edge: TransferEdge):
        self.trans.append(edge)

    def view(self):
        print(f"States: {', '.join(self.states)}")
        print(f"Initial State: {self.initial}")
        print(f"Final States: {', '.join(self.finals)}")
        print(f"Input Symbols: {', '.join(self.inputs)}")
        print(f"Tape Symbols: {', '.join(self.tapes)}")
        print(f"Blank Symbol: {self.blank}")
        print(f"Tape Number: {self.n}")
        print(f"Transfer Edges ({len(self.trans)}):")
        for edge in self.trans:
            print(f"  {edge}")

    def check(self):
        for state in self.finals:
            if state not in self.states:
                raise ParserException(f"Unknown final state: '{state}'.")
        if self.initial not in self.states:
            raise ParserException(f"Unknown initial state '{self.initial}'.")
        if self.blank not in self.tapes:
            raise ParserException(f"Unknown black symbol '{self.blank}'.")
        for sym in self.inputs:
            if sym not in self.tapes:
                raise ParserException(
                    f"Input symbol '{self.blank}' is not a tape symbol.")
        for edge in self.trans:
            if edge.old not in self.states:
                raise ParserException(
                    f"Unknown old state: '{edge.old}' in transfer edge {edge}.")
            if edge.new not in self.states:
                raise ParserException(
                    f"Unknown new state: '{edge.new}' in transfer edge {edge}.")
            if len(edge.oldsyms) != self.n:
                raise ParserException(
                    f"Unmatched tape number of old symbols: expect {self.n} but {len(edge.oldsyms)} in transfer edge {edge}.")
            if len(edge.newsyms) != self.n:
                raise ParserException(
                    f"Unmatched tape number of new symbols: expect {self.n} but {len(edge.newsyms)} in transfer edge {edge}.")
            for sym in edge.oldsyms:
                if sym != STAR_SYMBOL and sym not in self.tapes:
                    raise ParserException(
                        f"Unknown old symbol: '{sym}' in transfer edge {edge}.")
            for sym in edge.newsyms:
                if sym != STAR_SYMBOL and sym not in self.tapes:
                    raise ParserException(
                        f"Unknown new symbol: '{sym}' in transfer edge {edge}.")


class Tape:
    def __init__(self, blank: Symbol) -> None:
        self.blank: Symbol = blank
        self.r: List[Symbol] = [self.blank]
        self.l: List[Symbol] = []
        self.pos: int = 0

    def data(self):
        result: List[Symbol] = []
        index: List[int] = []

        sl = 0
        for i in range(len(self.l)-1, -1, -1):
            if self.l[i] != self.blank:
                sl = -(i+1)
                break
        sl = min(sl, self.pos)
        result.extend(self.l[0:-sl])
        index.extend(range(sl, 0))

        sr = -1
        for i in range(len(self.r)-1, -1, -1):
            if self.r[i] != self.blank:
                sr = i
                break
        sr = max(sr, self.pos)
        result.extend(self.r[0:sr+1])
        index.extend(range(sr+1))

        l, r = None, None
        for i in range(len(result)):
            if result[i] != self.blank:
                l = i
                break

        if l is None:
            return [self.blank], [self.pos]

        for i in range(len(result)-1, -1, -1):
            if result[i] != self.blank:
                r = i
                break

        ppos = index.index(self.pos)
        l = min(l, ppos)
        r = max(r, ppos)

        return result[l:r+1], index[l:r+1]

    def __str__(self) -> str:
        data, _ = self.data()
        return "".join(data)

    def view(self):
        result, index = self.data()

        assert len(result) == len(index) and len(result) > 0

        strTape = ""
        strIndex = ""
        strHead = ""

        if len(result) == 0:
            return

        for i, sym in enumerate(result):
            ind = index[i]
            sind = str(abs(ind))
            le = len(sind)
            strTape += f" {sym.ljust(le)}"
            strIndex += f" {sind}"
            if ind == self.pos:
                strHead += f" {'^'.ljust(le)}"
            else:
                strHead += f" {' '.ljust(le)}"

        return strIndex[1:], strTape[1:], strHead[1:]

    def left(self):
        self.pos -= 1
        if self.pos < 0:
            tp = abs(self.pos) - 1
            assert tp <= len(self.l)
            if tp == len(self.l):
                self.l.append(self.blank)

    def right(self):
        self.pos += 1
        tp = self.pos
        assert tp <= len(self.r)
        if tp == len(self.r):
            self.r.append(self.blank)

    def write(self, s: Symbol):
        if self.pos < 0:
            tp = abs(self.pos) - 1
            self.l[tp] = s
        else:
            self.r[self.pos] = s

    def read(self):
        if self.pos < 0:
            tp = abs(self.pos) - 1
            return self.l[tp]
        else:
            return self.r[self.pos]


@dataclass
class Environment:
    args: Argument = Argument(pathlib.Path("."), "", False)
    machine: TuringMachineDescription = TuringMachineDescription()


env = Environment()


class TuringMachine:
    def __init__(self, description: TuringMachineDescription) -> None:
        self.description = description
        self.status = TMStatus.Created

    def boot(self):
        self.tapes = [Tape(self.description.blank)
                      for _ in range(self.description.n)]
        self.current = self.description.initial
        self.status = TMStatus.Booted

    def __enter__(self):
        self.boot()
        return self

    def __exit__(self, type, value, trace):
        self.shutdown()

    def start(self, input: str):
        if env.args.verbose:
            print(f"Input: {input}")
        errIndex = None
        for i, sym in enumerate(input):
            if sym not in self.description.inputs:
                errIndex = i
                break
        if errIndex is not None:
            self.status = TMStatus.Error
            message = f"'{input[errIndex]}' was not declared in the set of input symbols"
            if env.args.verbose:
                print("==================== ERR ====================")
                print(f"error: {message}")
                print(f"Input: {input}")
                print(f"       {' '*errIndex}^")
            raise RunnerException(message)

        self.tapes[0].r = list(input)
        self.tapes[0].pos = 0
        self.stepcnt = 0

    def view(self):
        l = len(f"Index{len(self.tapes)}")
        print("Step".ljust(l), ":", str(self.stepcnt))
        for i, tape in enumerate(self.tapes):
            index, tp, head = tape.view()
            print(f"Index{i}".ljust(l), ":", index)
            print(f"Tape{i}".ljust(l), ":", tp)
            print(f"Head{i}".ljust(l), ":", head)
        print("State".ljust(l), ":", str(self.current))
        print("---------------------------------------------")

    def run(self):
        self.status = TMStatus.Running
        if env.args.verbose:
            print("==================== RUN ====================")
            self.view()
        while self.status == TMStatus.Running:
            if self.current in self.description.finals:
                self.status = TMStatus.Accepted
            elif not self.step():
                self.status = TMStatus.Halt

    def step(self) -> bool:
        matched = []
        transcnt = len(self.description.trans)
        for ei, edge in enumerate(self.description.trans):
            if edge.old != self.current:
                continue
            ismatch = True
            score = 0
            for i in range(self.description.n):
                v = self.tapes[i].read()
                if edge.oldsyms[i] != STAR_SYMBOL and edge.oldsyms[i] != v:
                    ismatch = False
                    break
                score += 1 if edge.oldsyms[i] == v else 0
            if ismatch:
                matched.append((edge, score, ei))
        matched.sort(key=lambda x: -(x[1] * transcnt + x[2]))
        if matched:
            edge = matched[0][0]
            for i in range(self.description.n):
                s, d = edge.newsyms[i], edge.dirs[i]
                if s != STAR_SYMBOL:
                    self.tapes[i].write(s)
                if d == Direction.Left:
                    self.tapes[i].left()
                elif d == Direction.Right:
                    self.tapes[i].right()
            self.current = edge.new
        else:
            return False
        self.stepcnt += 1
        if env.args.verbose:
            self.view()
        if DEBUG:
            # input()
            pass
        return True

    def shutdown(self):
        if env.args.verbose:
            if self.status != TMStatus.Error:
                print(f"Result: {str(self.tapes[0])}")
            print("==================== END ====================")
        else:
            if self.status != TMStatus.Error:
                print(str(self.tapes[0]))
        self.status = TMStatus.Created


def parseArg() -> Argument:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Turing machine description file.")
    parser.add_argument("input", help="Input string.")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity",
                        action="store_true")
    args = parser.parse_args()

    file = pathlib.Path(args.file)
    if not file.exists() or not file.is_file():
        raise Exception(f"File '{file}' does not exist.")

    return Argument(file, args.input, args.verbose)


def parse(text: str) -> TuringMachineDescription:
    result = TuringMachineDescription()

    DIRECTION_MAPPING = {
        "l": Direction.Left,
        "r": Direction.Right,
        "*": Direction.Empty,
    }

    def strip(line: str) -> str:
        try:
            ind = line.index(";")
            line = line[:ind]
        except ValueError:
            pass
        return line.strip()

    def parseMetadata(line: str):
        assert line.startswith("#")
        line = line[1:]

        if len(line) == 0:
            raise ParserException("Empty metadata line.")

        if " = " not in line:
            raise ParserException("Metadata line in wrong format.")

        head, tail = [i.strip() for i in line.split(" = ")]

        line = line[3:]

        if head == "Q":
            items = [l.strip()
                     for l in tail.lstrip("{").rstrip("}").split(",")]
            for item in items:
                result.addState(item)
        elif head == "S":
            items = [l.strip()
                     for l in tail.lstrip("{").rstrip("}").split(",")]
            for item in items:
                result.addInputSymbol(item)
        elif head == "G":
            items = [l.strip()
                     for l in tail.lstrip("{").rstrip("}").split(",")]
            for item in items:
                result.addTapeSymbol(item)
        elif head == "F":
            items = [l.strip()
                     for l in tail.lstrip("{").rstrip("}").split(",")]
            for item in items:
                result.addFinalState(item)
        elif head == "q0":
            result.initial = tail.strip()
        elif head == "B":
            result.blank = tail.strip()
        elif head == "N":
            try:
                n = int(tail.strip())
                assert n >= 1
            except:
                raise ParserException("Wrong format for the number of tapes.")
            result.n = n
        else:
            raise ParserException(f"Unknown metadata type '{head}'.")

    def parseEdge(line: str):
        items = [s.strip() for s in line.split(" ") if s.strip()]
        if len(items) != 5:
            raise ParserException(f"Wrong format for transfer edge.")
        old, oldsyms, newsyms, dirs, new = items
        rdirs: List[Direction] = []
        for dir in dirs:
            if dir not in DIRECTION_MAPPING:
                raise ParserException(f"Unknown direction '{dir}'.")
            rdirs.append(DIRECTION_MAPPING[dir])
        result.addTransferEdge(TransferEdge(
            old, list(oldsyms), new, list(newsyms), rdirs))

    lines = [strip(line) for line in text.splitlines()]
    lines = [line for line in lines if line]

    for i, line in enumerate(lines):
        try:
            if line.startswith("#"):
                parseMetadata(line)
            else:
                parseEdge(line)
        except Exception as ex:
            message = f"Failed to parse line {i+1} '{line}'."
            if env.args.verbose:
                print(message)
                print(f"  {str(ex)}")
            if isinstance(ex, ParserException):
                raise
            raise ParserException(message)

    try:
        result.check()
    except Exception as ex:
        message = f"Failed to check the turing machine."
        if env.args.verbose:
            print(message)
            print(f"  {str(ex)}")
        if isinstance(ex, ParserException):
            raise
        raise ParserException(message)

    # if env.args.verbose:
    #     result.view()

    return result


def run():
    with TuringMachine(env.machine) as machine:
        machine.start(env.args.input)
        machine.run()


def main():
    try:
        env.args = parseArg()

        text = env.args.file.read_text(encoding="utf-8")
        env.machine = parse(text)

        run()
    except ParserException as ex:
        if env.args.verbose:
            print(f"Parser Error: {str(ex)}")
        else:
            print("syntax error")
        exit(1)
    except RunnerException as ex:
        if env.args.verbose:
            # print(f"Runner Error: {str(ex)}")
            pass
        else:
            print("illegal input")
        exit(1)
    except Exception as ex:
        if DEBUG:
            raise
        else:
            print(str(ex))
            exit(1)


if __name__ == "__main__":
    main()
