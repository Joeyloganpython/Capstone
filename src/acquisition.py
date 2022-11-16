# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 19:41:03 2022

@author: silas
"""

import pandas as pd
from sodapy import Socrata
import os
import sys


# Define directories separation character based on OS
# Values were found in https://stackoverflow.com/a/13874620
# Darwin - MacOS
if sys.platform in ['darwin', 'linux']: 
    dir_sep = '/'

# Windows, Windows/cygwin, Windows/MSYS2
elif sys.platform in ['win32', 'msys', 'cygwin']: 
    dir_sep = '\\'

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:


def get_data(client, dataset_key, overwrite=False):
    id = dataset_key
    metadata = client.get_metadata(id)
    name = metadata['name'].replace(" ", "_")
    print(name)

    path = f"..{dir_sep}data{dir_sep}Pulled{dir_sep}{name}.csv"
    if not os.path.isfile(path) or overwrite:
        results = client.get_all(id)

        # Convert to pandas DataFrame
        results_df = pd.DataFrame.from_records(results)

        field_mapper = dict()
        for column in metadata['columns']:
            field_mapper[column['fieldName']] = column['name']

        results_df.rename(columns=field_mapper, inplace=True)

        results_df.to_csv(path)

def cdc(app_token):
    client = Socrata("data.cdc.gov", app_token)
    dataset_keys = ['gb4e-yj24']
    for dataset_key in dataset_keys:
        get_data(client, dataset_key)


def pa(app_token):
    client = Socrata("data.pa.gov", app_token)
    dataset_keys = {'wmgc-6qvd', 'wst4-3int', '7m4f-4k58', 'vjk8-em4w', 'hbkk-dwy3', 'rr54-ur6z',
                    'rqq6-7e5m', 'eswt-bam9', 'krjw-t48p'}
    for dataset_key in dataset_keys:
        get_data(client, dataset_key, overwrite=True)

def main():
    app_token = os.getenv('SOCRATA_APP_TOKEN')
    cdc(app_token)
    pa(app_token)


if __name__ == "__main__":
    main()
