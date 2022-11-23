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
import functools as ft


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

    opdfnew["Naloxone Administered"] = opdfnew['Naloxone Administered'].map(lambda x: 1 if x == "Y" else 0)
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

def incidents_with_naloxone(opioid_list, export_incident_df=True):
    # Loading PA GOV
    df = pd.read_csv('../data/Pulled/Overdose_Information_Network_Data_CY_January_2018_-_Current_Monthly_County_State_Police.csv')

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
    opdf.loc[opdf['Response Desc'].isnull(), 'Response Desc'] = 'None'

    opdf['Incident Date ym'] = pd.to_datetime(opdf['Incident Date']).dt.to_period('Y')
    opdf['Incident Date ym'] = opdf['Incident Date ym'].astype(str)
    opdf['Incident Date ym'] = opdf['Incident Date ym'].astype(int)

    # @TODO confirm with Joey whether this oppdf dataframe is needed or unintentional.
    oppdf = opdf.groupby(['Incident Date ym'])[['Incident ID']].count().reset_index()
    opdfnew = yn_switch(opdf, inplace=False)

    if export_incident_df:
        opdfnew.to_csv('../data/Aggregated/incidents.csv', index=False)

    # limiting
    opdfnew = opdfnew[['Incident ID',
                       'Incident County Name',
                       'Naloxone Administered',
                       'Survive',
                       'Incident Date ym']]

    # Renaming for joins later
    opdfnew = opdfnew.rename(columns={'Incident County Name': 'County',
                                      'Incident Date ym': 'Year'})
    # Getting totals
    opdfnew['Total Overdoses Per County'] = opdfnew.groupby(['County', 'Year'])['County'].transform('count')
    opdfnew['Percent Naloxone Administered Per County/Year'] = opdfnew.groupby(['County', 'Year'])['Naloxone Administered'].transform(
        'mean')
    opdfnew['Percent Survive Overdose Per County/Year'] = opdfnew.groupby(['County', 'Year'])['Survive'].transform(
        'mean')
    opdfnew['Total Number of PA.gov Overdoses Per County/Year'] = opdfnew.groupby(['County', 'Year'])[
        'Incident ID'].transform('count')

    # Limiting
    opdfnew = opdfnew[['County', 'Year',
                       'Percent Naloxone Administered Per County/Year',
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
    takebackdf.rename(columns={'Drug Take-Back Site':'Drug Take-Back Sites'}, inplace=True)
    return takebackdf


def treatment():

    # Loading treatment
    treatment_locations = pd.read_csv('../data/Pulled/Drug_and_Alcohol_Treatment_Facilities_May_2018_County_Drug_and_Alcohol_Programs.csv')
    treatment_loc_counts = treatment_locations.groupby('County').count()['Name of Facility'].reset_index()
    treatment_loc_counts.rename(columns = {'Name of Facility': 'Drug Treatment Locations'}, inplace=True)
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
                               'Incident Count': 'Incidents'
                               },
                      inplace=True)

    arrests_df = arrests_df.pivot(index=['County', 'Year'],
                                  columns='Drug',
                                  values=['Incidents', 'Arrests', 'Drug Quantity']).reset_index()

    arrests_df.columns = arrests_df.columns.map('-'.join).str.strip('-')
    arrests_df.columns = arrests_df.columns = [s.replace('-', ' - ') for s in arrests_df.columns]

    arrests_df = arrests_df.fillna(0)

    # Creating computed collumns
    arrests_df['%Incidents Fentanyl'] = (arrests_df['Incidents - Fentanyl'] /
                                        (arrests_df['Incidents - Fentanyl'] + arrests_df['Incidents - Opium'] + arrests_df[
                                            'Incidents - Heroin']) * 100)

    arrests_df['%Arrests Fentanyl'] = (arrests_df['Arrests - Fentanyl'] /
                                      (arrests_df['Arrests - Fentanyl'] + arrests_df['Arrests - Opium'] + arrests_df[
                                          'Arrests - Heroin'] ) * 100)

    arrests_df['%Quantity Fentanyl'] = (arrests_df['Drug Quantity - Fentanyl'] /
                                       (arrests_df['Drug Quantity - Fentanyl'] + arrests_df['Drug Quantity - Opium'] + arrests_df[
                                           'Drug Quantity - Heroin'] ) * 100)

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
                                   'County Percent Change Since 2010']]

    # Filtering out Countys other than PA
    population_df = population_df[population_df['County'] != 'Pennsylvania']

    # Remove "County" from County name
    cnt_pop_df = fix(population_df, inplace=False)
    return cnt_pop_df


def rates_per_10000(df, numeric_columns):
    new_df = df.copy()
    new_df.loc[:, numeric_columns] = new_df.loc[:, numeric_columns].div(new_df['County Population'],
                                                                                axis=0) * 10000
    return new_df


def main():
    opioid_list = ['CARFENTANIL',
                  'FENTANYL',
                  'FENTANYL ANALOG/OTHER SYNTHETIC OPIOID',
                  'HEROIN', 'METHADONE',
                  'PHARMACEUTICAL OPIOID',
                  'SUBOXONE']

    df_list_county_and_year = [incidents_with_naloxone(opioid_list), risky_prescribing(),
                               dispensation(), arrests()]

    # merges all the datasets with County and Year granularity
    merged_df = reduce(lambda left, right: pd.merge(left, right, on=['County', 'Year']), df_list_county_and_year)

    df_list_county = [merged_df, takeback(), treatment(), county_population()]

    merged_df = reduce(lambda left, right: pd.merge(left, right, on='County'), df_list_county)

    merged_df.rename(columns={'Number of Dispensations (by pharmacy location)': 'Total Drug Dispensation',
                              'Number of Prescriptions (by patient location)': 'Total Prescriptions',
                              'Percent Naloxone Administered Per County/Year': '% Naloxone Admin',
                              'Percent Survive Overdose Per County/Year': '% OD Survival',
                              'Total Number of PA.gov Overdoses Per County/Year': 'Opioid Overdoses',
                              'Number of Individuals Seeing 3+ Prescribers and 3+ Dispensers': '3+ Prescribers and 3+ Dispensers',
                              'Number of Individuals with Average Daily MME > 50': 'Average Daily MME > 50',
                              'Number of Individuals with Overlapping Opioid/Benzodiazepine Prescriptions': 'Overlapping Opioid/Benzodiazepine Prescriptions',
                              }, inplace=True)

    numeric_columns = ['Opioid Overdoses',
                       '3+ Prescribers and 3+ Dispensers',
                       'Average Daily MME > 50',
                       'Overlapping Opioid/Benzodiazepine Prescriptions',
                       'Total Drug Dispensation',
                       'Total Prescriptions',
                       'Incidents - Fentanyl',
                       'Incidents - Heroin',
                       'Incidents - Opium',
                       'Arrests - Fentanyl',
                       'Arrests - Heroin',
                       'Arrests - Opium',
                       'Drug Quantity - Fentanyl',
                       'Drug Quantity - Heroin',
                       'Drug Quantity - Opium',
                       'Drug Take-Back Sites',
                       'Drug Treatment Locations',
                       ]

    merged_df = rates_per_10000(merged_df, numeric_columns)
    merged_df.to_csv('../data/Aggregated/main_county.csv', index=False)

if __name__ == '__main__':
    main()



