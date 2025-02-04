# preprocess_data.py
# Kartik Sastry
# 3/8/2022

# Description:
# Python script for dimensionality reduction.
# See midterm report for detailed comments.

# Usage:
# python combine_data.py
# python preprocess_data.py

# Inputs:
# - ../dataset/all_trips.csv: generated by combine_data.py

# Outputs:
# - ../dataset/all_trips_reduced.csv: containing data from all trips with only essential features
# - ../dataset/reduced_feature_names.txt: containing the names of all features in the reduced dataset

################################################
#                 Libraries
################################################
import pandas as pd
import numpy as np

################################################
#     Relative Paths to Inputs/Outputs
################################################
path_to_all_data = '../dataset/all_trips.csv'
path_to_all_data_reduced = '../dataset/all_trips_reduced.csv'
path_to_feature_list = '../dataset/reduced_feature_names.txt'

################################################
#         Read In Master Data Record
################################################
# encoding='utf-8', errors='ignore' skips over non-standard characters, e.g. the degree symbol
with open(path_to_all_data, encoding='utf-8', errors='ignore') as f:
    df = pd.read_csv(f, delimiter=',')

# Move 'trip_id' to the second-to-last column, and 'temperature' to the last column
df = df.reindex(columns=[col for col in df.columns if col != 'trip_id'] + ['trip_id'])
df = df.reindex(columns=[col for col in df.columns if col != 'Battery Temperature [C]'] + ['Battery Temperature [C]'])

# Print shape
print('Shape of original dataset: ', df.shape)
print()

################################################
#   Removal of Specially Measured Features
################################################
# inplace=true modifies df in place!
features_to_drop = ['Cabin Temperature Sensor [C]', 'Ambient Temperature Sensor [C]', 'Coolant Volume Flow +500 [l/h]', 'Temperature Coolant Heater Inlet [C]','Temperature Coolant Heater Outlet [C]','Temperature Heat Exchanger Outlet [C]','Temperature Defrost lateral left [C]','Temperature Defrost lateral right [C]','Temperature Defrost central [C]','Temperature Defrost central left [C]','Temperature Defrost central right [C]','Temperature Footweel Driver [C]','Temperature Footweel Co-Driver [C]','Temperature Feetvent Co-Driver [C]','Temperature Feetvent Driver [C]','Temperature Head Co-Driver [C]','Temperature Head Driver [C]','Temperature Vent right [C] ','Temperature Vent central right [C]','Temperature Vent central left [C]','Temperature Vent right [C]']
df.drop(columns=features_to_drop, inplace=True)

################################################
#       Removal of Unnecessary Features
################################################
# inplace=true modifies df in place!
features_to_drop = ['Coolant Temperature Heatercore [C]', 'Requested Coolant Temperature [C]', 'Coolant Temperature Inlet [C]', 'Heat Exchanger Temperature [C]']
df.drop(columns=features_to_drop, inplace=True)

################################################
# Removal of Redundant Features (By Inspection)
################################################
# inplace=true modifies df in place!
features_to_drop = ['Regenerative Braking Signal ', 'max. Battery Temperature [C]', 'displayed SoC [%]', 'min. SoC [%]', 'max. SoC [%)', 'Heating Power CAN [kW]', 'Heating Power LIN [W]', 'Heater Signal']
df.drop(columns=features_to_drop, inplace=True)

################################################
# Removal of Redundant Features (By Correlation)
################################################
# compute correlation matrix
abs_corr_matrix = np.abs(df.corr(method='pearson', numeric_only=True))

# extract pairwise correlations and sort by value
corr_pairs = abs_corr_matrix.unstack().sort_values(ascending=False)

# drop duplicates (i.e. A, B is the same as B, A)
corr_pairs = corr_pairs[corr_pairs.index.map(lambda x: x[0] < x[1])]

# print sorted pairs and their correlation coefficients
print('Pairs of features with strong Pearson correlation:')
for pair, corr in corr_pairs.items():
    if (corr >= 0.7):
        print(f"{pair}: {corr:.2f}")
print()

# inplace=true modifies df in place!
features_to_drop = ['Longitudinal Acceleration [m/s^2]', 'Heater Voltage [V]', 'Heater Current [A]']
df.drop(columns=features_to_drop, inplace=True)

################################################
#          Check for Missing Data
################################################
# Check for missing data in each column
missing_data = df.isnull().sum() + df.isna().sum() + df.eq('None').sum()
print('Missing data by feature:')
print(missing_data)
print()

# count the number of missing and total observations for each trip_id
missing_mask = df.isnull() | df.isna() | (df == 'None')
missing_count = missing_mask.groupby(df['trip_id']).sum()
total_count = missing_mask.groupby(df['trip_id']).count()

print('Missing data by trip file:')
print('file, #missing, #total')
# print the missing data statistics for each trip_id
for trip_id in missing_count.index:
    missing_obs = missing_count.loc[trip_id].sum()
    total_obs = total_count.loc[trip_id].max()
    print(trip_id, missing_obs, total_obs)
print()

# drop any rows with missing data
df = df.dropna()

# # Check that missing data in each column is gone
# missing_data = df.isnull().sum() + df.isna().sum() + df.eq('None').sum()
# print(missing_data)

################################################
#              Discard Outliers
################################################
# filter rows where trip_id is not TripB02
df_filtered = df[df['trip_id'] != 'TripB02']

# find the maximum value of 'Requested Heating Power [W]'
max_heater_power = df_filtered['Requested Heating Power [W]'].max()

# discard rows where Requested Heating Power [W] >= max_heater_power
df = df[df['Requested Heating Power [W]'] < max_heater_power]

################################################
#          Save Concatenated Data to CSV
################################################
# Print shape
print('Shape of reduced dataset: ', df.shape)
print()

print('Saving reduced dataset to:', path_to_all_data_reduced)
df.to_csv(path_to_all_data_reduced, index=False)

################################################
#      Generate Text File w/ Feature Names
################################################
# Write the column names to a text file, one per line
print('Saving a list of feature names in:', path_to_feature_list)
with open(path_to_feature_list, 'w') as f:
    for col in df.columns:
        f.write(col + '\n')
