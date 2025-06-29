import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import make_pipeline
from xgboost import XGBClassifier
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load and combine data (adjust paths as needed)
try:
    kaggle_data = pd.read_csv('credit_risk.csv')
    german_data = pd.read_csv('german_credit.csv')
    
    # Preprocess Kaggle data (adjust column names as needed)
    kaggle_data['target'] = kaggle_data['loan_status'].apply(lambda x: 1 if x == 'default' else 0)
    kaggle_processed = kaggle_data[['income', 'age', 'loan_amount', 'credit_score', 'target']]
    
    # Preprocess German data
    german_processed = german_data.rename(columns={
        'Class': 'target',
        'Duration': 'loan_duration',
        'Amount': 'loan_amount'
    })
    german_processed['target'] = german_processed['target'].replace({2: 1, 1: 0})  # Convert to 0/1
    
    # Combine datasets (use common features)
    combined_data = pd.concat([kaggle_processed, german_processed], axis=0)
except Exception as e:
    print(f"Error loading data: {e}")
    # Create sample data if files not found
    print("Creating sample data for demo purposes")
    np.random.seed(42)
    combined_data = pd.DataFrame({
        'income': np.random.normal(50000, 15000, 1000),
        'age': np.random.randint(20, 70, 1000),
        'loan_amount': np.random.randint(1000, 50000, 1000),
        'credit_score': np.random.randint(300, 850, 1000),
        'target': np.random.choice([0, 1], 1000, p=[0.8, 0.2])
    })

# 2. Feature engineering
combined_data['debt_to_income'] = combined_data['loan_amount'] / combined_data['income']
combined_data['credit_utilization'] = np.random.uniform(0, 1, len(combined_data))  # Simulated

# 3. Split data
X = combined_data.drop('target', axis=1)
y = combined_data['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# 4. Preprocessing pipeline
numeric_features = ['income', 'age', 'loan_amount', 'credit_score', 'debt_to_income', 'credit_utilization']
numeric_transformer = Pipeline(steps=[
    ('scaler', StandardScaler())])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features)])

# 5. Model pipeline with SMOTE
model = make_pipeline(
    preprocessor,
    SMOTE(random_state=42),
    XGBClassifier(
        objective='binary:logistic',
        eval_metric='auc',
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=sum(y_train==0)/sum(y_train==1),
        random_state=42
    )
)

# 6. Quick hyperparameter tuning (limited due to time)
param_dist = {
    'xgbclassifier__max_depth': [3, 5, 7],
    'xgbclassifier__learning_rate': [0.01, 0.1, 0.2],
    'xgbclassifier__subsample': [0.7, 0.8, 0.9]
}

search = RandomizedSearchCV(
    model, param_distributions=param_dist,
    n_iter=5, scoring='roc_auc', cv=3, verbose=1, n_jobs=-1
)
search.fit(X_train, y_train)

# 7. Evaluation
best_model = search.best_estimator_
y_pred = best_model.predict(X_test)
y_proba = best_model.predict_proba(X_test)[:, 1]

print("\nBest Model Evaluation:")
print(classification_report(y_test, y_pred))
print(f"ROC AUC: {roc_auc_score(y_test, y_proba):.4f}")

# 8. Save model
joblib.dump(best_model, 'loan_model.joblib')
print("Model saved as 'loan_model.joblib'")

# 9. Quick visualization
plt.figure(figsize=(10, 6))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.savefig('confusion_matrix.png')
plt.close()  