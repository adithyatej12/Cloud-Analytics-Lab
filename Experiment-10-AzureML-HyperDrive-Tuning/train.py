"""Train a Random Forest classifier on student performance data.

Used by Experiment 10 (Azure ML HyperDrive tuning). HyperDrive calls this
script once per child run, passing a different hyperparameter combination
each time via the --n_estimators / --max_depth / --min_samples_split
arguments. The script logs the run's accuracy so HyperDrive can rank runs,
and saves the trained model to outputs/model.pkl.

It also runs standalone outside Azure ML: if no Azure ML run context is
available, accuracy is printed to stdout instead of being logged.

Usage (standalone):
    python train.py --data student_performance.csv
    python train.py --data student_performance.csv --n_estimators 200 --max_depth 10

Expected CSV columns: one or more score columns (names containing "score",
"marks", or "grade") and a "result" column with Pass/Fail values, as
produced by the Experiment 6 cleaning step (performance_band + result).
"""

import argparse
import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# Column-name fragments that identify the score (feature) columns.
SCORE_KEYWORDS = ("score", "marks", "grade")

TARGET_COLUMN = "result"


def find_score_columns(df):
    """Return the score columns, detected by name (adapts to the CSV layout)."""
    return [
        col
        for col in df.columns
        if any(keyword in col.lower() for keyword in SCORE_KEYWORDS)
    ]


def log_accuracy(accuracy):
    """Log accuracy to the Azure ML run, falling back to plain print.

    Run.get_context() returns the current run inside Azure ML. Outside
    Azure ML it raises (or returns a context with no logging), so the
    try/except keeps the script runnable standalone for local testing.
    """
    try:
        from azureml.core import Run

        run = Run.get_context()
        run.log("accuracy", accuracy)
    except Exception:
        print(f"accuracy: {accuracy}")


def main():
    parser = argparse.ArgumentParser(
        description="Train a Random Forest classifier on student performance data."
    )
    parser.add_argument(
        "--data",
        type=str,
        default="student_performance.csv",
        help="Path to the student performance CSV file.",
    )
    # Hyperparameters tuned by HyperDrive (one value per child run).
    parser.add_argument("--n_estimators", type=int, default=100)
    parser.add_argument("--max_depth", type=int, default=None)
    parser.add_argument("--min_samples_split", type=int, default=2)
    args = parser.parse_args()

    # Load data and pick out the features (score columns) and target.
    df = pd.read_csv(args.data)
    score_cols = find_score_columns(df)
    if not score_cols:
        raise ValueError(
            "No score columns found in the CSV (looked for column names "
            "containing 'score', 'marks', or 'grade')."
        )
    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Target column '{TARGET_COLUMN}' not found in the CSV. "
            "Expected the cleaned Experiment 6 output with a Pass/Fail result."
        )

    X = df[score_cols]
    y = df[TARGET_COLUMN]

    # Hold out 20% of the rows for evaluation (stratified to keep the
    # Pass/Fail balance the same in train and test).
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train with this run's hyperparameters.
    clf = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        min_samples_split=args.min_samples_split,
        random_state=42,
    )
    clf.fit(X_train, y_train)

    # Evaluate and log the accuracy HyperDrive ranks runs by.
    accuracy = accuracy_score(y_test, clf.predict(X_test))
    print(f"accuracy: {accuracy:.4f}")
    log_accuracy(accuracy)

    # Save the model. Azure ML automatically uploads everything under
    # outputs/ as a run artifact, so the best run's model.pkl is kept.
    os.makedirs("outputs", exist_ok=True)
    joblib.dump(clf, "outputs/model.pkl")
    print("Model saved to outputs/model.pkl")


if __name__ == "__main__":
    main()
