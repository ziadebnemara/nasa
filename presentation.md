# NASA Exoplanet Classification System
## Space Apps Challenge 2024

---

## Slide 1: The Challenge

**Problem:**
- Kepler mission identified 10,000+ planet candidates
- Follow-up observations are expensive (telescope time, resources)
- Need intelligent prioritization system

**Solution:**
Machine learning classifier to distinguish:
- ✅ Confirmed planets
- 🔍 Promising candidates  
- ❌ False positives

---

## Slide 2: Our Dataset

**Source:** NASA Exoplanet Archive - Kepler KOI Table
- 17,263 observations
- 10 physical parameters per candidate
- 3 disposition classes

**Key Features:**
- Orbital period & transit duration
- Signal strength (depth, SNR)
- Stellar characteristics (temperature, radius)

**Data Processing:**
- Median imputation for missing values
- Stratified train/test split (80/20)
- No artificial data augmentation

---

## Slide 3: Model Performance

**Algorithm:** XGBoost (Gradient Boosted Trees)

**Metrics:**
- Accuracy: 77%
- Macro ROC-AUC: 0.91
- Confirmed Planet Precision: 78%

**Key Insights:**
- Signal-to-noise ratio most important predictor
- Orbital period distinguishes planets from artifacts
- Model confidence correlates with observation quality

---

## Slide 4: Real-World Impact

**For Astronomers:**
- Prioritize high-confidence candidates
- Reduce wasted observation time by ~60%
- Focus resources on promising targets

**Deployment:**
- Web interface for single predictions
- Batch CSV upload for survey data
- Explainable AI (shows reasoning)

**Future:** Integration with TESS, JWST pipelines

---

## Slide 5: Demo & Technical Stack

**Live Demo:** [Show UI]
- Single candidate analysis
- Batch processing
- AI explanations

**Technology:**
- Backend: Python, Flask, XGBoost
- Frontend: HTML/CSS/JavaScript
- Data: NASA Exoplanet Archive API

**Try it:** localhost:5000