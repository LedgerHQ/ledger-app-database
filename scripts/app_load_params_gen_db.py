#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
from app_load_params_utils import load_database, save_database
from makefile_dump import get_app_listvariants, get_app_listparams
from app_load_params_check import PARAMS_VALUE_CHECK


BUILD_PATH_LIST = {
  "app-acala"            : "app"              ,
  "app-algorand"         : "app"              ,
  "app-avalanche"        : "app"              ,
  "app-arweave"          : "app"              ,
  "app-astar"            : "app"              ,
  "app-axelar"           : "app"              ,
  "app-bifrost"          : "app"              ,
  "app-bifrost-kusama"   : "app"              ,
  "app-bifrost-new"      : "app"              ,
  "app-blockstack"       : "app"              ,
  "app-coti"             : "app"              ,
  "app-casper"           : "app"              ,
  "app-centrifuge"       : "app"              ,
  "app-cosmos"           : "app"              ,
  "app-cryptocom"        : "app"              ,
  "app-dgld"             : "app"              ,
  "app-decimal"          : "app"              ,
  "app-desmos"           : "app"              ,
  "app-dock"             : "app"              ,
  "app-edgeware"         : "app"              ,
  "app-equilibrium"      : "app"              ,
  "app-filecoin"         : "app"              ,
  "app-firmachain"       : "app"              ,
  "app-flow"             : "app"              ,
  "app-genshiro"         : "app"              ,
  "app-iov"              : "app"              ,
  "app-internetcomputer" : "app"              ,
  "app-karura"           : "app"              ,
  "app-khala"            : "app"              ,
  "app-kusama"           : "app"              ,
  "app-medibloc"         : "app"              ,
  "app-near"             : "workdir/app-near" ,
  "app-nodle"            : "app"              ,
  "app-oasis"            : "app"              ,
  "app-panacea"          : "app"              ,
  "app-parallel"         : "app"              ,
  "app-persistence"      : "app"              ,
  "app-phala"            : "app"              ,
  "app-polkadex"         : "app"              ,
  "app-polkadot"         : "app"              ,
  "app-polymesh"         : "app"              ,
  "app-reef"             : "app"              ,
  "app-secret"           : "app"              ,
  "app-stacks"           : "app"              ,
  "app-statemine"        : "app"              ,
  "app-statemint"        : "app"              ,
  "app-thorchain"        : "app"              ,
  "app-terra"            : "app"              ,
  "app-xxnetwork"        : "app"              ,
}


def gen_app(app_path: Path, database_path: Path):
    print(f"Generating for {app_path.name}")

    app_build_path = BUILD_PATH_LIST.get(app_path.name, "./")
    app_full_path = app_path / app_build_path

    # Retrieve database
    database = load_database(database_path)

    # Retrieve available variants
    try:
        variant_param_name, variants = get_app_listvariants(app_full_path)
    except:
        print("Skipping generation due to error")
        return

    for variant in variants:
        app_params = get_app_listparams(app_full_path,
                                        variant_param=f"{variant_param_name}={variant}")

        print(app_params)

        database_params = {key: app_params[key] for key in PARAMS_VALUE_CHECK if key in app_params}

        # Drop apps which don't have a path set
        if not database_params.get("path", [None])[0]:
            continue
        database[variant] = database_params

    save_database(database, database_path)


def gen_all_apps(apps_path: Path, database_path: Path):
    app_path_list = [x for x in apps_path.iterdir() if x.is_dir()]
    for app_path in app_path_list:
        gen_app(app_path, database_path)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--app_path", type=Path, default=None)
    parser.add_argument("--apps_path", type=Path, default=None)
    parser.add_argument("--database_path", required=True, type=Path)

    args = parser.parse_args()

    if args.app_path is not None:
        gen_app(args.app_path, args.database_path)
    elif args.apps_path is not None:
        gen_all_apps(args.apps_path, args.database_path)
    else:
        parser.print_help()
