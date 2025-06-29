from flask import Flask, request, render_template, jsonify
import pandas as pd
import joblib
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

# Debug: Print available files
import os
print("Current files:", os.listdir())

try:
    model = joblib.load('loan_model.joblib')
    print("✅ Model loaded successfully!")
    print(f"Model features: {model.feature_names_in_ if hasattr(model, 'feature_names_in_') else 'N/A'}")
except Exception as e:
    print(f"❌ Model loading failed: {str(e)}")
    raise

@app.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            print("\n📦 Received form data:", request.form)
            
            # Validate required fields
            required = ['income', 'age', 'loan_amount', 'credit_score']
            if not all(field in request.form for field in required):
                raise BadRequest("Missing required fields")
            
            # Convert inputs with validation
            input_data = {
                'income': float(request.form['income']),
                'age': float(request.form['age']),
                'loan_amount': float(request.form['loan_amount']),
                'credit_score': float(request.form['credit_score']),
                'debt_to_income': float(request.form['loan_amount']) / max(1, float(request.form['income'])),
                'credit_utilization': float(request.form.get('credit_utilization', 0.5))
            }
            print("🔢 Processed inputs:", input_data)
            
            # Create DataFrame matching training format
            input_df = pd.DataFrame([input_data])
            print("📊 Input DataFrame:", input_df)
            
            # Predict
            probability = model.predict_proba(input_df)[0][1]
            print(f"🎯 Prediction: {probability:.2f}")
            
            return jsonify({
                'prediction': float(probability),
                'risk': "High Risk" if probability > 0.5 else "Low Risk"
            })
            
        except Exception as e:
            print(f"🔥 Error: {str(e)}")
            return jsonify({'error': str(e)}), 400
    
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)