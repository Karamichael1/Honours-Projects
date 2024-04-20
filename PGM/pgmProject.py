import pandas as pd
import numpy as np
from pgmpy.models import BayesianNetwork
from pgmpy.estimators import MmhcEstimator, BayesianEstimator
from pgmpy.inference import VariableElimination
from sklearn.preprocessing import MinMaxScaler, KBinsDiscretizer
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import BaggingRegressor

# Load the dataset
data = pd.read_csv('property_data.csv')

# Data Preprocessing
# Handle missing values using forward fill and backward fill
data.fillna(method='ffill', inplace=True)
data.fillna(method='bfill', inplace=True)

# Handling Outliers using winsorization
def winsorize(data, column, limit):
    lower_limit = data[column].quantile(limit)
    upper_limit = data[column].quantile(1 - limit)
    data[column] = data[column].clip(lower=lower_limit, upper=upper_limit)
    return data

outlier_columns = ['square_feet', 'price']
data = winsorize(data, outlier_columns, 0.05)

# Normalize numerical features using Min-Max scaling
scaler = MinMaxScaler()
numerical_columns = ['square_feet', 'price']
data[numerical_columns] = scaler.fit_transform(data[numerical_columns])

# Discretize numerical features using KBinsDiscretizer
discretizer = KBinsDiscretizer(n_bins=5, encode='ordinal', strategy='quantile')
data[numerical_columns] = discretizer.fit_transform(data[numerical_columns])

# Create an ensemble of Bayesian networks using bagging and cross-validation
n_estimators = 10
n_splits = 5
ensemble_models = []

kf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

for train_index, test_index in kf.split(data, data['price']):
    train_data = data.iloc[train_index]
    test_data = data.iloc[test_index]
    
    for _ in range(n_estimators):
        # Generate bootstrap samples
        bootstrap_indices = np.random.choice(len(train_data), size=len(train_data), replace=True)
        bootstrap_data = train_data.iloc[bootstrap_indices]
        
        # Perform structured learning using MmhcEstimator
        estimator = MmhcEstimator(bootstrap_data)
        model = estimator.estimate()
        
        # Estimate the parameters of the Bayesian network using Bayesian estimation
        estimator = BayesianEstimator(model, bootstrap_data)
        model.fit(bootstrap_data, estimator=estimator)
        
        ensemble_models.append(model)

# Function to calculate property price evaluation using the ensemble
def evaluate_property_price_ensemble(area, bedrooms, bathrooms, square_feet):
    # Discretize input variables
    square_feet_discretized = discretizer.transform([[square_feet]])[0][0]
    
    # Perform inference using each model in the ensemble
    price_probabilities_ensemble = []
    for model in ensemble_models:
        inference = VariableElimination(model)
        query = inference.query(variables=['price'], evidence={'area': area, 'bedrooms': bedrooms, 'bathrooms': bathrooms, 'square_feet': square_feet_discretized})
        price_probabilities_ensemble.append(query['price'].values)
    
    # Average the price probabilities from all models
    price_probabilities_mean = np.mean(price_probabilities_ensemble, axis=0)
    
    # Calculate expected price
    expected_price = np.sum(price_probabilities_mean * discretizer.bin_edges_[0])
    
    return expected_price

# Example usage
area = 'Residential'
bedrooms = 3
bathrooms = 2
square_feet = 1500

estimated_price_ensemble = evaluate_property_price_ensemble(area, bedrooms, bathrooms, square_feet)
print(f"Estimated Property Price (Ensemble): ${estimated_price_ensemble:.2f}")