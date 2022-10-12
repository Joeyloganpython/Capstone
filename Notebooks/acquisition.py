# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 19:41:03 2022

@author: silas
"""

import pandas as pd
from sodapy import Socrata
import os

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:

def get_data(client, dataset_key):
    id = dataset_key
    metadata = client.get_metadata(id)
    name = metadata['name'].replace(" ", "_")
    print(name)
    path = f"..\\data\\{name}.csv"
    # path = f"..\\data\\{name}.csv"
    if not os.path.isfile(path):
        results = client.get_all(id)
        # results = client.get(id)
        # Convert to pandas DataFrame
        results_df = pd.DataFrame.from_records(results)
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
        get_data(client, dataset_key)

def main():
    app_token = os.getenv('SOCRATA_APP_TOKEN')
    cdc(app_token)
    pa(app_token)


if __name__ == "__main__":
    main()



    # First 2000 results, returned as JSON from API / converted to Python list of
    # dictionaries by sodapy.
    # for key in list(pa_datasets.keys()):
    #     id = pa_datasets[key]
    #     metadata = client.get_metadata(id)
    #     name = metadata['name'].replace(" ", "_")
    #     path = f"..\\data\\from_api\\{name}.csv"
    #     # path = f"..\\data\\{name}.csv"
    #     if not os.path.isfile(path):
    #         results = client.get_all(id)
    #         # results = client.get(id)
    #         # Convert to pandas DataFrame
    #         results_df = pd.DataFrame.from_records(results)
    #         results_df.to_csv(path)

    # for key in pa_datasets.keys():
    #     id = pa_datasets[key]
    #     metadata = client.get_metadata(id)
    #     name = metadata['name'].replace(" ", "_")
    #     path = f"..\\data\\from_api\\{name}.csv"
    #     # path = f"..\\data\\{name}.csv"
    #     df = pd.read_csv(path)
    #     print(len(df))

    # dataset_keys = {'drugbusts': 'wmgc-6qvd', 'naloxone': 'wst4-3int', 'riskyprescribing': '7m4f-4k58',
    #                'drugtakeback': 'vjk8-em4w', 'overdoseinfonet': 'hbkk-dwy3', 'dispensation': 'rr54-ur6z',
    #                'unemployment': 'rqq6-7e5m', 'treatmentfacilities': 'eswt-bam9', 'druguseestimates': 'krjw-t48p'}