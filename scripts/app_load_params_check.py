#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
import json


PARAMS_VALUE_CHECK = {
    "curve": list,
    "path": list,
    "path_slip21": str,
    "appName": str,
    "appFlags": str,
}


def check_manifest(manifest: dict, database: dict) -> None:
    ret = 0

    for variant, data in manifest["VARIANTS"].items():
        target = data["TARGET"]
        print(f"Checking for target '{target}' and variant '{variant}'")

        app_params = {key: data[key] for key in PARAMS_VALUE_CHECK.keys() if key in data}
        app_params["appName"] = data["APPNAME"]
        print("Retrieved params:")
        print(json.dumps(app_params, indent=4))

        # Retrieve database app_params
        app_params_ref = database.get(variant)
        if not app_params_ref:
            print(f"[ERROR] Missing '{variant}' definition in the database")
            ret = -1
            break

        # Check that the params match with the one from the database
        for key in PARAMS_VALUE_CHECK.keys():
            app_params_ref_value = app_params_ref.get(key)
            app_params_value = app_params.get(key)
            if key == "appFlags":
                if app_params_value.startswith("0x"):
                    app_params_value = int(app_params_value, 16)
                else:
                    app_params_value = int(app_params_value)

                app_params_ref_value = app_params_ref_value.get(target)
                if not app_params_ref_value:
                    print(f"[ERROR] Missing 'appFlags' for '{target}'")
                    ret = -1
                    continue
                if app_params_ref_value.startswith("0x"):
                    app_params_ref_value = int(app_params_ref_value, 16)
                else:
                    app_params_ref_value = int(app_params_ref_value)

            if not app_params_value == app_params_ref_value:
                print(f"[ERROR] Unexpected value for '{key}' ({app_params_value} vs {app_params_ref_value})")
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
