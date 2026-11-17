"""X-IDS Interactive Streamlit Dashboard.

Explainable AI-driven Network Intrusion Detection System using Graph Neural Networks.
This application provides visualization for network flow traffic, graph topologies,
detection performance benchmarks, and XAI feature attributions.
"""

import streamlit as st


def main() -> None:
    """Render the primary Streamlit dashboard application."""
    st.set_page_config(
        page_title="X-IDS Dashboard",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # ------------------ Sidebar Navigation ------------------
    st.sidebar.title("🛡️ X-IDS Control Center")
    st.sidebar.caption("Explainable Graph Neural Network Intrusion Detection")

    page = st.sidebar.radio(
        "Navigation Menu",
        options=[
            "Overview & Architecture",
            "Dataset & Flow Inspection",
            "Network Graph Topology",
            "Intrusion Detection Models",
            "Explainability (XAI) Insights"
        ],
        index=0
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("System Configuration")
    selected_dataset = st.sidebar.selectbox(
        "Active Benchmark Dataset",
        options=["CIC-IDS2017", "CSE-CIC-IDS2018", "UNSW-NB15", "Synthetic Demo"],
        index=0
    )
    selected_model = st.sidebar.selectbox(
        "Active Detection Model",
        options=["Graph Attention Network (GAT)", "Graph Convolutional Network (GCN)", "GraphSAGE", "Random Forest (Baseline)", "Tabular MLP"],
        index=0
    )
    st.sidebar.info(f"Loaded: `{selected_dataset}`\n\nModel: `{selected_model}`")

    # ------------------ Page Content ------------------
    if page == "Overview & Architecture":
        st.title("🛡️ X-IDS: Explainable AI-driven Network Intrusion Detection System")
        st.markdown(
            """
            Welcome to the **X-IDS** interactive dashboard. This research platform models network traffic
            flows as communication graphs and leverages **Graph Neural Networks (GNNs)** combined with
            **Explainable AI (XAI)** techniques to deliver accurate, interpretable intrusion detection.
            """
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="System Status", value="Ready", delta="Scaffold Active")
        with col2:
            st.metric(label="Monitored Endpoints", value="1,248 IPs", delta="+12 Active")
        with col3:
            st.metric(label="Active Graph Edges", value="14,892 Flows", delta="+310 / min")
        with col4:
            st.metric(label="Detection Accuracy", value="-- %", delta="Awaiting Train")

        st.markdown("---")
        st.subheader("System Architecture")
        st.markdown(
            """
            ```
            [ Raw Network Flows ] ──> [ Preprocessing & Scaling ] ──> [ Graph Construction ]
                                                                             │
               ┌─────────────────────────────────────────────────────────────┘
               ▼
            [ Graph Neural Network (GNN) ] ──> [ Anomaly Classification ] ──> [ Explainability Layer (XAI) ]
                                                                             ├── Saliency Subgraphs
                                                                             └── Flow Feature Attribution
            ```
            """
        )

    elif page == "Dataset & Flow Inspection":
        st.title("📊 Dataset & Flow Inspection")
        st.markdown("Explore raw and preprocessed network traffic flows, socket tuples, and protocol attributes.")
        st.info("TODO: Connect with `src/preprocessing.py` to stream preprocessed flow samples.")

        st.subheader("Sample Network Flow Attributes (Placeholder)")
        st.dataframe(
            {
                "Flow ID": ["192.168.1.10:443-10.0.0.5:52312", "192.168.1.15:80-10.0.0.8:53210"],
                "Src IP": ["192.168.1.10", "192.168.1.15"],
                "Dst IP": ["10.0.0.5", "10.0.0.8"],
                "Protocol": ["TCP", "TCP"],
                "Duration (ms)": [124.5, 45.2],
                "Total Packets": [14, 6],
                "Total Bytes": [2450, 480],
                "Label": ["Benign", "DoS-SynFlood (Suspect)"]
            },
            use_container_width=True
        )

    elif page == "Network Graph Topology":
        st.title("🕸️ Network Graph Topology Visualizer")
        st.markdown("Interactive topological representation of host communications and flow interactions.")
        st.info("TODO: Connect with `src/graph_builder.py` and PyTorch Geometric graph data.")

        st.subheader("Graph Statistics Overview")
        col_g1, col_g2, col_g3 = st.columns(3)
        col_g1.metric("Graph Nodes (|V|)", "1,248")
        col_g2.metric("Graph Edges (|E|)", "14,892")
        col_g3.metric("Graph Density", "0.0095")

    elif page == "Intrusion Detection Models":
        st.title("⚡ Intrusion Detection Benchmark")
        st.markdown("Performance metrics comparing Graph Neural Networks against tabular baseline classifiers.")
        st.info("TODO: Populate with experiment metrics from `results/metrics/` and `src/evaluate.py`.")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.subheader("Model Benchmark (Target)")
            st.markdown(
                """
                | Model | Accuracy | Precision | Recall | F1-Score | FPR |
                |---|---|---|---|---|---|
                | **Random Forest (Baseline)** | -- | -- | -- | -- | -- |
                | **Tabular MLP** | -- | -- | -- | -- | -- |
                | **GCN** | -- | -- | -- | -- | -- |
                | **GAT (Proposed)** | -- | -- | -- | -- | -- |
                | **GraphSAGE** | -- | -- | -- | -- | -- |
                """
            )
        with col_m2:
            st.subheader("Confusion Matrix Placeholder")
            st.info("Confusion matrix heatmaps generated during evaluation will render here.")

    elif page == "Explainability (XAI) Insights":
        st.title("🔍 Explainability & Interpretability (XAI)")
        st.markdown(
            "Interpret GNN intrusion predictions by analyzing influential communication subgraphs, "
            "critical neighbor nodes, and salient flow attributes via GNNExplainer / SHAP."
        )
        st.info("TODO: Connect with `notebooks/06_explainability.ipynb` and `results/explanations/`.")

        st.subheader("Feature Importance & Saliency Attribution")
        st.write("Top influential flow features identified by the explainability module will appear here.")


if __name__ == "__main__":
    main()
