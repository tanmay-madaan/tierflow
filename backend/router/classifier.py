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
    def __init__(self, model_dir=None):
        if model_dir is None:
            try:
                from config import MODEL_DIR
                self.model_dir = Path(MODEL_DIR).resolve()
            except ImportError:
                self.model_dir = (Path(__file__).resolve().parent.parent / 'trained_models').resolve()
        else:
            self.model_dir = Path(model_dir).resolve()

        self.model = None
        self.vectorizer = None
        self.scaler = None
        self.metrics = {}
        self.fe = FeatureExtractor()
        self._load_model()

    def _load_model(self):
        # Reset all artifacts for atomic consistency
        self.model = None
        self.vectorizer = None
        self.scaler = None
        self.metrics = {}

        model_path = self.model_dir / 'model.pkl'
        vec_path = self.model_dir / 'vectorizer.pkl'
        scaler_path = self.model_dir / 'scaler.pkl'
        metrics_path = self.model_dir / 'metrics.json'

        # Validate that all required artifact files exist
        required_paths = [model_path, vec_path, scaler_path, metrics_path]
        missing = [f.name for f in required_paths if not f.exists()]
        if missing:
            print(f"[MLClassifier] Missing artifact files in {self.model_dir}: {missing}. Falling back to safe heuristic.")
            return

        try:
            m = joblib.load(model_path)
            v = joblib.load(vec_path)
            s = joblib.load(scaler_path)

            with open(metrics_path, 'r', encoding='utf-8') as f:
                metrics = json.load(f)

            # Validate that loaded estimators are fitted
            from sklearn.utils.validation import check_is_fitted
            check_is_fitted(m)
            check_is_fitted(v)
            check_is_fitted(s)

            # Explicit check for vectorizer idf_ attribute to catch cross-version unpickling divergence
            if not hasattr(v, 'idf_') or v.idf_ is None:
                raise ValueError("TfidfVectorizer loaded but idf_ vector is missing or not fitted")

            # All validations passed — assign state atomically
            self.model = m
            self.vectorizer = v
            self.scaler = s
            self.metrics = metrics
            print(f"[MLClassifier] Successfully verified and loaded model artifacts from {self.model_dir}")

        except Exception as e:
            print(f"[MLClassifier] Failed to load/verify model artifacts from {self.model_dir}: {e}. Falling back to safe heuristic.")
            self.model = None
            self.vectorizer = None
            self.scaler = None
            self.metrics = {}

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
            'accuracy': float(accuracy_score(labels, preds)),
            'precision': float(precision_score(labels, preds, average='macro')),
            'recall': float(recall_score(labels, preds, average='macro')),
            'f1': float(f1_score(labels, preds, average='macro')),
            'confusion_matrix': confusion_matrix(labels, preds).tolist(),
            'class_labels': self.model.classes_.tolist()
        }
        print("Training Metrics:", self.metrics)

        self.model_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_dir / 'model.pkl')
        joblib.dump(self.vectorizer, self.model_dir / 'vectorizer.pkl')
        joblib.dump(self.scaler, self.model_dir / 'scaler.pkl')
        with open(self.model_dir / 'metrics.json', 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2)

    def predict(self, query: str) -> dict:
        if self.model is None or self.vectorizer is None or self.scaler is None:
            # Fallback heuristic
            f = self.fe.extract(query)
            comp = f['estimated_complexity']
            model_map = {'LOW': 'SMALL', 'MODERATE': 'MEDIUM', 'HIGH': 'LARGE'}
            sel = model_map.get(comp, 'MEDIUM')
            return {'selected_model': sel, 'confidence': 0.6, 'probabilities': {sel: 0.6}}

        try:
            X_text = self.vectorizer.transform([query])
            X_num = self._extract_numerical([query])
            X_num_scaled = self.scaler.transform(X_num)
            X_combined = sp.hstack((X_text, X_num_scaled))

            probs = self.model.predict_proba(X_combined)[0]
            classes = self.model.classes_
            
            prob_dict = {classes[i]: float(probs[i]) for i in range(len(classes))}
            selected_model = classes[np.argmax(probs)]
            confidence = float(np.max(probs))

            return {
                'selected_model': selected_model,
                'confidence': confidence,
                'probabilities': prob_dict
            }
        except Exception as e:
            print(f"[MLClassifier] Runtime prediction error: {e}. Falling back to safe heuristic.")
            f = self.fe.extract(query)
            comp = f['estimated_complexity']
            model_map = {'LOW': 'SMALL', 'MODERATE': 'MEDIUM', 'HIGH': 'LARGE'}
            sel = model_map.get(comp, 'MEDIUM')
            return {'selected_model': sel, 'confidence': 0.6, 'probabilities': {sel: 0.6}}

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
