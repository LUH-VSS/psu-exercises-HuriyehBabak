#!/bin/env python3
import subprocess
import os
import sys
from shutil import which
from pathlib import Path

if which("sml") is None:
    print("ERROR: sml not found in path")
    print("Please install smlnj from https://www.smlnj.org/ or your package manager")
    sys.exit(1)

TESTS_PATH = Path("./tests/")
os.chdir(TESTS_PATH)

EXERCISE_PATH = Path("../exercise/")

ENV = os.environ
ENV["CM_VERBOSE"] = "false"

tests = [
    ["factorial", "test1"],
    ["prepend", "test2"],
    ["last", "test3"],
    ["concat", "test4"],
    ["traverse", "test5"],
]

passed = 0

arguments = sys.argv[1:]
if len(arguments) > 0:
    tests = [test for test in tests if test[0] in arguments]

for e, t in tests:
    print(f"{t}: {e}", end="")

    exercise_file = EXERCISE_PATH / (e + ".sml")
    test_file = t + ".sml"

    command = f"sml {exercise_file} {test_file}"
    result = subprocess.run(
        command, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )

    if not result.returncode and b"TESTS PASSED" in result.stdout:
        print(" - PASSED")
        passed += 1
        continue

    print("")
    print(result.stdout.decode())
    print("*******")
    print(f"{e} FAILED")
    print("*******")


print(f"{passed}/{len(tests)} tests passed!")
sys.exit(0 if passed == len(tests) else 1)
