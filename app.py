from flask import Flask, request, render_template, jsonify
import pandas as pd
import joblib
from werkzeug.exceptions import BadRequest
import os
import sys

app = Flask(__name__)

# Debug: Print environment info
print("Python version:", sys.version)
print("Current files:", os.listdir())

# Check package versions
try:
    import sklearn
    import numpy as np
    print(f"scikit-learn version: {sklearn.__version__}")
    print(f"numpy version: {np.__version__}")
except ImportError as e:
    print(f"Import error: {e}")

# Load model with enhanced error handling
try:
    model = joblib.load('loan_model.joblib')
    print("✅ Model loaded successfully!")
    if hasattr(model, 'feature_names_in_'):
        print(f"Model features: {model.feature_names_in_}")
    else:
        print("Model feature names not available")
except Exception as e:
    print(f"❌ Model loading failed: {str(e)}")
    raise RuntimeError(f"Failed to load model: {str(e)}") from e

@app.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            print("\n📦 Received form data:", request.form)
            
            # Required fields
            required = {
                'income': float,
                'age': float,
                'loan_amount': float,
                'credit_score': float
            }
            
            # Validate inputs
            input_data = {}
            for field, type_cast in required.items():
                if field not in request.form:
                    raise BadRequest(f"Missing required field: {field}")
                try:
                    input_data[field] = type_cast(request.form[field])
                except ValueError:
                    raise BadRequest(f"Invalid value for {field}")
            
            # Calculate derived fields
            input_data['debt_to_income'] = input_data['loan_amount'] / max(1, input_data['income'])
            input_data['credit_utilization'] = float(request.form.get('credit_utilization', 0.5))
            
            print("🔢 Processed inputs:", input_data)
            
            # Create DataFrame with expected feature order
            feature_order = ['income', 'age', 'loan_amount', 'credit_score', 
                           'debt_to_income', 'credit_utilization']
            input_df = pd.DataFrame([input_data])[feature_order]
            print("📊 Input DataFrame:", input_df)
            
            # Predict
            probability = model.predict_proba(input_df)[0][1]
            print(f"🎯 Prediction: {probability:.2f}")
            
            return jsonify({
                'prediction': float(probability),
                'risk': "High Risk" if probability > 0.5 else "Low Risk",
                'probability': f"{probability*100:.1f}%"
            })
            
        except BadRequest as e:
            print(f"🚨 Validation error: {str(e)}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            print(f"🔥 Unexpected error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

