
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import joblib
import numpy as np

# Load the dataset
try:
    # The script is run from the root, so the path is relative to the root
    df = pd.read_csv('preprocessed_sample.csv')
except FileNotFoundError:
    print("Error: 'preprocessed_sample.csv' not found. Make sure the file is in the root directory.")
    exit()

# --- Data Preprocessing ---

# Drop rows with missing target values
df.dropna(subset=['Disposition'], inplace=True)

# Select features (X) and target (y)
features_to_drop = ['KepID', 'KOIName', 'Disposition', 'KeplerDisposition', 'DispositionScore']
X = df.drop(columns=features_to_drop)
y = df['Disposition']

# Handle potential non-numeric columns that should be numeric
for col in X.columns:
    if X[col].dtype == 'object':
        X[col] = pd.to_numeric(X[col], errors='coerce')

# Fill remaining NaN values with the mean of the column
# Using a loop to avoid potential issues with chained indexing
for col in X.columns:
    if X[col].isnull().any():
        X[col].fillna(X[col].mean(), inplace=True)

# Encode the categorical target variable
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

# --- Model Training ---

print("Training the RandomForestClassifier...")
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)
print("Model training complete.")

# --- Model Evaluation ---

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy:.4f}")

print("\nClassification Report:")
target_names = label_encoder.inverse_transform(np.unique(y_encoded))
print(classification_report(y_test, y_pred, target_names=target_names))

# --- Save the Model and Encoder ---

model_filename = 'exoplanet_model.joblib'
encoder_filename = 'label_encoder.joblib'
features_filename = 'feature_columns.joblib'

joblib.dump(model, model_filename)
joblib.dump(label_encoder, encoder_filename)
joblib.dump(X.columns.tolist(), features_filename)

print(f"\nModel saved to '{model_filename}'")
print(f"Label encoder saved to '{encoder_filename}'")
print(f"Feature columns saved to '{features_filename}'")
