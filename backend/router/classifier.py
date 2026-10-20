import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import scipy.sparse as sp
import joblib
from pathlib import Path
from router.feature_extractor import FeatureExtractor
import json

class MLClassifier:
    def __init__(self, model_dir='trained_models'):
        self.model_dir = Path(model_dir)
        self.model = None
        self.vectorizer = None
        self.scaler = None
        self.metrics = {}
        self.fe = FeatureExtractor()
        self._load_model()

    def _load_model(self):
        try:
            if (self.model_dir / 'model.pkl').exists():
                self.model = joblib.load(self.model_dir / 'model.pkl')
                self.vectorizer = joblib.load(self.model_dir / 'vectorizer.pkl')
                self.scaler = joblib.load(self.model_dir / 'scaler.pkl')
                with open(self.model_dir / 'metrics.json', 'r') as f:
                    self.metrics = json.load(f)
        except Exception as e:
            print(f"Could not load model: {e}")
            self.model = None

    def _extract_numerical(self, queries):
        features = []
        for q in queries:
            f = self.fe.extract(q)
            features.append([
                f['query_length'], f['word_count'], f['sentence_count'],
                f['has_math_keywords'], f['has_code_keywords'],
                f['has_reasoning_keywords'], f['num_constraints'],
                f['has_multi_step']
            ])
        return np.array(features)

    def train(self, data_path='data/queries.csv'):
        df = pd.read_csv(data_path)
        queries = df['query'].values
        labels = df['model'].values

        self.vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1,2))
        X_text = self.vectorizer.fit_transform(queries)

        X_num = self._extract_numerical(queries)
        self.scaler = StandardScaler()
        X_num_scaled = self.scaler.fit_transform(X_num)

        X_combined = sp.hstack((X_text, X_num_scaled))

        self.model = LogisticRegression(max_iter=1000, multi_class='multinomial')
        self.model.fit(X_combined, labels)

        preds = self.model.predict(X_combined)
        
        self.metrics = {
            'accuracy': accuracy_score(labels, preds),
            'precision': precision_score(labels, preds, average='macro'),
            'recall': recall_score(labels, preds, average='macro'),
            'f1': f1_score(labels, preds, average='macro'),
            'confusion_matrix': confusion_matrix(labels, preds).tolist(),
            'class_labels': self.model.classes_.tolist()
        }
        print("Training Metrics:", self.metrics)

        self.model_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_dir / 'model.pkl')
        joblib.dump(self.vectorizer, self.model_dir / 'vectorizer.pkl')
        joblib.dump(self.scaler, self.model_dir / 'scaler.pkl')
        with open(self.model_dir / 'metrics.json', 'w') as f:
            json.dump(self.metrics, f)

    def predict(self, query: str) -> dict:
        if self.model is None:
            # Fallback heuristic
            f = self.fe.extract(query)
            comp = f['estimated_complexity']
            model_map = {'LOW': 'SMALL', 'MODERATE': 'MEDIUM', 'HIGH': 'LARGE'}
            sel = model_map[comp]
            return {'selected_model': sel, 'confidence': 0.6, 'probabilities': {sel: 0.6}}

        X_text = self.vectorizer.transform([query])
        X_num = self._extract_numerical([query])
        X_num_scaled = self.scaler.transform(X_num)
        X_combined = sp.hstack((X_text, X_num_scaled))

        probs = self.model.predict_proba(X_combined)[0]
        classes = self.model.classes_
        
        prob_dict = {classes[i]: probs[i] for i in range(len(classes))}
        selected_model = classes[np.argmax(probs)]
        confidence = float(np.max(probs))

        return {
            'selected_model': selected_model,
            'confidence': confidence,
            'probabilities': prob_dict
        }

    def get_metrics(self) -> dict:
        """
        Returns the metrics stored in trained_models/metrics.json.

        IMPORTANT: After running train.py (which calls evaluate.py --save-model),
        these will be HELD-OUT TEST SET metrics from a 70/15/15 stratified split.
        Before that, the file contained IN-SAMPLE training metrics (~94.8% accuracy)
        which should NOT be interpreted as generalisation performance.

        Check the '_note' key in the returned dict to confirm which type of metrics
        are loaded.
        """
        return self.metrics
