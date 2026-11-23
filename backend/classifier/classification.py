
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "training_data.csv"

_cached_model = None


# --------------------------------------------------
# LOAD AND VALIDATE DATASET
# --------------------------------------------------

def load_dataset(dataset_path=DATASET_PATH):
    df = pd.read_csv(dataset_path)

    required_columns = {"text", "label"}

    if not required_columns.issubset(df.columns):
        raise ValueError(
            "Training dataset must contain 'text' and 'label' columns."
        )

    df = df.dropna(subset=["text", "label"]).copy()

    df["text"] = df["text"].astype(str).str.strip()
    df["label"] = df["label"].astype(str).str.strip().str.lower()

    df = df[
        (df["text"] != "") &
        (df["label"] != "")
    ]

    if df.empty:
        raise ValueError("Training dataset contains no valid records.")

    class_counts = df["label"].value_counts()

    if (class_counts < 2).any():
        raise ValueError(
            "Every category needs at least 2 training examples.\n"
            f"Insufficient categories:\n{class_counts[class_counts < 2]}"
        )

    return df


# --------------------------------------------------
# BUILD AND TRAIN PIPELINE
# --------------------------------------------------

def build_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("classifier", LogisticRegression())
    ])


def train_classifier(dataset_path=DATASET_PATH):
    df = load_dataset(dataset_path)

    x = df["text"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    clf = build_pipeline()
    clf.fit(X_train, y_train)

    return clf, (X_test, y_test)


# --------------------------------------------------
# LAZY MODEL LOADING
# --------------------------------------------------

def get_model():
    global _cached_model

    if _cached_model is None:
        _cached_model, _ = train_classifier()

    return _cached_model


def __getattr__(name):
    if name == "model":
        return get_model()

    raise AttributeError(
        f"module '{__name__}' has no attribute '{name}'"
    )


# --------------------------------------------------
# CLASSIFICATION
# --------------------------------------------------

def classify_document(text):
    if not isinstance(text, str) or not text.strip():
        return "other"

    clf = get_model()
    predicted_category = clf.predict([text])[0]

    return predicted_category


# --------------------------------------------------
# PREDICTION DETAILS
# --------------------------------------------------

def predict_document(text):
    if not isinstance(text, str) or not text.strip():
        return {
            "category": "other",
            "confidence": 0.0,
            "probabilities": {}
        }

    clf = get_model()
    probabilities = clf.predict_proba([text])[0]

    best_index = probabilities.argmax()

    predicted_category = clf.classes_[best_index]
    confidence = float(probabilities[best_index])

    probability_details = {
        category: round(float(probability), 4)
        for category, probability in zip(
            clf.classes_,
            probabilities
        )
    }

    return {
        "category": predicted_category,
        "confidence": round(confidence, 4),
        "probabilities": probability_details
    }


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":
    clf, (X_test, y_test) = train_classifier()

    predictions = clf.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    print(f"Classifier accuracy: {accuracy:.2f}")

    print("\nAvailable categories:")

    for category in clf.classes_:
        print(f"- {category}")
