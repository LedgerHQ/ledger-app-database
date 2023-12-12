# Ledger app database repository

This project contains databases and associated scripts related to Ledger apps.

## app-load-params-db.json

This database list the different APP_LOAD_PARAMS for each app variants.
It associate to an app variant:
- the appFlags
- the appName
- the curve
- the path

### Usage in an app

This database is used to check apps for misuse of APP_LOAD_PARAMS or conflicts on APPNAME or VARIANT.
It is part of the App compliance workflow which is mandatory for all apps.
Please see an example on how to use the reusable workflows in the `app-boilerplate` repository.
We will always keep the `app-boilerplate` repository complete and up-to-date in terms of workflows.
https://github.com/LedgerHQ/app-boilerplate

### How to add support for your application

If your application is not already in the database or if you want to update its content (for example to request for another derivation path), please create a Pr with the requested changes. You can use this [script](https://github.com/LedgerHQ/ledger-app-database/blob/main/scripts/app_load_params_gen_db.py) with `--app_path` parameter to easily update the ledger app database with your own app data.
