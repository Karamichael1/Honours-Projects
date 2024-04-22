import pandas as pd
from pgmpy.estimators import HillClimbSearch, BayesianEstimator, BicScore
from pgmpy.models import BayesianModel, BayesianNetwork
from pgmpy.inference import VariableElimination
from ucimlrepo import fetch_ucirepo
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from daft import PGM
import daft
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import log_loss, accuracy_score, f1_score
from sklearn.model_selection import train_test_split

def plot_structure(DAG):
    # Create a NetworkX graph from the DAG
    G = nx.DiGraph()
    G.add_nodes_from(DAG.nodes)
    G.add_edges_from(DAG.edges)

    # Use Graphviz dot layout
    pos = nx.drawing.layout.planar_layout(G)

    # Create the plot
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=500, arrowsize=20)
    plt.show()

# Fetch dataset
adult = fetch_ucirepo(id=2)

# Data (as pandas dataframes)
X = adult.data.features
y = adult.data.targets

# Preprocessing: Label Encoding for categorical variables
categorical_vars = ['workclass', 'education', 'marital-status', 'occupation', 'relationship', 'race', 'sex', 'native-country']
label_encoders = {}
for col in categorical_vars:
    label_encoders[col] = LabelEncoder()
    X[col] = label_encoders[col].fit_transform(X[col])

# Discretize the features using quantile-based discretization
num_bins = 5  # Number of bins for discretization
discretize_vars = ['hours-per-week', 'capital-loss', 'capital-gain', 'age', 'fnlwgt', 'education-num']
X_discretized = X.copy()
for col in discretize_vars:
    X_discretized[col] = pd.cut(X[col], 5, labels=False)

data = pd.concat([X_discretized, y], axis=1)
data['income'] = data['income'].str.strip('.')

# Split the data into train, validation, and test sets
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)
train_data, val_data = train_test_split(train_data, test_size=0.25, random_state=42)  # 0.25 of 0.8 is 0.2

# Learn Bayesian network structure using Hill Climb Search on the training data
est = HillClimbSearch(train_data)
best_model = est.estimate(scoring_method=BicScore(train_data))

# Print learned Bayesian network structure
print("Learned Bayesian network structure:")
BayesNet = BayesianNetwork(best_model.edges())

# Create CPTs for the Bayesian network using the training data
BayesNet.fit(train_data)
print(best_model.nodes())

# Print CPTs
print("\nConditional Probability Tables (CPTs):")
# for cpd in BayesNet.get_cpds():
#     print(cpd)

inference = VariableElimination(BayesNet)

val_data = val_data.dropna()

# Calculate log loss, accuracy, and F1 score on the validation set
y_true_val = val_data['income'].map({'<=50K': 0, '>50K': 1}).values  # Convert string labels to integers
y_pred_probs_val = []
y_pred_val = []
for _, row in val_data.iterrows():
    evidence = row.drop('income').to_dict()
    query = inference.query(['income'], evidence=evidence)
    prob = query.values[1]
    if not np.isnan(prob):
        y_pred_probs_val.append(prob)  # Assuming '1' represents the positive class
        y_pred_val.append(1 if prob > 0.5 else 0)  # Threshold the predicted probabilities

# Calculate metrics only if there are valid predictions
if len(y_pred_probs_val) > 0:
    log_loss_value_val = log_loss(y_true_val, y_pred_probs_val)
    accuracy_val = accuracy_score(y_true_val, y_pred_val)
    f1_val = f1_score(y_true_val, y_pred_val)  # Calculate F1 score



# Remove rows with missing values from the test data
test_data = test_data.dropna()

# Calculate log loss, accuracy, and F1 score on the test set
y_true_val = val_data['income'].map({'<=50K': 0, '>50K': 1}).values  # Convert string labels to integers
y_pred_probs_val = []
y_pred_val = []
for _, row in val_data.iterrows():
    evidence = row.drop('income').to_dict()
    try:
        query = inference.query(['income'], evidence=evidence)
        prob = query.values[1]
        if not np.isnan(prob):
            y_pred_probs_val.append(prob)  # Assuming '1' represents the positive class
            y_pred_val.append(1 if prob > 0.5 else 0)  # Threshold the predicted probabilities
    except KeyError:
        continue

# Calculate metrics only if there are valid predictions
if len(y_pred_probs_val) > 0:
    log_loss_value_val = log_loss(y_true_val[:len(y_pred_probs_val)], y_pred_probs_val)
    accuracy_val = accuracy_score(y_true_val[:len(y_pred_val)], y_pred_val)
    f1_val = f1_score(y_true_val[:len(y_pred_val)], y_pred_val)  # Calculate F1 score

    print("\nValidation Set Metrics:")
    print("Log Loss:", log_loss_value_val)
    print("Accuracy:", accuracy_val)
    print("F1 Score:", f1_val)
else:
    print("No valid predictions for the validation set.")

# Calculate log loss, accuracy, and F1 score on the test set
y_true_test = test_data['income'].map({'<=50K': 0, '>50K': 1}).values  # Convert string labels to integers
y_pred_probs_test = []
y_pred_test = []
for _, row in test_data.iterrows():
    evidence = row.drop('income').to_dict()
    try:
        query = inference.query(['income'], evidence=evidence)
        prob = query.values[1]
        if not np.isnan(prob):
            y_pred_probs_test.append(prob)  # Assuming '1' represents the positive class
            y_pred_test.append(1 if prob > 0.5 else 0)  # Threshold the predicted probabilities
    except KeyError:
        continue

# Calculate metrics only if there are valid predictions
if len(y_pred_probs_test) > 0:
    log_loss_value_test = log_loss(y_true_test[:len(y_pred_probs_test)], y_pred_probs_test)
    accuracy_test = accuracy_score(y_true_test[:len(y_pred_test)], y_pred_test)
    f1_test = f1_score(y_true_test[:len(y_pred_test)], y_pred_test)  # Calculate F1 score

    print("\nTest Set Metrics:")
    print("Log Loss:", log_loss_value_test)
    print("Accuracy:", accuracy_test)
    print("F1 Score:", f1_test)
else:
    print("No valid predictions for the test set.")
plot_structure(best_model)