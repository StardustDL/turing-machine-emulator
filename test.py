import subprocess
import functools
import random
import math


def test(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"{'-'*20}> Test Start: {func.__name__} <{'-'*20}")
        func(*args, **kwargs)
        print(f"{'-'*20}> Test End: {func.__name__} <{'-'*20}")
    return wrapper


def run(src: str, input: str = "", verbose: bool = False, auto: bool = False):
    args = ["python", "./turing.py", src, input]
    if verbose:
        args.append("-v")
    if auto:
        args.append("-a")
    result = subprocess.run(args, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, encoding="utf-8")
    return result


@test
def bug():
    r: subprocess.CompletedProcess[str] = run("./samples/bug.tm")
    assert r.returncode != 0
    assert r.stdout == ""
    assert r.stderr.strip() == "syntax error"

    r: subprocess.CompletedProcess[str] = run(
        "./samples/palindrome_detector_2tapes.tm", "1012")
    assert r.returncode != 0
    assert r.stdout == ""
    assert r.stderr.strip() == "illegal input"

    r: subprocess.CompletedProcess[str] = run(
        "./samples/palindrome_detector_2tapes.tm", "1012", verbose=True)
    assert r.returncode != 0
    assert r.stdout == ""
    print(r.stderr, end="")


@test
def palindrome(file="./samples/palindrome_detector_2tapes.tm"):
    print(f"Machine: {file}")
    r: subprocess.CompletedProcess[str] = run(
        file, "101")
    r.check_returncode()
    assert r.stdout.strip() == "True"
    assert r.stderr == ""

    r: subprocess.CompletedProcess[str] = run(
        file, "1011")
    r.check_returncode()
    assert r.stdout.strip() == "False"
    assert r.stderr == ""

    for i in range(10):
        s = bin(random.randint(0, 1000))[2:]
        print(f"Case {i+1}: {s}")
        r: subprocess.CompletedProcess[str] = run(
            file, s)
        r.check_returncode()
        if s == s[::-1]:
            assert r.stdout.strip() == "True"
        else:
            assert r.stdout.strip() == "False"
        r: subprocess.CompletedProcess[str] = run(
            file, s + s[::-1])
        r.check_returncode()
        assert r.stdout.strip() == "True"


def cmp_gcd(a, b, file="./samples/gcd.tm", auto=True):
    inp = '1'*a+'0'+'1'*b
    r: subprocess.CompletedProcess[str] = run(file, inp, auto=auto)
    r.check_returncode()
    result = r.stdout.strip()
    assert all(c == '1' for c in result)
    assert len(result) == math.gcd(a, b)


@test
def gcd(file="./samples/gcd.tm", auto=True, top=100):
    print(f"Machine: {file}")
    r: subprocess.CompletedProcess[str] = run(file, "101", auto=auto)
    r.check_returncode()
    assert r.stdout.strip() == "1"
    assert r.stderr == ""

    r: subprocess.CompletedProcess[str] = run(
        file, "11110111111", auto=auto)
    r.check_returncode()
    assert r.stdout.strip() == "11"
    assert r.stderr == ""

    for i in range(10):
        s = random.randint(1, top)
        t = random.randint(1, top)
        print(f"Case {i+1}: gcd({s}, {t})")
        cmp_gcd(s, t, file, auto)


@test
def gcd_all(file="./samples/gcd.tm", auto=True, top=50):
    print(f"Machine: {file}")
    for i in range(1, top+1):
        for j in range(1, top+1):
            print(f"Case: gcd({i}, {j})")
            try:
                cmp_gcd(i, j, file, auto)
            except:
                print(f"Case Failed: gcd({i}, {j})")
                raise


if __name__ == "__main__":
    bug()
    palindrome()
    gcd_all("./samples/gcd2.tm", auto=False, top=10)
    gcd()
    gcd("./samples/gcd2.tm", auto=False)
    gcd("./samples/gcd2-sim.tm")
