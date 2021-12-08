#!/usr/bin/python3

import argparse
import enum
import pathlib
from dataclasses import dataclass, field

from typing import Dict, List, Set, Tuple
from enum import Enum

Symbol = str
State = str
SymbolSet = Set[Symbol]
StateSet = Set[State]


STAR_SYMBOL: Symbol = "*"


class Direction(Enum):
    Empty = 0
    Left = 1
    Right = 2


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
                raise Exception(f"Unknown final state: '{state}'.")
        if self.initial not in self.states:
            raise Exception(f"Unknown initial state '{self.initial}'.")
        if self.blank not in self.tapes:
            raise Exception(f"Unknown black symbol '{self.blank}'.")
        for edge in self.trans:
            if edge.old not in self.states:
                raise Exception(
                    f"Unknown old state: '{edge.old}' in transfer edge {edge}.")
            if edge.new not in self.states:
                raise Exception(
                    f"Unknown new state: '{edge.new}' in transfer edge {edge}.")
            if len(edge.oldsyms) != self.n:
                raise Exception(
                    f"Unmatched tape number of old symbols: expect {self.n} but {len(edge.oldsyms)} in transfer edge {edge}.")
            if len(edge.newsyms) != self.n:
                raise Exception(
                    f"Unmatched tape number of new symbols: expect {self.n} but {len(edge.newsyms)} in transfer edge {edge}.")
            for sym in edge.oldsyms:
                if sym != STAR_SYMBOL and sym not in self.tapes:
                    raise Exception(
                        f"Unknown old symbol: '{sym}' in transfer edge {edge}.")
            for sym in edge.newsyms:
                if sym != STAR_SYMBOL and sym not in self.tapes:
                    raise Exception(
                        f"Unknown new symbol: '{sym}' in transfer edge {edge}.")

    def checkInput(self, input: str):
        for sym in input:
            if sym not in self.inputs:
                raise Exception(f"Unknown input symbol '{sym}'.")


@dataclass
class Environment:
    args: Argument = Argument(pathlib.Path("."), "", False)
    machine: TuringMachineDescription = TuringMachineDescription()


env = Environment()


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
            raise Exception("Empty metadata line.")

        if " = " not in line:
            raise Exception("Metadata line in wrong format.")

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
                raise Exception("Wrong format for the number of tapes.")
            result.n = n
        else:
            raise Exception(f"Unknown metadata type '{head}'.")

    def parseEdge(line: str):
        items = [s.strip() for s in line.split(" ") if s.strip()]
        if len(items) != 5:
            raise Exception(f"Wrong format for transfer edge.")
        old, oldsyms, newsyms, dirs, new = items
        rdirs: List[Direction] = []
        for dir in dirs:
            if dir not in DIRECTION_MAPPING:
                raise Exception(f"Unknown direction '{dir}'.")
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
            if env.args.verbose:
                print(f"Failed to parse line {i+1} '{line}'.")
                print(f"  {str(ex)}")
            raise Exception("syntax error")

    try:
        result.check()
    except Exception as ex:
        if env.args.verbose:
            print(f"Failed to check the turing machine.")
            print(f"  {str(ex)}")
        raise Exception("syntax error")

    if env.args.verbose:
        result.view()

    return result


def main():
    try:
        env.args = parseArg()

        text = env.args.file.read_text(encoding="utf-8")
        env.machine = parse(text)
    except Exception as ex:
        print(str(ex))
        exit(1)


if __name__ == "__main__":
    main()
