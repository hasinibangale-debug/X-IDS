# Results Directory

This directory stores outputs generated across experimental runs, model training, evaluation phases, and explainability workflows in the **X-IDS** project.

---

## Directory Organization

```
results/
├── README.md              # This documentation file
├── models/                # Saved weights, trained checkpoints, and model parameters
│   └── .gitkeep
├── metrics/               # Numerical evaluations, classification reports, and benchmark tables
│   └── .gitkeep
├── figures/               # Static visualizations, loss curves, confusion matrices, and TSNE/UMAP plots
│   └── .gitkeep
└── explanations/          # Saliency maps, GNNExplainer subgraphs, and SHAP feature attributions
    └── .gitkeep
```

---

## Description of Subdirectories

### 1. `models/`
- Serialized machine learning models (e.g., scikit-learn `.joblib` / `.pkl` baseline models).
- Deep learning and Graph Neural Network checkpoints (e.g., PyTorch / PyG state dicts `.pt`, `.pth`).
- Preprocessor state artifacts (e.g., fitted Scalers, Encoders).

### 2. `metrics/`
- Formatted performance summary reports in JSON, CSV, and Markdown formats.
- Standard evaluation metrics:
  - Accuracy, Precision, Recall, Macro/Weighted F1-Score
  - False Positive Rate (FPR), False Alarm Rate (FAR)
  - Area Under the ROC Curve (ROC-AUC), Precision-Recall AUC (PR-AUC)
- Comparative benchmark tables contrasting baseline classifiers against GNN variants (GCN, GAT, GraphSAGE).

### 3. `figures/`
- High-resolution figures (PNG, SVG, PDF) suitable for research publication and presentation:
  - Training and validation loss/accuracy learning trajectories.
  - Multi-class Confusion Matrix heatmaps.
  - Receiver Operating Characteristic (ROC) and Precision-Recall (PR) curves.
  - t-SNE / UMAP 2D projections of node and graph embeddings.
  - Network communication topology visualizations.

### 4. `explanations/`
- Explainable AI (XAI) outputs:
  - SHAP summary beeswarm plots and waterfall charts for tabular baseline feature importance.
  - GNNExplainer and SubgraphX induced subgraph visualizations highlighting critical attack paths, influential nodes (IPs/hosts), and relevant edge attributes.
  - Quantitative fidelity and sparsity metrics evaluating explanation quality.

---

## Reproducibility Guidelines

- When logging experiment outputs, prepend or tag filenames with the timestamp or experiment identifier (e.g., `gat_cicids2017_seed42_metrics.json`).
- Ensure all random seeds (Python, NumPy, PyTorch) are fixed and logged alongside results.
