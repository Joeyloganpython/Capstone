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
    df = pd.read_csv('../data/Pulled/Emergency_Medical_Services_(EMS)_Naloxone_Dose_Administered_CY_2018_-_Current_Quarterly_County_Health.csv')

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

    return (opdfnew)


def takeback():
    # Loading Takeback dataset
    takebackdf = pd.read_csv('../data/Pulled/Prescription_Drug_Take-Back_Box_Locations_County_Drug_and_Alcohol_Programs.csv')

    # Fixing County name
    takebackdf = fix(takebackdf, False)

    # Count takeback locations for each county
    takebackdf = takebackdf.groupby('County').count()['Drug Take-Back Site'].reset_index()
    takebackdf.rename(columns={'Drug Take-Back Site':'Total Take Back Locations'})
    return takebackdf


def treatment():

    # Loading treatment
    treatment_locations = pd.read_csv('../data/Pulled/Drug_and_Alcohol_Treatment_Facilities_May_2018_County_Drug_and_Alcohol_Programs.csv')
    treatment_loc_counts = treatment_locations.groupby('County').count()['Name of Facility'].reset_index()
    treatment_loc_counts.rename(columns = {'Name of Facility': 'Total Treatment Locations'}, inplace=True)
    return treatment_loc_counts


def risky_prescribing():
    # Risky Precribing dataset
    risky_df = pd.read_csv(
        '../data/Pulled/Risky_Prescribing_Measures_Quarter_3_2016_-_Current_Quarterly_County_&_Statewide_Health.csv')

    # Dropping any duplicates from initial dataset
    risky_df.drop('Unnamed: 0', axis=1, inplace=True)
    risky_df.drop_duplicates(inplace=True)

    # Removing PA as to not count twice
    risky_df = risky_df[risky_df['County'] != 'Pennsylvania']

    keep_columns = ['County', 'Year', 'Risky Measure Type', 'Rate or Count']
    risky_df = risky_df[keep_columns]

    # exclude 'rates' and counts that could result in duplicates
    keep_rate_or_count = ['Number of Individuals Seeing 3+ Prescribers and 3+ Dispensers',
                          'Number of Individuals with Average Daily MME > 50',
                          'Number of Individuals with Overlapping Opioid/Benzodiazepine Prescriptions']

    risky_df = risky_df[risky_df['Risky Measure Type'].isin(keep_rate_or_count)].dropna()

    # Summing per county/year
    risky_df = risky_df.groupby(['County', 'Year', 'Risky Measure Type']).sum().reset_index()
    risky_df.rename(columns={'Rate or Count': 'Total Risky Prescriptions'}, inplace=True)

    risky_df = risky_df.pivot(index=['County', 'Year'],
                              columns='Risky Measure Type',
                              values='Total Risky Prescriptions').reset_index()
    return risky_df


def dispensation():
    # Dispensation Dataset
    dispen_df = pd.read_csv(
        '../data/Pulled/Dispensation_Data_without_Buprenorphine_Quarter_3_2016_-_Current_Quarterly_County_Health.csv')

    # removing the index column and removing any duplicates in the initial dataset
    dispen_df.drop('Unnamed: 0', axis=1, inplace=True)
    dispen_df.drop_duplicates(inplace=True)

    # Measures will be for all ages and all genders
    dispen_df = dispen_df[dispen_df['Age Group'] == 'All Ages']
    dispen_df = dispen_df[dispen_df['Gender'] == 'All Genders']
    dispen_df = dispen_df.rename(columns={'County Name': 'County'})

    keep_columns = ['County', 'Year', 'Type of Rate or Count Measure', 'Rate or Count']

    dispen_df = dispen_df[keep_columns]

    keep_rate_or_count = ['Number of Dispensations (by pharmacy location)',
                          'Number of Prescriptions (by patient location)']

    dispen_df = dispen_df[dispen_df['Type of Rate or Count Measure'].isin(keep_rate_or_count)].dropna()

    dispen_df = dispen_df.groupby(['County', 'Year', 'Type of Rate or Count Measure']).sum().reset_index()
    dispen_df.rename(columns={'Rate or Count': 'Total Prescriptions or Dispensations'}, inplace=True)

    dispen_df = dispen_df.pivot(index=['County', 'Year'],
                                columns='Type of Rate or Count Measure',
                                values='Total Prescriptions or Dispensations').reset_index()

    return dispen_df

def arrests():
    # Loading Arrests dataset
    arrests_df = pd.read_csv('../data/Pulled/Opioid_Seizures_and_Arrests_CY_2013_-_Current_Quarterly_County_State_Police.csv')

    # removing the index column and removing any duplicates in the initial dataset
    arrests_df.drop('Unnamed: 0', axis=1, inplace=True)
    arrests_df.drop_duplicates(inplace=True)

    keep_columns = ['County Name', 'Year', 'Drug', 'Incident Count', 'Drug Quantity', 'Arrests']
    arrests_df = arrests_df[keep_columns]

    arrests_df = arrests_df.groupby(['County Name', 'Year', 'Drug']).sum().reset_index()
    arrests_df.rename(columns={'County Name': 'County',
                               'Arrests': 'Opioid Arrest Count',
                               'Incident Count': 'Opioid Incident Count'
                               },
                      inplace=True)

    arrests_df = arrests_df.pivot(index=['County', 'Year'],
                                  columns='Drug',
                                  values=['Opioid Incident Count', 'Opioid Arrest Count']).reset_index()

    arrests_df.columns = arrests_df.columns.map('-'.join).str.strip('-')
    arrests_df.columns = arrests_df.columns = [s.replace('-', ' - ') for s in arrests_df.columns]

    arrests_df = arrests_df.fillna(0)

    return arrests_df


def county_population():
    # Loading County Population dataset
    population_df = pd.read_csv('../data/Pulled/County_pop.csv')

    population_df = population_df.rename(columns={
        'Numeric_change': 'County Numeric Change Since 2010',
        'Percent_Change': 'County Percent Change Since 2010',
        '2020': 'County Population'})
    population_df = population_df[['County',
                                   'County Population',
                                   'County Numeric Change Since 2010',
                                   'County Percent Change Since 2010']]

    # Filtering out Countys other than PA
    population_df = population_df[population_df['County'] != 'Pennsylvania']

    # Remove "County" from County name
    cnt_pop_df = fix(population_df, inplace=False)
    return cnt_pop_df


def main():
    # opioid_list = ['CARFENTANIL',
    #               'FENTANYL',
    #               'FENTANYL ANALOG/OTHER SYNTHETIC OPIOID',
    #               'HEROIN', 'METHADONE',
    #               'PHARMACEUTICAL OPIOID',
    #               'SUBOXONE']
    #
    # incidents_with_naloxone(opioid_list)

    # print(takeback())
    # print(treatment().sort_values(by='County'))
    # print(takeback().sort_values(by='County'))
    print(county_population())


if __name__ == '__main__':
    main()



