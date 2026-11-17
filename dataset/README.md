# Dataset Directory

This directory is designated for storing raw and processed network traffic datasets used in the **X-IDS (Explainable AI-driven Network Intrusion Detection System)** research project.

> **Note:** Raw dataset files (such as large CSVs, PCAPs, and Parquet files) must **not** be committed to version control. Ensure all large data files are excluded via `.gitignore`.

---

## Directory Organization

```
dataset/
├── README.md              # This documentation file
├── raw/                   # Unmodified raw benchmark datasets (downloaded externally)
│   └── .gitkeep
└── processed/             # Cleaned, normalized, and preprocessed feature sets
    └── .gitkeep
```

---

## Supported & Benchmark Datasets

The project is designed to benchmark against industry-standard network intrusion detection datasets, including:

1. **CIC-IDS2017 / CSE-CIC-IDS2018**
   - *Source:* Canadian Institute for Cybersecurity (UNB)
   - *Characteristics:* Realistic network traffic containing benign activity alongside common multi-stage attacks (e.g., DoS/DDoS, Brute Force, PortScan, Web Attacks, Infiltration, Botnets).
2. **UNSW-NB15**
   - *Source:* University of New South Wales / Cyber Range Lab
   - *Characteristics:* Comprehensive modern network traffic flows with 49 features including statistical and content characteristics across 9 attack families.
3. **NSL-KDD / KDD Cup 99** *(for legacy baseline comparison)*
   - *Source:* University of New Brunswick

---

## Expected Data Format & Schema

Raw flow records should be placed in `dataset/raw/` in **CSV** or **Parquet** format.

### Key Expected Feature Fields

| Category | Example Column Names | Description |
|---|---|---|
| **Flow Identifiers** | `src_ip`, `dst_ip`, `src_port`, `dst_port`, `protocol` | 5-tuple socket information identifying endpoints and transmission protocols |
| **Temporal Attributes** | `timestamp`, `flow_duration` | Start time, time window, and duration of the network connection |
| **Volume & Traffic Metrics** | `total_fwd_packets`, `total_bwd_packets`, `total_len_fwd_packets`, `total_len_bwd_packets` | Aggregated count of transmitted packets and payload byte volumes |
| **Statistical Dynamics** | `flow_bytes_s`, `flow_packets_s`, `packet_length_mean`, `packet_length_std`, `flow_iat_mean` | Inter-arrival times (IAT), statistical dispersion of packet sizes, throughput |
| **TCP Flag Counts** | `fin_flag_count`, `syn_flag_count`, `rst_flag_count`, `psh_flag_count`, `ack_flag_count` | Distribution of TCP control flags indicating connection states and port scans |
| **Ground-Truth Label** | `label`, `attack_category` | Binary classification (`Benign` vs. `Malicious`) or multiclass attack taxonomic labels |

---

## Data Ingestion Steps

1. Download the target dataset from its respective academic repository.
2. Place raw files into `dataset/raw/<dataset_name>/`.
3. Run `notebooks/02_preprocessing.ipynb` or execute `src/preprocessing.py` to generate normalized and partitioned artifacts into `dataset/processed/`.
