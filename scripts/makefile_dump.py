#!/usr/bin/env python3

"""
This is a pure duplicate of
https://github.com/LedgerHQ/ledger-app-workflows/blob/master/scripts/makefile_dump.py
This is to allow easily generating the db from the apps code.
"""

import subprocess
from argparse import ArgumentParser
from pathlib import Path
from typing import Tuple, List, Dict
from tempfile import NamedTemporaryFile
import json


LISTPARAMS_MAKEFILE = """
listparams:
\t@echo Start dumping params
\t@echo APP_LOAD_PARAMS=$(APP_LOAD_PARAMS)
\t@echo GLYPH_FILES=$(GLYPH_FILES)
\t@echo ICONNAME=$(ICONNAME)
\t@echo TARGET=$(TARGET)
\t@echo TARGET_NAME=$(TARGET_NAME)
\t@echo TARGET_ID=$(TARGET_ID)
\t@echo APPNAME=$(APPNAME)
\t@echo APPVERSION=$(APPVERSION)
\t@echo API_LEVEL=$(API_LEVEL)
\t@echo SDK_NAME=$(SDK_NAME)
\t@echo SDK_VERSION=$(SDK_VERSION)
\t@echo SDK_HASH=$(SDK_HASH)
\t@echo Stop dumping params
"""


def run_cmd(cmd: str,
            cwd: Path,
            print_output: bool = False,
            no_throw: bool = False) -> str:
    print(f"[run_cmd] Running: {cmd} from {cwd}")

    ret = subprocess.run(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         universal_newlines=True,
                         cwd=cwd)
    if no_throw is False and ret.returncode:
        print(f"[run_cmd] Error {ret.returncode} raised while running cmd: {cmd}")
        print("[run_cmd] Output was:")
        print(ret.stdout)
        raise ValueError()

    if print_output:
        print(f"[run_cmd] Output:\n{ret.stdout}")

    return ret.stdout.strip()


def get_app_listvariants(app_build_path: Path) -> Tuple[str, List[str]]:
    # Using listvariants Makefile target
    listvariants = run_cmd("make listvariants", cwd=app_build_path)
    if "VARIANTS" not in listvariants:
        raise ValueError(f"Invalid variants retrieved: {listvariants}")

    # Drop Makefile logs previous to listvariants output
    listvariants = listvariants.split("VARIANTS ")[1]
    listvariants = listvariants.split("\n")[0]

    variants = listvariants.split(" ")
    variant_param_name = variants.pop(0)
    assert variants, "At least one variant should be defined in the app Makefile"
    return variant_param_name, variants


def get_app_listparams(app_build_path: Path,
                       variant_param: str) -> Dict:
    with NamedTemporaryFile(suffix='.mk') as tmp:
        tmp_file = Path(tmp.name)

        with open(tmp_file, "w") as f:
            f.write(LISTPARAMS_MAKEFILE)

        ret = run_cmd(f"make -f Makefile -f {tmp_file} listparams {variant_param}",
                      cwd=app_build_path)

    ret = ret.split("Start dumping params\n")[1]
    ret = ret.split("\nStop dumping params")[0]

    listparams = {}
    for line in ret.split("\n"):
        if "=" not in line:
            continue

        if "APP_LOAD_PARAMS=" in line:
            app_load_params_str = line.replace("APP_LOAD_PARAMS=", "")
            listparams["APP_LOAD_PARAMS"] = app_load_params_str
        else:
            key, value = line.split("=")
            listparams[key] = value

    return listparams


def save_app_params(app_build_path: Path, json_path: Path) -> None:

    # Retrieve available variants
    variant_param_name, variants = get_app_listvariants(app_build_path)

    ret = {
        "VARIANT_PARAM": variant_param_name,
        "VARIANTS": {}
    }

    for variant in variants:
        print(f"Checking for variant: {variant}")

        app_params = get_app_listparams(app_build_path,
                                        variant_param=f"{variant_param_name}={variant}")

        ret["VARIANTS"][variant] = app_params

    with open(json_path, "w") as f:
        json.dump(ret, f, indent=4)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--app_build_path",
                        help="App build path, e.g. <app-boilerplate/app>",
                        required=True)
    parser.add_argument("--json_path",
                        help="Json path to store the output",
                        required=True)

    args = parser.parse_args()

    save_app_params(args.app_build_path, args.json_path)
