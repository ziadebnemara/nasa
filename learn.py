from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import pandas as pd
import os
import json
from datetime import datetime
import sqlite3

app = Flask(__name__)
CORS(app)

# Load the trained model
model = None
try:
    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print(f"Model loaded from {model_path}: {type(model)}")
except Exception as e:
    print(f"Error loading model from {model_path}: {e}")
    model = None

# Explicitly set feature names from your CSV header
feature_names = [
    'period',
    'duration',
    'depth',
    'planet_radius',
    'stellar_temperature',
    'stellar_gravity',
    'stellar_radius',
    'magnitude',
    'snr',
    'equilibrium_temp'
]

# Map numeric model outputs to human-friendly labels
PREDICTION_LABELS = {
    1: 'exoplanet',
    2: 'candidate of exoplanet',
    0: 'not an exoplanet'
}

# Initialize feedback database
def init_feedback_db():
    """Initialize SQLite database for storing user feedback"""
    db_path = os.path.join(os.path.dirname(__file__), 'feedback.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT NOT NULL,
                  features TEXT NOT NULL,
                  model_prediction INTEGER NOT NULL,
                  prediction_label TEXT NOT NULL,
                  user_provided_label TEXT NOT NULL,
                  verified INTEGER DEFAULT 1)''')
    conn.commit()
    conn.close()
    print(f"Feedback database initialized at {db_path}")

def store_feedback(features_dict, prediction, prediction_label, user_label):
    """Store user feedback in database for future model retraining"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'feedback.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO feedback 
                     (timestamp, features, model_prediction, prediction_label, user_provided_label, verified)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (datetime.now().isoformat(),
                   json.dumps(features_dict),
                   int(prediction),
                   prediction_label,
                   user_label.upper(),
                   1))
        
        conn.commit()
        conn.close()
        print(f"✅ Feedback stored: Model predicted '{prediction_label}', User confirmed '{user_label}'")
        return True
    except Exception as e:
        print(f"❌ Error storing feedback: {e}")
        return False

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded!'}), 500

    input_data = request.json
    print("Received input:", input_data)
    
    # Extract optional known_disposition from user
    known_disposition = input_data.get('known_disposition', None)
    
    # Determine expected features
    try:
        model_features = getattr(model, 'feature_names_in_', None)
        if model_features is not None:
            expected_features = [str(x) for x in model_features]
        else:
            expected_features = feature_names
    except Exception:
        expected_features = feature_names

    # Build the input row in the same order as expected_features
    features_dict = {name: input_data.get(name, 0) for name in expected_features}
    data_row = [features_dict[name] for name in expected_features]
    
    try:
        df_input = pd.DataFrame([data_row], columns=expected_features)
        df_input = df_input.apply(pd.to_numeric, errors='ignore').fillna(0)
        
        # Make prediction
        prediction = model.predict(df_input)[0]
        
        # Normalize prediction to Python int
        try:
            pred_int = int(prediction)
        except Exception:
            try:
                pred_int = int(prediction.item())
            except Exception:
                pred_int = prediction

        label = PREDICTION_LABELS.get(pred_int, str(pred_int))
        
        # Store feedback if user provided known disposition
        if known_disposition and known_disposition.strip():
            store_feedback(features_dict, pred_int, label, known_disposition.strip())
        
        return jsonify({
            'prediction': pred_int, 
            'label': label,
            'feedback_stored': bool(known_disposition and known_disposition.strip())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/feedback/stats', methods=['GET'])
def get_feedback_stats():
    """Get statistics about collected feedback"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'feedback.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Total feedback count
        c.execute('SELECT COUNT(*) FROM feedback')
        total_count = c.fetchone()[0]
        
        # Count by user-provided labels
        c.execute('SELECT user_provided_label, COUNT(*) FROM feedback GROUP BY user_provided_label')
        label_counts = dict(c.fetchall())
        
        # Count where model was correct
        c.execute('''SELECT COUNT(*) FROM feedback 
                     WHERE UPPER(prediction_label) = UPPER(user_provided_label)''')
        correct_count = c.fetchone()[0]
        
        conn.close()
        
        accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
        
        return jsonify({
            'total_feedback': total_count,
            'label_distribution': label_counts,
            'model_accuracy_on_feedback': round(accuracy, 2),
            'correct_predictions': correct_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/feedback/export', methods=['GET'])
def export_feedback():
    """Export all feedback data for model retraining"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'feedback.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        c.execute('SELECT * FROM feedback')
        rows = c.fetchall()
        
        feedback_data = []
        for row in rows:
            feedback_data.append({
                'id': row[0],
                'timestamp': row[1],
                'features': json.loads(row[2]),
                'model_prediction': row[3],
                'prediction_label': row[4],
                'user_provided_label': row[5],
                'verified': row[6]
            })
        
        conn.close()
        
        return jsonify({
            'count': len(feedback_data),
            'data': feedback_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Initialize database on startup
    init_feedback_db()
    app.run(debug=True)