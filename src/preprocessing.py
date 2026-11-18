
"""
X-IDS: CIC-IDS2017 Data Preprocessing

Reproducible preprocessing pipeline for the GeneratedLabelledFlows
subset of CIC-IDS2017.
"""

import os
import gc
import json
import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "generated_labelled_flows"
    / "TrafficLabelling "
)

PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

CHECKPOINT_DIR = PROCESSED_DIR / "checkpoints"
SOURCE_PARQUET_DIR = CHECKPOINT_DIR / "source_parquet"


# --------------------------------------------------
# PREPROCESSING CONFIGURATION
# --------------------------------------------------

CHUNK_SIZE = 50000
RANDOM_STATE = 42

INVALID_FEATURE_COLUMNS = [
    "Flow Duration",
    "Flow Packets/s",
    "Flow IAT Min",
    "Flow IAT Mean",
    "Flow IAT Max",
    "Flow Bytes/s",
    "Fwd IAT Min",
    "Fwd Header Length",
    "Bwd Header Length",
    "min_seg_size_forward"
]

CONSTANT_COLUMNS = [
    "Bwd PSH Flags",
    "Bwd URG Flags",
    "Fwd Avg Bytes/Bulk",
    "Fwd Avg Packets/Bulk",
    "Fwd Avg Bulk Rate",
    "Bwd Avg Bytes/Bulk",
    "Bwd Avg Packets/Bulk",
    "Bwd Avg Bulk Rate"
]

DUPLICATE_FEATURES = [
    "SYN Flag Count",
    "CWE Flag Count",
    "Subflow Fwd Packets",
    "Subflow Bwd Packets"
]

METADATA_COLUMNS = [
    "Flow ID",
    "Source IP",
    "Source Port",
    "Destination IP",
    "Destination Port",
    "Protocol",
    "Timestamp",
    "Label",
    "Capture_Date"
]


# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# CSV TO PARQUET CONVERSION
# --------------------------------------------------

def convert_csvs_to_parquet():
    """Convert raw CIC-IDS2017 CSV files into Parquet checkpoints."""

    SOURCE_PARQUET_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(RAW_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in: {RAW_DIR}"
        )

    logger.info("Found %d CSV files.", len(csv_files))

    for csv_file in csv_files:

        parquet_file = SOURCE_PARQUET_DIR / (
            csv_file.stem + ".parquet"
        )

        if parquet_file.exists():
            logger.info(
                "Checkpoint already exists. Skipping: %s",
                parquet_file.name
            )
            continue

        logger.info("Processing: %s", csv_file.name)

        chunks = []

        for chunk in pd.read_csv(
            csv_file,
            encoding="cp1252",
            low_memory=False,
            chunksize=CHUNK_SIZE
        ):
            chunk = chunk.dropna(how="all")

            if not chunk.empty:
                chunks.append(chunk)

        if not chunks:
            logger.warning(
                "No usable records in %s",
                csv_file.name
            )
            continue

        file_df = pd.concat(
            chunks,
            ignore_index=True
        )

        file_df.to_parquet(
            parquet_file,
            index=False
        )

        logger.info(
            "Saved %s with %s rows.",
            parquet_file.name,
            len(file_df)
        )

        del chunks, file_df
        gc.collect()

    logger.info("CSV conversion completed.")


# --------------------------------------------------
# LOAD AND COMBINE PARQUET FILES
# --------------------------------------------------

def load_and_combine_parquet():
    """Load all source Parquet files and combine them."""

    parquet_files = sorted(
        SOURCE_PARQUET_DIR.glob("*.parquet")
    )

    if not parquet_files:
        raise FileNotFoundError(
            "No Parquet checkpoints found. "
            "Run CSV conversion first."
        )

    logger.info(
        "Found %d Parquet checkpoint files.",
        len(parquet_files)
    )

    dataframes = []

    for parquet_file in parquet_files:

        logger.info("Loading: %s", parquet_file.name)

        file_df = pd.read_parquet(parquet_file)

        dataframes.append(file_df)

        logger.info(
            "Loaded %s rows and %s columns.",
            len(file_df),
            len(file_df.columns)
        )

    df = pd.concat(
        dataframes,
        ignore_index=True
    )

    del dataframes
    gc.collect()

    logger.info(
        "Combined dataset shape: %s",
        df.shape
    )

    return df


# --------------------------------------------------
# DATA CLEANING
# --------------------------------------------------

def clean_data(df):
    """Clean CIC-IDS2017 flow records."""

    logger.info("Starting data cleaning.")

    # Standardize column names
    df.columns = df.columns.str.strip()

    # Replace infinite values with NaN
    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    # Remove constant columns
    existing_constant_columns = [
        col for col in CONSTANT_COLUMNS
        if col in df.columns
    ]

    df.drop(
        columns=existing_constant_columns,
        inplace=True
    )

    # Remove duplicate header column
    duplicate_header = "Fwd Header Length.1"

    if duplicate_header in df.columns:
        if df[duplicate_header].equals(
            df["Fwd Header Length"]
        ):
            df.drop(
                columns=[duplicate_header],
                inplace=True
            )

    # Parse timestamps
    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"],
        format="mixed",
        dayfirst=True,
        errors="coerce"
    )

    # Replace invalid negative measurements with NaN
    for col in INVALID_FEATURE_COLUMNS:
        if col in df.columns:
            df.loc[df[col] < 0, col] = np.nan

    # Remove exact duplicate feature columns
    duplicate_pairs = [
        ("SYN Flag Count", "Fwd PSH Flags"),
        ("CWE Flag Count", "Fwd URG Flags"),
        ("Subflow Fwd Packets", "Total Fwd Packets"),
        ("Subflow Bwd Packets", "Total Backward Packets")
    ]

    for duplicate_col, original_col in duplicate_pairs:

        if (
            duplicate_col in df.columns
            and original_col in df.columns
        ):
            if df[duplicate_col].equals(df[original_col]):
                df.drop(
                    columns=[duplicate_col],
                    inplace=True
                )

    # Remove exact duplicate records
    before_duplicates = len(df)

    df.drop_duplicates(
        keep="first",
        inplace=True
    )

    df.reset_index(
        drop=True,
        inplace=True
    )

    removed_duplicates = before_duplicates - len(df)

    # Add capture date for temporal analysis
    df["Capture_Date"] = df["Timestamp"].dt.date

    logger.info(
        "Removed %d duplicate records.",
        removed_duplicates
    )

    logger.info(
        "Cleaned dataset shape: %s",
        df.shape
    )

    logger.info(
        "Remaining missing values: %d",
        df.isna().sum().sum()
    )

    return df


# --------------------------------------------------
# SAVE CLEANED DATASET
# --------------------------------------------------

def save_cleaned_data(df):
    """Save the cleaned dataset as a Parquet file."""

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = PROCESSED_DIR / "cleaned_flows.parquet"

    df.to_parquet(
        output_path,
        index=False
    )

    logger.info(
        "Cleaned dataset saved to: %s",
        output_path
    )

    logger.info(
        "Saved dataset shape: %s",
        df.shape
    )

# --------------------------------------------------
# STRATIFIED DATA SPLITTING
# --------------------------------------------------

def split_data(df):
    """Split dataset into train, validation and test sets."""

    indices = np.arange(len(df))

    train_idx, temp_idx = train_test_split(
        indices,
        train_size=0.70,
        stratify=df["Label"],
        random_state=RANDOM_STATE
    )

    val_idx, test_idx = train_test_split(
        temp_idx,
        test_size=0.50,
        stratify=df["Label"].iloc[temp_idx],
        random_state=RANDOM_STATE
    )

    # Save split indices
    split_path = PROCESSED_DIR / "data_split_indices.npz"

    np.savez_compressed(
        split_path,
        train_idx=train_idx,
        val_idx=val_idx,
        test_idx=test_idx
    )

    train_df = df.iloc[train_idx].copy()
    val_df = df.iloc[val_idx].copy()
    test_df = df.iloc[test_idx].copy()

    logger.info("Data splitting completed.")

    logger.info("Training records: %d", len(train_df))
    logger.info("Validation records: %d", len(val_df))
    logger.info("Testing records: %d", len(test_df))

    return train_df, val_df, test_df


# --------------------------------------------------
# FEATURE EXTRACTION AND IMPUTATION
# --------------------------------------------------

def prepare_features(train_df, val_df, test_df):
    """Extract numerical features and impute missing values."""

    feature_columns = [
        col
        for col in train_df.select_dtypes(
            include=[np.number]
        ).columns
        if col not in METADATA_COLUMNS
    ]

    logger.info(
        "Number of selected features: %d",
        len(feature_columns)
    )

    # Separate features and labels
    X_train = train_df[feature_columns]
    X_val = val_df[feature_columns]
    X_test = test_df[feature_columns]

    y_train = train_df["Label"].astype(str).to_numpy()
    y_val = val_df["Label"].astype(str).to_numpy()
    y_test = test_df["Label"].astype(str).to_numpy()

    # Fit imputer only on training data
    imputer = SimpleImputer(strategy="median")

    X_train_imputed = imputer.fit_transform(X_train)
    X_val_imputed = imputer.transform(X_val)
    X_test_imputed = imputer.transform(X_test)

    logger.info("Median imputation completed.")

    logger.info(
        "Training features shape: %s",
        X_train_imputed.shape
    )

    logger.info(
        "Validation features shape: %s",
        X_val_imputed.shape
    )

    logger.info(
        "Testing features shape: %s",
        X_test_imputed.shape
    )

    return (
        X_train_imputed,
        X_val_imputed,
        X_test_imputed,
        y_train,
        y_val,
        y_test,
        imputer,
        feature_columns
    )

# --------------------------------------------------
# SAVE PROCESSED DATA
# --------------------------------------------------

def save_processed_data(
    X_train,
    X_val,
    X_test,
    y_train,
    y_val,
    y_test,
    imputer,
    feature_columns
):
    """Save processed arrays and preprocessing objects."""

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save feature arrays
    np.save(PROCESSED_DIR / "X_train.npy", X_train)
    np.save(PROCESSED_DIR / "X_val.npy", X_val)
    np.save(PROCESSED_DIR / "X_test.npy", X_test)

    # Save label arrays
    np.save(PROCESSED_DIR / "y_train.npy", y_train)
    np.save(PROCESSED_DIR / "y_val.npy", y_val)
    np.save(PROCESSED_DIR / "y_test.npy", y_test)

    # Save fitted imputer
    joblib.dump(
        imputer,
        PROCESSED_DIR / "median_imputer.joblib"
    )

    # Save selected feature names
    joblib.dump(
        feature_columns,
        PROCESSED_DIR / "feature_columns.joblib"
    )

    logger.info("Processed arrays and objects saved.")

    logger.info(
        "Processed data directory: %s",
        PROCESSED_DIR
    )

# --------------------------------------------------
# SAVE PREPROCESSING METADATA
# --------------------------------------------------

def save_metadata(df, feature_columns):
    """Save label mapping and preprocessing configuration."""

    # Create alphabetical label mapping
    labels = sorted(df["Label"].astype(str).unique())

    label_mapping = {
        label: index
        for index, label in enumerate(labels)
    }

    mapping_path = PROCESSED_DIR / "label_mapping.json"

    with open(mapping_path, "w", encoding="utf-8") as file:
        json.dump(
            label_mapping,
            file,
            indent=4,
            ensure_ascii=False
        )

    # Preprocessing configuration
    config = {
        "dataset": "CIC-IDS2017 GeneratedLabelledFlows",
        "total_records": int(len(df)),
        "total_classes": int(len(labels)),
        "total_features": int(len(feature_columns)),
        "feature_columns": feature_columns,
        "removed_constant_columns": CONSTANT_COLUMNS,
        "removed_duplicate_features": DUPLICATE_FEATURES,
        "invalid_negative_value_columns": INVALID_FEATURE_COLUMNS,
        "imputation_strategy": "median",
        "imputer_fit_on": "training_data_only",
        "split_ratios": {
            "train": 0.70,
            "validation": 0.15,
            "test": 0.15
        },
        "random_state": RANDOM_STATE
    }

    config_path = PROCESSED_DIR / "preprocessing_config.json"

    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(
            config,
            file,
            indent=4,
            ensure_ascii=False
        )

    logger.info("Label mapping and configuration saved.")

# --------------------------------------------------
# MAIN PREPROCESSING PIPELINE
# --------------------------------------------------

def main(convert_csv=False):
    """Run the complete preprocessing pipeline."""

    logger.info("=" * 60)
    logger.info("X-IDS DATA PREPROCESSING STARTED")
    logger.info("=" * 60)

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Step 1: Convert CSV files if explicitly requested
    if convert_csv:
        convert_csvs_to_parquet()

    # Step 2: Load and combine source data
    df = load_and_combine_parquet()

    # Step 3: Clean the dataset
    df = clean_data(df)

    # Step 4: Save cleaned dataset
    save_cleaned_data(df)

    # Step 5: Split the dataset
    train_df, val_df, test_df = split_data(df)

    # Step 6: Extract features and impute missing values
    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
        imputer,
        feature_columns
    ) = prepare_features(
        train_df,
        val_df,
        test_df
    )

    # Step 7: Save processed arrays and objects
    save_processed_data(
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
        imputer,
        feature_columns
    )

    # Step 8: Save metadata
    save_metadata(df, feature_columns)

    logger.info("=" * 60)
    logger.info("X-IDS DATA PREPROCESSING COMPLETED")
    logger.info("=" * 60)


# --------------------------------------------------
# SCRIPT ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="X-IDS CIC-IDS2017 preprocessing pipeline"
    )

    parser.add_argument(
        "--convert-csv",
        action="store_true",
        help="Convert raw CSV files into Parquet checkpoints"
    )

    args = parser.parse_args()

    main(convert_csv=args.convert_csv)
