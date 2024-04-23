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
   G = nx.DiGraph()
   G.add_nodes_from(DAG.nodes)
   G.add_edges_from(DAG.edges)

   pos = nx.drawing.layout.planar_layout(G)

   plt.figure(figsize=(10, 8))
   nx.draw(G, pos, with_labels=True, node_size=500, arrowsize=20)
   plt.show()

adult = fetch_ucirepo(id=2)

X = adult.data.features
y = adult.data.targets

categorical_vars = ['workclass', 'education', 'marital-status', 'occupation', 'relationship', 'race', 'sex', 'native-country']
label_encoders = {}
for col in categorical_vars:
   label_encoders[col] = LabelEncoder()
   X[col] = label_encoders[col].fit_transform(X[col])

num_bins = 5
discretize_vars = ['hours-per-week', 'capital-loss', 'capital-gain', 'age', 'fnlwgt', 'education-num']
X_discretized = X.copy()
for col in discretize_vars:
   X_discretized[col] = pd.cut(X[col], 5, labels=False)

data = pd.concat([X_discretized, y], axis=1)
data['income'] = data['income'].str.strip('.')

train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)
train_data, val_data = train_test_split(train_data, test_size=0.25, random_state=42)

est = HillClimbSearch(train_data)
best_model = est.estimate(scoring_method=BicScore(train_data))

print("Learned Bayesian network structure:")
BayesNet = BayesianNetwork(best_model.edges())

BayesNet.fit(train_data)
print(best_model.nodes())

print("\nConditional Probability Tables (CPTs):")

inference = VariableElimination(BayesNet)

val_data = val_data.dropna()

y_true_val = val_data['income'].map({'<=50K': 0, '>50K': 1}).values
y_pred_probs_val = []
y_pred_val = []
for _, row in val_data.iterrows():
   evidence = row.drop('income').to_dict()
   query = inference.query(['income'], evidence=evidence)
   prob = query.values[1]
   if not np.isnan(prob):
       y_pred_probs_val.append(prob)
       y_pred_val.append(1 if prob > 0.5 else 0)

if len(y_pred_probs_val) > 0:
   log_loss_value_val = log_loss(y_true_val, y_pred_probs_val)
   accuracy_val = accuracy_score(y_true_val, y_pred_val)
   f1_val = f1_score(y_true_val, y_pred_val)


test_data = test_data.dropna()

y_true_val = val_data['income'].map({'<=50K': 0, '>50K': 1}).values
y_pred_probs_val = []
y_pred_val = []
for _, row in val_data.iterrows():
   evidence = row.drop('income').to_dict()
   try:
       query = inference.query(['income'], evidence=evidence)
       prob = query.values[1]
       if not np.isnan(prob):
           y_pred_probs_val.append(prob)
           y_pred_val.append(1 if prob > 0.5 else 0)
   except KeyError:
       continue

if len(y_pred_probs_val) > 0:
   log_loss_value_val = log_loss(y_true_val[:len(y_pred_probs_val)], y_pred_probs_val)
   accuracy_val = accuracy_score(y_true_val[:len(y_pred_val)], y_pred_val)
   f1_val = f1_score(y_true_val[:len(y_pred_val)], y_pred_val)

   print("\nValidation Set Metrics:")
   print("Log Loss:", log_loss_value_val)
   print("Accuracy:", accuracy_val)
   print("F1 Score:", f1_val)
else:
   print("No valid predictions for the validation set.")

y_true_test = test_data['income'].map({'<=50K': 0, '>50K': 1}).values
y_pred_probs_test = []
y_pred_test = []
for _, row in test_data.iterrows():
   evidence = row.drop('income').to_dict()
   try:
       query = inference.query(['income'], evidence=evidence)
       prob = query.values[1]
       if not np.isnan(prob):
           y_pred_probs_test.append(prob)
           y_pred_test.append(1 if prob > 0.5 else 0)
   except KeyError:
       continue

if len(y_pred_probs_test) > 0:
   log_loss_value_test = log_loss(y_true_test[:len(y_pred_probs_test)], y_pred_probs_test)
   accuracy_test = accuracy_score(y_true_test[:len(y_pred_test)], y_pred_test)
   f1_test = f1_score(y_true_test[:len(y_pred_test)], y_pred_test)

   print("\nTest Set Metrics:")
   print("Log Loss:", log_loss_value_test)
   print("Accuracy:", accuracy_test)
   print("F1 Score:", f1_test)
else:
   print("No valid predictions for the test set.")
plot_structure(best_model)