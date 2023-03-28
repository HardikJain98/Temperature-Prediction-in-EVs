# evaluate_models.py
# Kartik Sastry
# 3/12/2022

# Description:
# Python script to evaluate all regression models by training on and testing against common data

# Usage:
# python combine_data.py
# python preprocess_data.py
# (optional) python visualize_data.py
# python evaluate_models

# Inputs:
# - ../dataset/all_trips_reduced.csv: generated by preprocess_data.py
# - implementations of models in models.py

# Outputs:
# - ../figs/errplot.png

################################################
#                 Libraries
################################################
import pandas as pd
import numpy as np
from models import model_1_train, model_1_predict, model_2_train, model_2_predict, model_3_train, model_3_predict, model_4_train, model_4_predict, evaluate
import matplotlib.pyplot as plt

################################################
#     Relative Paths to Inputs/Outputs
################################################
path_to_figs_dir = '../figs/'

################################################
#              Read In Dataset
################################################
# Read in all data
path_to_all_data_reduced = '../dataset/all_trips_reduced.csv'
with open(path_to_all_data_reduced, encoding='utf-8', errors='ignore') as f:
    data = pd.read_csv(f, delimiter=',')

# Drop trip_id column for
data = data.drop(columns=['trip_id'])

# Convert to numpy
data = data.to_numpy()

# Split data into features (X) and target (y). Temperature is the last column!
X = data[:, :-1]
y = data[:, -1]

################################################
#           K-Fold Cross Validation
################################################
# Number of folds (1/K is the fraction of data used to test; remaining (K-1)/K used to train)
K = 5

# Number of observations
N = X.shape[0]
fold_size = N // K

# Shuffle indices randomly; seed RNG for repeatablity
np.random.seed(sum(ord(c) for c in "kartik was here"))
indices = np.random.permutation(N)

# Go!
model_1_error_metrics = []
model_2_error_metrics = []
model_3_error_metrics = []
model_4_error_metrics = []
model_1_errors = np.array([])
model_2_errors = np.array([])
model_3_errors = np.array([])
model_4_errors = np.array([])
for i in range(K):
    ################################################
    #       Get Testing / Training Data
    ################################################
    start, end = i * fold_size, (i+1) * fold_size
    X_test, y_test = X[indices[start:end]], y[indices[start:end]]
    X_train = np.vstack((X[indices[:start]], X[indices[end:]]))
    y_train = np.concatenate((y[indices[:start]], y[indices[end:]]))

    ################################################
    #           Train and Test Model 1
    ################################################
    # Train model 1 on training data
    model = model_1_train(X_train, y_train)

    # Test model 1 on test data
    y_test_pred = model_1_predict(model, X_test)

    # Evaluate model performance
    model_1_error_metrics.append(evaluate(y_test, y_test_pred))
    model_1_errors = np.concatenate((model_1_errors, y_test-y_test_pred))

    ################################################
    #           Train and Test Model 2
    ################################################
    # Train model 2 on training data
    model = model_2_train(X_train, y_train)

    # Test model 2 on test data
    y_test_pred = model_2_predict(model, X_test)

    # Evaluate model performance
    model_2_error_metrics.append(evaluate(y_test, y_test_pred))
    model_2_errors = np.concatenate((model_2_errors, y_test-y_test_pred))

    ################################################
    #           Train and Test Model 3
    ################################################
    # Train model 3 on training data
    model = model_3_train(X_train, y_train)

    # Test model 3 on test data
    y_test_pred = model_3_predict(model, X_test)

    # Evaluate model performance
    model_3_error_metrics.append(evaluate(y_test, y_test_pred))
    model_3_errors = np.concatenate((model_3_errors, y_test-y_test_pred))

    ################################################
    #           Train and Test Model 4
    ################################################

################################################
#            Look At Error Metrics
################################################
print('Model 1:')
print('Errors Per Fold:')
print(np.array(model_1_error_metrics).T)
print('Average Across Folds:')
print(np.mean(np.array(model_1_error_metrics).T, axis=1))

print()

print('Model 2:')
print('Errors Per Fold:')
print(np.array(model_2_error_metrics).T)
print('Average Across Folds:')
print(np.mean(np.array(model_2_error_metrics).T, axis=1))

print()

print('Model 3:')
print('Errors Per Fold:')
print(np.array(model_3_error_metrics).T)
print('Average Across Folds:')
print(np.mean(np.array(model_3_error_metrics).T, axis=1))

# print()

# print('Model 4:')
# print('Errors Per Fold:')
# print(np.array(model_4_error_metrics).T)
# print('Average Across Folds:')
# print(np.mean(np.array(model_4_error_metrics).T, axis=1))

################################################
#            Look At Error Histograms
################################################
# Create a 1x3 grid of subplots
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(15, 3))

ax[0].hist(model_1_errors, bins=20)
ax[0].set_xlabel("Estimation Error [deg C]")
ax[0].set_ylabel("Count")
ax[0].set_title("Linear Regression")

ax[1].hist(model_2_errors, bins=20)
ax[1].set_xlabel("Estimation Error [deg C]")
ax[1].set_ylabel("Count")
ax[1].set_title("Polynomial Regression")

ax[2].hist(model_3_errors, bins=20)
ax[2].set_xlabel("Estimation Error [deg C]")
ax[2].set_ylabel("Count")
ax[2].set_title("Polynomial Regression w/ $\ell_1$ Penalty")

# plt.show() # blocks execution
fig.tight_layout()
fig.savefig(path_to_figs_dir + 'errplot.png', format='png', bbox_inches='tight')
