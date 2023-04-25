#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
from typing import Dict
from collections import defaultdict
import json

APP_LOAD_PARAMS_ALLOWED = {
    "targetId",
    "targetVersion",
    "apiLevel",
    "fileName",
    "icon",
    "curve",
    "path",
    "path_slip21",
    "appName",
    # "signature", # Reserved for internal usage
    # "signApp", # Reserved for internal usage
    "appFlags",
    # "bootAddr", # Deprecated?
    # "rootPrivateKey", # Should not be used for app deployment
    # "signPrivateKey", # Should not be used for app deployment
    # "apdu", # Should not be used for app deployment
    # "deployLegacy", # Deprecated?
    "delete",
    # "params", # Deprecated?
    "tlv",
    "dataSize",
    "appVersion",
    # "offline", # Should not be used for app deployment
    # "offlineText", # Should not be used for app deployment
    # "installparamsSize", # Deprecated?
    "tlvraw",
    # "dep", # Deprecated?
    "nocrc",
}

APP_LOAD_PARAMS_VALUE_CHECK = {
    "curve",
    "path",
    "path_slip21",
    "appName",
    "appFlags",
}


def parse_listapploadparams(app_load_params_str: str) -> Dict:
    # Convert to dict. Store value in list type as some params can appear
    # multiple times (e.g `--path`).

    app_load_params = defaultdict(list)
    for param in app_load_params_str.split("--"):
        param = param.strip()
        if not param:
            continue

        if param.startswith("targetVersion="):
            parts = param.split("=")
        else:
            parts = param.split(" ")

        param_name = parts[0]

        param_value = None
        if len(parts) > 1:
            param_value = " ".join(parts[1:])

        app_load_params[param_name].append(param_value)

    return dict(app_load_params)


def check_manifest(manifest: dict, database: dict) -> None:
    ret = 0

    for variant, data in manifest["VARIANTS"].items():
        target = data["TARGET"]
        print(f"Checking for target '{target}' and variant '{variant}'")

        app_load_params_str = data["APP_LOAD_PARAMS"]
        app_load_params = parse_listapploadparams(app_load_params_str)
        print("Retrieved listapploadparams:")
        print(json.dumps(app_load_params, indent=4))

        # Check that no unknown or reserved param is used
        for key in app_load_params:
            if key not in APP_LOAD_PARAMS_ALLOWED:
                print(f"[ERROR] Not allowed '{key}' in APP_LOAD_PARAMS")
                ret = -1

        # Retrieve database app_params
        app_params_ref = database.get(variant)
        if not app_params_ref:
            print(f"[ERROR] Missing '{variant}' definition in the database")
            ret = -1
            break

        # Check that the params match with the one from the database
        for key in APP_LOAD_PARAMS_VALUE_CHECK:
            app_params_ref_value = app_params_ref.get(key)
            app_load_params_value = app_load_params.get(key)
            if key == "appName":
                if len(app_load_params_value) != 1:
                    print(f"[ERROR] Expected a single value for 'appName' ({app_load_params_value} vs {app_params_ref_value})")
                    ret = -1
                    continue
                app_load_params_value = app_load_params_value[0]
            elif key == "appFlags":
                if not app_load_params_value:
                    app_load_params_value = ["0x000"]

                if len(app_load_params_value) != 1:
                    print(f"[ERROR] Expected a single value for 'appFlags' ({app_load_params_value} vs {app_params_ref_value})")
                    ret = -1
                    continue

                app_load_params_value = app_load_params_value[0]
                if app_load_params_value.startswith("0x"):
                    app_load_params_value = int(app_load_params_value, 16)
                else:
                    app_load_params_value = int(app_load_params_value)

                app_params_ref_value = app_params_ref_value.get(target)
                if not app_params_ref_value:
                    print(f"[ERROR] Missing 'appFlags' for '{target}'")
                    ret = -1
                    continue
                if app_params_ref_value.startswith("0x"):
                    app_params_ref_value = int(app_params_ref_value, 16)
                else:
                    app_params_ref_value = int(app_params_ref_value)

            if not app_load_params_value == app_params_ref_value:
                print(f"[ERROR] Unexpected value for '{key}' ({app_load_params_value} vs {app_params_ref_value})")
                ret = -1

    return ret


def check_app(app_manifests_path: Path, database_path: Path) -> None:
    ret = 0

    # Retrieve database
    with open(database_path, 'r') as f:
        database = json.load(f)

    manifest_list = [x for x in app_manifests_path.iterdir() if x.name.endswith(".json")]
    for manifest_path in manifest_list:
        # Retrieve manifest
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        print(f"Checking {manifest_path.name}")
        ret |= check_manifest(manifest, database)

    if ret:
        print("Please fix the issues by either:")
        print("- Updating your app Makefile")
        print("- Creating a PR on https://github.com/LedgerHQ/ledger-app-database"
              " to update the app-params-database.json")

    exit(ret)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--app_manifests_path", required=True, type=Path)
    parser.add_argument("--database_path", required=True, type=Path)

    args = parser.parse_args()

    check_app(args.app_manifests_path, args.database_path)
