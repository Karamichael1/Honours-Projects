import pandas as pd
from pgmpy.estimators import HillClimbSearch,BayesianEstimator,BicScore
from pgmpy.models import BayesianModel,BayesianNetwork
from pgmpy.inference import VariableElimination
from ucimlrepo import fetch_ucirepo
import matplotlib.pyplot as plt
import networkx as nx
from daft import PGM
import daft

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
# fetch dataset 
adult = fetch_ucirepo(id=2) 
# data (as pandas dataframes) 
X = adult.data.features 
y = adult.data.targets 


# Discretize the features using quantile-based discretization
num_bins = 5  # Number of bins for discretization
discretize_vars = ['hours-per-week', 'capital-loss', 'capital-gain', 'age', 'fnlwgt', 'education-num']
X_discretized = X.copy()
for col in discretize_vars:
    X_discretized[col] = pd.cut(X[col], 5, labels=False)
data = pd.concat([X_discretized, y], axis=1)
data['income'] = data['income'].str.strip('.')
# Learn Bayesian network structure using Hill Climb Search
est = HillClimbSearch(data)
best_model = est.estimate(scoring_method=BicScore(data))
# Print learned Bayesian network structure
print("Learned Bayesian network structure:")
BayesNet=BayesianNetwork(best_model.edges())
# Create CPTs for the Bayesian network
BayesNet.fit(data)
print(best_model.nodes())
# Print CPTs
print("\nConditional Probability Tables (CPTs):")
#for cpd in BayesNet.get_cpds():
    #print(cpd)

# Perform exact inference using variable elimination
inference = VariableElimination(BayesNet)

# Example evidence (replace with your desired feature values)
evidence = {'age': 1}

# Perform inference on the 'target' variable given the evidence
query = inference.query(['income'], evidence=evidence)
print("\nInference result:")
print(query)
plot_structure(best_model)
