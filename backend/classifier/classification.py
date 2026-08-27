import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer

BASE_DIR = Path(__file__).resolve().parent
df = pd.read_csv(BASE_DIR / "training_data.csv")

x = df["text"]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42, stratify=y
)

model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", LogisticRegression())
])

model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)

print(f"accuracy: {accuracy:.2f}")


def classify_document(text):
    return model.predict([text])[0]