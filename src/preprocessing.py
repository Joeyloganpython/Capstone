import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
from matplotlib import style
import datetime
import seaborn as sns
import numpy as np
from functools import reduce


# There is some datacleanup needed as some counties are in all caps and listed as PA
def fix(df, inplace=True):
    if inplace:
        new_df = df
    else:
        new_df = df.copy()

    new_df["County"] = new_df["County"].apply(lambda x: str.title(x.split(' ')[0].strip()))

    if not inplace:
        return new_df


def yn_switch(op_df, inplace=True):
    if inplace:
        opdfnew = op_df
    else:
        opdfnew = op_df.copy()

    opdfnew["Narcan Admin"] = opdfnew['Naloxone Administered'].map(lambda x: 1 if x == "Y" else 0)
    opdfnew["Survive"] = opdfnew['Survive'].map(lambda x: 1 if x == "Y" else 0)

    if not inplace:
        return opdfnew

def extract_drugs_by_victim(df):
    df_new = df.copy()
    victims = df_new[['Incident ID',
                  'Victim ID',
                  'Victim OD Drug ID',
                  'Susp OD Drug Desc']].groupby(['Incident ID', 'Victim ID'])

    dataframes = []
    for group in victims:
        temp_df = group[1]
        drugs = temp_df['Susp OD Drug Desc'].unique()
        drugs_concat = ''
        for i, drug in enumerate(drugs):
            if i == 0:
                drugs_concat = drugs_concat + drug
            else:
                drugs_concat = drugs_concat + ' | ' + drug
        temp_df['All Drugs'] = drugs_concat
        temp_df = temp_df.drop(['Victim OD Drug ID', 'Susp OD Drug Desc'], axis=1)
        dataframes.append(temp_df)

    other_drugs = pd.concat(dataframes)

    return(pd.merge(df_new, other_drugs))

def incidents_with_naloxone(opioid_list):
    # Loading PA GOV
    df = pd.read_csv('../data/PAGOV.csv')

    keep_columns = ['Incident ID',
                    'Incident Date',
                    'Incident Time',
                    'Day',
                    'Incident County Name',
                    'Incident State',
                    'Victim ID',
                    'Gender Desc',
                    'Age Range',
                    'Race',
                    'Ethnicity Desc',
                    'Victim State',
                    'Victim OD Drug ID',
                    'Susp OD Drug Desc',
                    'Naloxone Administered',
                    'Survive',
                    'Response Desc'
                    ]

    new_df = df[keep_columns]
    new_df = new_df.drop_duplicates()
    new_df.set_index(['Incident ID', 'Victim ID'])

    # This function adds a new column to the dataframe that contains a pipe delimited string listing all
    # drugs found in the victim.
    new_df = extract_drugs_by_victim(new_df)

    # Reduce incidents to ones with specific opioid
    opdf = new_df.loc[new_df['Susp OD Drug Desc'].isin(opioid_list)]

    # Need another step to filter out incidents with multiple drugs
    drop_columns = ['Victim OD Drug ID',
                    'Susp OD Drug Desc'
                    ]
    opdf = opdf.drop(drop_columns, axis=1)
    opdf = opdf.drop_duplicates()

    opdf['Incident Date ym'] = pd.to_datetime(opdf['Incident Date']).dt.to_period('Y')
    opdf['Incident Date ym'] = opdf['Incident Date ym'].astype(str)
    opdf['Incident Date ym'] = opdf['Incident Date ym'].astype(int)

    print(opdf.head())

    # @TODO confirm with Joey whether this oppdf dataframe is needed or unintentional.
    oppdf = opdf.groupby(['Incident Date ym'])[['Incident ID']].count().reset_index()
    opdfnew = yn_switch(opdf, inplace=False)

    # limiting
    opdfnew = opdfnew[['Incident ID',
                       'Incident County Name',
                       'Narcan Admin',
                       'Survive',
                       'Incident Date ym']]

    # Renaming for joins later
    opdfnew = opdfnew.rename(columns={'Incident County Name': 'County',
                                      'Incident Date ym': 'Year'})
    # Getting totals
    opdfnew['Total Overdoses Per County'] = opdfnew.groupby(['County', 'Year'])['County'].transform('count')
    opdfnew['Percent Narcan Admin Per County/Year'] = opdfnew.groupby(['County', 'Year'])['Narcan Admin'].transform(
        'mean')
    opdfnew['Percent Survive Overdose Per County/Year'] = opdfnew.groupby(['County', 'Year'])['Survive'].transform(
        'mean')
    opdfnew['Total Number of PA.gov Overdoses Per County/Year'] = opdfnew.groupby(['County', 'Year'])[
        'Incident ID'].transform('count')

    # Limiting
    opdfnew = opdfnew[['County', 'Year',
                       'Percent Narcan Admin Per County/Year',
                       'Percent Survive Overdose Per County/Year',
                       'Total Number of PA.gov Overdoses Per County/Year']].drop_duplicates()

    print(len(opdfnew))
    print(opdfnew.head())


def main():
    opioid_list = ['CARFENTANIL',
                  'FENTANYL',
                  'FENTANYL ANALOG/OTHER SYNTHETIC OPIOID',
                  'HEROIN', 'METHADONE',
                  'PHARMACEUTICAL OPIOID',
                  'SUBOXONE']

    incidents_with_naloxone(opioid_list)



if __name__ == '__main__':
    main()


    # Loading Takeback dataset
    takebackdf = pd.read_csv('../data/Pulled/Prescription_Drug_Take-Back_Box_Locations_County_Drug_and_Alcohol_Programs.csv')

    # Loading treatment
    treatdf = pd.read_csv('../data/Pulled/Drug_and_Alcohol_Treatment_Facilities_May_2018_County_Drug_and_Alcohol_Programs.csv')

    # Risky Precribing dataset
    risky_df = pd.read_csv(
        '../data/Pulled/Risky_Prescribing_Measures_Quarter_3_2016_-_Current_Quarterly_County___Statewide_Health.csv')

    # Dispensation Dataset
    dispen_df = pd.read_csv(
        '../data/Pulled/Dispensation_Data_without_Buprenorphine_Quarter_3_2016_-_Current_Quarterly_County_Health.csv')

    # Loading Arrests dataset
    arrests_df = pd.read_csv('../data/Pulled/Opioid_Seizures_and_Arrests_CY_2013_-_Current_Quarterly_County_State_Police.csv')

    # Loading County Population dataset
    population_df = pd.read_csv('../data/Pulled/County_pop.csv')
