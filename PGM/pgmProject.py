import pandas as pd
import numpy as np
from pgmpy.models import BayesianNetwork
from pgmpy.estimators import MmhcEstimator, BayesianEstimator
from pgmpy.inference import VariableElimination
from sklearn.preprocessing import MinMaxScaler, KBinsDiscretizer
from sklearn.model_selection import StratifiedKFold
import os
print("Current working directory:", os.getcwd())
# Load and combine all Excel files into a single DataFrame
# Load and combine all Excel files into a single DataFrame
data = pd.DataFrame()
file_names = ['C:/Users/User/Documents/GitHub/Honours-Projects/PGM/Transfer rep - Aloe Ridge 1 - 20180102 - 20240422.xlsx',
              'C:/Users/User/Documents/GitHub/Honours-Projects/PGM/Transfer rep - Aloe Ridge 1 - 20060101 - 20080101.xlsx',
              'C:/Users/User/Documents/GitHub/Honours-Projects/PGM/Transfer rep - Aloe Ridge 1 - 20080101 - 20180101.xlsx',
              'C:/Users/User/Documents/GitHub/Honours-Projects/PGM/Transfer rep - Aloe Ridge 2 - 20080101 - 20150101.xlsx',
              'C:/Users/User/Documents/GitHub/Honours-Projects/PGM/Transfer rep - Aloe Ridge 2 - 20150102 - 20240422.xlsx',
              'C:/Users/User/Documents/GitHub/Honours-Projects/PGM/Transfer rep - Greenstone Crest - 20150101 - 20150930.xlsx',
              'C:/Users/User/Documents/GitHub/Honours-Projects/PGM/Transfer rep - Greenstone Crest - 20151001 - 20160601.xlsx',
              'C:/Users/User/Documents/GitHub/Honours-Projects/PGM/Transfer rep - Greenstone Crest - 20160601 - 20161231.xlsx',
              'C:/Users/User/Documents/GitHub/Honours-Projects/PGM/Transfer rep - Greenstone Crest - 20170101 - 20200331.xlsx',
              'C:/Users/User/Documents/GitHub/Honours-Projects/PGM/Transfer rep - Greenstone Crest - 20200401 - 20240422.xlsx',
              'C:/Users/User/Documents/GitHub/Honours-Projects/PGM/Transfer rep - Greenstone Ridge 1.xlsx',
              'C:/Users/User/Documents/GitHub/Honours-Projects/PGM/Transfer rep - Greenstone Ridge 2.xlsx']

for file in file_names:
    data = pd.concat([data, pd.read_excel(file)], ignore_index=True)
# Data Preprocessing
# Handle missing values
data.fillna(method='ffill', inplace=True)
data.fillna(method='bfill', inplace=True)

# Normalize numerical features using Min-Max scaling
scaler = MinMaxScaler()
numerical_cols = ['Sales price', 'Size']
data[numerical_cols] = scaler.fit_transform(data[numerical_cols])

# Discretize numerical features using KBinsDiscretizer
discretizer = KBinsDiscretizer(n_bins=5, encode='ordinal', strategy='quantile')
data[numerical_cols] = discretizer.fit_transform(data[numerical_cols])

# Create an ensemble of Bayesian networks using bagging and cross-validation
n_estimators = 10
n_splits = 5
ensemble_models = []
kf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

for train_index, test_index in kf.split(data, data['Sales price']):
    train_data = data.iloc[train_index]
    test_data = data.iloc[test_index]
    for _ in range(n_estimators):
        # Generate bootstrap samples
        bootstrap_indices = np.random.choice(len(train_data), size=len(train_data), replace=True)
        bootstrap_data = train_data.iloc[bootstrap_indices]

        # Perform structured learning using MmhcEstimator
        estimator = MmhcEstimator(bootstrap_data)
        model = estimator.estimate()

        # Print the learned Bayesian network structure
        print(f"Learned Bayesian Network structure: {model.edges()}")

        # Estimate the parameters of the Bayesian network using Bayesian estimation
        estimator = BayesianEstimator(model, bootstrap_data)
        model.fit(bootstrap_data, estimator=estimator)
        ensemble_models.append(model)

# Inference function to estimate sales price
def estimate_sales_price(township, erf, suburb, street_number, sales_date, seller_name, size, r_m2=None):
    evidence = {
        'Township': township,
        'Erf': erf,
        'Suburb': suburb,
        'Street Number': street_number,
        'Sales Date': sales_date,
        'Seller Name': seller_name,
        'Size': size
    }

    # Discretize input variables
    size_discretized = discretizer.transform([[size]])[0][0]

    # Perform inference using each model in the ensemble
    price_probabilities_ensemble = []
    for model in ensemble_models:
        inference = VariableElimination(model)
        query = inference.query(variables=['Sales price'], evidence=evidence)
        price_probabilities_ensemble.append(query['Sales price'].values)

    # Average the price probabilities from all models
    price_probabilities_mean = np.mean(price_probabilities_ensemble, axis=0)

    # Calculate the expected sales price
    expected_sales_price = np.sum(price_probabilities_mean * discretizer.bin_edges_[0])

    return expected_sales_price

# Example usage
township = 'GREENSTONE HILL EXT 20'
erf = 1834
suburb = 'GREENSTONE HILL'
street_number = 41
sales_date = '2015/02/03'
seller_name = 'PRIVATE PERSON'
size = 300
r_m2 = None  # If not provided, it will be estimated from the data

estimated_price = estimate_sales_price(township, erf, suburb, street_number, sales_date, seller_name, size, r_m2)
print(f"Estimated Sales Price: {estimated_price:.2f}")