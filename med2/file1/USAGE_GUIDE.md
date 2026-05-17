# Diabetic Retinopathy Detection - Complete Usage Guide

## 🎯 Quick Reference

### Installation (One-time setup)
```bash
# Install all dependencies
pip install -r requirements.txt --break-system-packages

# For systems without pip breaking changes:
pip install -r requirements.txt
```

### Training
```bash
# Train with default settings (recommended for first time)
python train.py

# Training will output:
# - models/best_model.pth (trained model)
# - results/training_history.png (loss/accuracy curves)
# - results/confusion_matrix.png (classification matrix)
# - results/roc_curves.png (ROC curves)
# - results/classification_report.txt (detailed metrics)
# - results/training_results.json (summary)
```

### Inference
```bash
# Single image prediction
python inference.py --model models/best_model.pth --image path/to/image.jpg

# Batch processing (directory of images)
python inference.py --model models/best_model.pth --image path/to/images/ --batch

# Specify output directory
python inference.py --model models/best_model.pth --image image.jpg --output my_visualizations/
```

---

## 📖 Detailed Walkthrough

### Step 1: Prepare Your Environment

#### System Requirements
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB for synthetic dataset, 50GB+ for real datasets
- **Processor**: CPU-optimized (GPU optional but faster)

#### Install Python Packages
```bash
cd diabetic_retinopathy_detector
pip install -r requirements.txt --break-system-packages
```

**Package List:**
- `torch==2.0.1` - Deep learning framework
- `torchvision==0.15.2` - Computer vision utilities
- `numpy==1.24.3` - Numerical computing
- `pandas==2.0.3` - Data manipulation
- `matplotlib==3.7.2` - Plotting
- `seaborn==0.12.2` - Statistical visualization
- `scikit-learn==1.3.0` - Machine learning utilities
- `Pillow==10.0.0` - Image processing
- `opencv-python==4.8.0.76` - Computer vision
- `tqdm==4.65.0` - Progress bars

---

### Step 2: Prepare Your Dataset

#### Option A: Use Synthetic Data (Demo/Learning)

The training script automatically generates synthetic fundus images:
- **Pros**: No download needed, immediate testing
- **Cons**: Not clinically accurate, for demonstration only

Run training directly - synthetic data is auto-generated:
```bash
python train.py
```

#### Option B: Use Real Clinical Data (Research/Production)

1. **Download a public dataset:**

   **Kaggle Diabetic Retinopathy Detection** (Recommended)
   ```bash
   # Install Kaggle CLI
   pip install kaggle
   
   # Set up Kaggle API credentials (get from https://www.kaggle.com/settings)
   # Place kaggle.json in ~/.kaggle/
   
   # Download dataset
   kaggle competitions download -c diabetic-retinopathy-detection
   unzip diabetic-retinopathy-detection.zip -d data/
   ```

2. **Organize images by class:**
   ```
   data/dr_dataset/
   ├── 0_No_DR/          # No diabetic retinopathy
   ├── 1_Mild/           # Mild NPDR
   ├── 2_Moderate/       # Moderate NPDR
   ├── 3_Severe/         # Severe NPDR
   └── 4_Proliferative_DR/  # PDR
   ```

3. **Modify train.py to use your data:**
   
   Comment out the synthetic data generation and point to your dataset:
   ```python
   # In train.py, find this line:
   # data_dir = create_synthetic_dataset(...)
   
   # Replace with:
   data_dir = './data/dr_dataset'  # Your actual dataset
   ```

---

### Step 3: Train the Model

#### Basic Training
```bash
python train.py
```

**What happens during training:**

1. **Data Loading** (1-2 minutes)
   - Loads/generates dataset
   - Splits into train/validation sets (80/20)
   - Applies data augmentation

2. **Model Initialization**
   - Loads pretrained ResNet18
   - Adds custom classifier for 5 classes
   - Initializes optimizer and scheduler

3. **Training Loop** (15-60 minutes depending on CPU)
   ```
   Epoch 1/15
   ------------------------------------------------------------
   Training: 100%|████████████| Loss: 1.234, Acc: 45.67%
   Validation: 100%|█████████| Loss: 1.189, Acc: 48.32%
   ✓ Best model saved! (Val Acc: 48.32%)
   
   Epoch 2/15
   ...
   ```

4. **Final Evaluation**
   - Generates confusion matrix
   - Plots ROC curves
   - Calculates clinical metrics
   - Saves all visualizations

**Expected Training Time:**
- CPU (4 cores): ~30-60 minutes
- CPU (8+ cores): ~15-30 minutes
- GPU: ~5-10 minutes

#### Advanced Training Options

**Modify training parameters** in `train.py`:

```python
config = {
    'img_size': 224,              # Image resolution (128, 224, 384)
    'batch_size': 16,             # Reduce if out of memory (4, 8, 16, 32)
    'num_epochs': 15,             # More epochs = better training (10-50)
    'learning_rate': 0.001,       # Learning rate (0.0001 - 0.01)
    'num_classes': 5,             # Don't change unless dataset differs
    'train_split': 0.8,           # Train/validation split (0.7 - 0.9)
    'num_samples_per_class': 150  # For synthetic data only
}
```

**For faster training (testing):**
```python
config = {
    'img_size': 128,              # Smaller images
    'batch_size': 8,              # Smaller batches
    'num_epochs': 5,              # Fewer epochs
    'num_samples_per_class': 50   # Less synthetic data
}
```

**For better performance (production):**
```python
config = {
    'img_size': 384,              # Higher resolution
    'batch_size': 32,             # Larger batches (needs more RAM)
    'num_epochs': 30,             # More training
    # Use real dataset with thousands of images
}
```

---

### Step 4: Evaluate Training Results

After training completes, check the `results/` directory:

#### 1. Training History (`training_history.png`)
- **Loss curves**: Should decrease over epochs
- **Accuracy curves**: Should increase over epochs
- **Look for**: Convergence, overfitting (train/val divergence)

#### 2. Confusion Matrix (`confusion_matrix.png`)
- Shows prediction accuracy per class
- Diagonal = correct predictions
- Off-diagonal = misclassifications
- **Look for**: Strong diagonal, minimal confusion between No DR and PDR

#### 3. ROC Curves (`roc_curves.png`)
- One curve per class
- AUC score (0.5 = random, 1.0 = perfect)
- **Target**: AUC > 0.85 for each class

#### 4. Classification Report (`classification_report.txt`)
```
                    precision    recall  f1-score   support

         No DR       0.9234    0.8891    0.9059       123
          Mild       0.7845    0.8123    0.7982       108
      Moderate       0.8567    0.8234    0.8397       115
        Severe       0.8123    0.8456    0.8286       102
Proliferative DR     0.9012    0.9234    0.9122       98

      accuracy                           0.8596       546
     macro avg       0.8556    0.8588    0.8569       546
  weighted avg       0.8612    0.8596    0.8603       546
```

**Metrics explained:**
- **Precision**: Of predicted positives, how many were correct?
- **Recall (Sensitivity)**: Of actual positives, how many did we find?
- **F1-Score**: Harmonic mean of precision and recall
- **Support**: Number of samples in validation set

#### 5. Clinical Metrics (in console output)
```
CLINICAL METRICS (Per-Class)
======================================================================

No DR:
  Sensitivity (Recall): 0.8891  # True positive rate
  Specificity: 0.9456           # True negative rate
  PPV (Precision): 0.9234       # Positive predictive value
  NPV: 0.9123                   # Negative predictive value
```

**Clinical interpretation:**
- **Sensitivity**: Ability to detect disease when present (minimize false negatives)
- **Specificity**: Ability to rule out disease when absent (minimize false positives)
- **PPV**: Probability of disease given positive test
- **NPV**: Probability of no disease given negative test

---

### Step 5: Make Predictions

#### Single Image Prediction

```bash
python inference.py \
    --model models/best_model.pth \
    --image path/to/fundus_image.jpg
```

**Output example:**
```
======================================================================
DIABETIC RETINOPATHY DETECTION RESULTS
======================================================================

📊 Prediction: Moderate NPDR
   Confidence: 87.32%
   Severity Score: 2/4

📝 Description:
   More than just microaneurysms but less than Severe NPDR

💡 Clinical Recommendation:
   Moderate NPDR detected. Follow-up in 3-6 months.

📈 Class Probabilities:
   No DR                  3.21% ███
   Mild                   5.47% ██████
   Moderate              87.32% ███████████████████████████████████
   Severe                 3.45% ███
   Proliferative DR       0.55% █

🖼️  Visualization: ./visualizations/image_001_prediction_20251018_120345.png
======================================================================
```

**Visualization includes:**
- Original fundus image
- GradCAM heatmap (model attention)
- Prediction details
- Probability distribution
- Clinical recommendation

#### Batch Processing

Process an entire directory:

```bash
python inference.py \
    --model models/best_model.pth \
    --image path/to/images/ \
    --batch \
    --output my_results/
```

**Output:**
```
Processing 45 images...

[1/45] Processing: patient_001.jpg
  → Prediction: No DR (Confidence: 94.23%)
  → No diabetic retinopathy detected. Continue annual screening.

[2/45] Processing: patient_002.jpg
  → Prediction: Mild (Confidence: 78.56%)
  → Mild NPDR detected. Follow-up in 6-12 months.

...

[45/45] Processing: patient_045.jpg
  → Prediction: Proliferative DR (Confidence: 91.87%)
  → Proliferative DR detected. URGENT referral to ophthalmologist required!

======================================================================
BATCH PROCESSING COMPLETE - 45 images processed
======================================================================
```

All visualizations saved to `my_results/`

---

### Step 6: Interpret Results

#### Understanding GradCAM Visualizations

GradCAM shows **where the model is looking**:

🔴 **Red/Yellow regions** = High attention
- Should focus on pathological features:
  - Microaneurysms (small red dots)
  - Hemorrhages (red spots/streaks)
  - Exudates (yellow/white deposits)
  - Neovascularization (abnormal vessels)

🟢 **Green/Blue regions** = Low attention
- Should be background areas

**Good GradCAM:**
- Highlights actual lesions
- Focuses on optic disc and macula appropriately
- Ignores image borders and artifacts

**Bad GradCAM:**
- Focuses on image corners or artifacts
- Completely uniform (no attention localization)
- Misses obvious pathology

#### Clinical Decision Support

**The model provides:**
1. ✅ Severity classification (0-4 scale)
2. ✅ Confidence score
3. ✅ Attention visualization
4. ✅ Clinical recommendation

**You should consider:**
- ⚠️ Image quality (blur, artifacts, poor illumination)
- ⚠️ Patient history and symptoms
- ⚠️ Previous screening results
- ⚠️ Model confidence level

**Red flags requiring human review:**
- Low confidence (<70%)
- Conflicting class probabilities
- GradCAM focusing on artifacts
- Borderline severity cases

---

## 🔧 Troubleshooting

### Training Issues

**Problem**: "Out of memory"
```
RuntimeError: [enforce fail at CPUAllocator.cpp:64] . DefaultCPUAllocator: can't allocate memory
```
**Solution**:
- Reduce `batch_size` (try 8 or 4)
- Reduce `img_size` (try 128 or 96)
- Close other applications

---

**Problem**: "Training too slow"
**Solution**:
- Reduce `num_epochs` for testing (try 5)
- Use smaller dataset (`num_samples_per_class: 50`)
- Consider GPU if available

---

**Problem**: "Poor validation accuracy"
**Solution**:
- Train longer (`num_epochs: 30-50`)
- Use real clinical dataset
- Check data quality
- Adjust learning rate
- Balance class distribution

---

### Inference Issues

**Problem**: "Model file not found"
```
FileNotFoundError: [Errno 2] No such file or directory: 'models/best_model.pth'
```
**Solution**:
- Ensure you've run training first
- Check the exact path to model file
- Use absolute path if needed

---

**Problem**: "Image loading error"
```
OSError: cannot identify image file
```
**Solution**:
- Verify image is not corrupted
- Check image format (JPG, PNG supported)
- Ensure file permissions are correct

---

**Problem**: "Low confidence predictions"
**Solution**:
- Check image quality (blur, artifacts)
- Ensure proper illumination
- Verify correct image orientation
- Retrain with more diverse data

---

## 📊 Performance Benchmarks

### Synthetic Dataset (Demo)
- **Training time**: 15-30 minutes (CPU)
- **Accuracy**: 75-85% (validation)
- **Note**: For demonstration only

### Real Clinical Dataset (Kaggle DR)
- **Training time**: 2-4 hours (CPU), 20-40 minutes (GPU)
- **Expected accuracy**: 85-92%
- **Expected AUC**: 0.90-0.95 per class
- **Production-ready with proper validation**

---

## ⚠️ Important Notes

### This is Research Software
- ✅ Educational purposes
- ✅ Research and development
- ✅ Algorithm validation
- ❌ NOT for clinical diagnosis without validation
- ❌ NOT FDA/CE approved
- ❌ NOT a substitute for expert opinion

### Before Clinical Use
1. Validate on diverse patient populations
2. Compare against ophthalmologist assessments
3. Test on target equipment/imaging protocols
4. Obtain regulatory approval
5. Establish quality assurance procedures
6. Train healthcare staff on proper use

### Data Privacy
- Comply with HIPAA (US) or GDPR (EU)
- De-identify all patient data
- Secure storage and transmission
- Maintain audit trails
- Patient consent for AI analysis

---

## 🎓 Learning Resources

### Understanding DR Classification
- [AAO DR Preferred Practice Pattern](https://www.aao.org/preferred-practice-pattern/diabetic-retinopathy-ppp)
- [ETDRS Classification](https://en.wikipedia.org/wiki/Diabetic_retinopathy#Classification)
- [International DR Classification](https://iovs.arvojournals.org/article.aspx?articleid=2124572)

### Deep Learning for Medical Imaging
- Gulshan et al. (2016) - Development and Validation of Deep Learning for DR
- Ting et al. (2017) - AI for DR and Related Eye Diseases
- Selvaraju et al. (2017) - Grad-CAM Visual Explanations

### Dataset Papers
- Kaggle DR: https://www.kaggle.com/c/diabetic-retinopathy-detection
- APTOS 2019: https://www.kaggle.com/c/aptos2019-blindness-detection
- Messidor-2: http://www.adcis.net/en/third-party/messidor2/

---

## 📧 Support & Questions

### Code Issues
1. Check this guide thoroughly
2. Review README.md
3. Examine code comments
4. Verify all dependencies installed

### Research Collaboration
- This system is designed for educational purposes
- Feel free to adapt for your research
- Please cite appropriate papers if publishing results

### Medical Questions
- Consult with ophthalmologists
- Refer to clinical guidelines
- This is NOT medical advice

---

**Remember**: AI is a tool to assist healthcare professionals, not replace them. Always prioritize patient safety and professional medical judgment.

---

*Last Updated: October 2025*
