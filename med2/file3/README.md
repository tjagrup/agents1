# Medical Dataset for Diabetes & Hypertension Prediction

## Overview
This is a comprehensive synthetic medical dataset containing 5,000 patient records with 57 features designed for developing AI/ML models to predict and prevent diabetes and hypertension.

## Dataset Statistics
- **Total Patients**: 5,000
- **Total Features**: 57
- **Diabetes Prevalence**: 31.9%
- **Hypertension Prevalence**: 69.4%
- **Missing Data**: ~0.5% (realistic to medical data)

## Files Included

### 1. Main Dataset
- **`diabetes_hypertension_dataset.csv`** - The complete dataset with 5,000 patient records

### 2. Documentation
- **`data_dictionary.csv`** - Complete description of all columns, data types, and valid ranges
- **`dataset_preview.csv`** - Sample of first 5 records for quick review

### 3. Statistical Analysis
- **`dataset_statistical_summary.csv`** - Comprehensive statistical summary of all features
- **`feature_correlation_matrix.csv`** - Correlation matrix between all numerical features

### 4. Model Results
- **`model_results.xlsx`** - Machine learning model performance metrics and feature importance rankings

### 5. Python Scripts
- **`generate_medical_dataset.py`** - Script used to generate the synthetic dataset
- **`explore_dataset.py`** - Data exploration and analysis script
- **`ml_pipeline.py`** - Complete machine learning pipeline with multiple models

## Feature Categories

### Clinical Parameters
- **Laboratory Values**: HbA1c, fasting glucose, OGTT, lipid panels, kidney function tests
- **Vital Signs**: Blood pressure (multiple timepoints), heart rate variability, BMI trajectories
- **Medical History**: Family history, gestational diabetes, PCOS, metabolic syndrome

### Demographics & Lifestyle
- **Demographics**: Age, sex, ethnicity
- **Lifestyle**: Physical activity, diet quality, smoking, alcohol, sleep, stress
- **Socioeconomic**: Education, income, insurance, occupation, residence type

### Temporal Data
- **Longitudinal Measurements**: Historical values for HbA1c, glucose, BP, BMI
- **Healthcare Utilization**: Doctor visits, ER visits, hospitalizations
- **Medication Adherence**: Current medications and compliance rates

## Target Variables
- **`has_diabetes`**: Binary (1 = HbA1c ≥ 6.5%)
- **`has_hypertension`**: Binary (1 = BP ≥ 140/90 mmHg)
- **`diabetes_risk_score`**: Calculated risk score (0-100)
- **`hypertension_risk_score`**: Calculated risk score (0-100)

## Key Features of the Dataset

### Realistic Correlations
- BMI correlates with diabetes/hypertension risk
- Family history increases disease probability
- Age progression affects clinical parameters
- Lifestyle factors impact health outcomes

### Temporal Patterns
- 6-month history for key clinical markers
- 2-year BMI progression
- Medication adherence tracking

### Clinical Relevance
- Features based on established medical risk factors
- Ranges within realistic clinical parameters
- Missing data patterns similar to real EHR data

## Model Performance (Initial Testing)

### Diabetes Prediction
- **Random Forest AUC-ROC**: 1.000
- **Top Features**: HbA1c levels, family history, BMI

### Hypertension Prediction  
- **Random Forest AUC-ROC**: 1.000
- **Top Features**: Blood pressure readings, age, BMI

*Note: Perfect scores are due to synthetic data with built-in correlations. Real-world performance will be lower.*

## Usage Instructions

### Loading the Dataset
```python
import pandas as pd
df = pd.read_csv('diabetes_hypertension_dataset.csv')
```

### Basic Preprocessing
```python
# Handle missing values
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy='median')
df_imputed = pd.DataFrame(imputer.fit_transform(df.select_dtypes(include=['number'])))

# Encode categorical variables
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
for col in ['sex', 'ethnicity', 'smoking_status']:
    df[col + '_encoded'] = le.fit_transform(df[col])
```

### Train-Test Split
```python
from sklearn.model_selection import train_test_split

# Features and target
X = df.drop(['has_diabetes', 'has_hypertension', 'patient_id'], axis=1)
y_diabetes = df['has_diabetes']
y_hypertension = df['has_hypertension']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y_diabetes, test_size=0.2, random_state=42, stratify=y_diabetes
)
```

## Next Steps for Model Development

1. **Feature Engineering**
   - Create interaction features
   - Add temporal trend indicators
   - Calculate risk progression rates

2. **Advanced Models**
   - Implement LSTM for temporal patterns
   - Try XGBoost/LightGBM
   - Develop ensemble methods

3. **Clinical Validation**
   - Define clinical thresholds
   - Implement decision curve analysis
   - Create risk stratification protocols

4. **Deployment Considerations**
   - Add explainability (SHAP/LIME)
   - Implement drift detection
   - Create monitoring dashboards

## Limitations

This is synthetic data generated for demonstration purposes. While it maintains realistic correlations and distributions, it should not be used for actual clinical decision-making. Key limitations include:

- Perfect correlations between related features
- Simplified disease progression patterns
- No real patient outcomes
- Limited temporal complexity

## License & Usage

This synthetic dataset is provided for educational and research purposes. It can be freely used for:
- Model development and testing
- Educational demonstrations
- Research prototyping
- Technical interviews

## Contact

For questions about the dataset generation methodology or feature engineering approaches, please refer to the included Python scripts which contain detailed documentation of the data generation process.
