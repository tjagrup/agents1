# Diabetic Retinopathy Detection - Machine Learning Pipeline

A comprehensive deep learning system for automated detection and classification of diabetic retinopathy from fundus images. This research-grade implementation includes training, evaluation, and inference with full visualization capabilities.

## 🎯 Overview

This system performs **multi-class classification** of diabetic retinopathy severity:

- **Class 0**: No DR (No Diabetic Retinopathy)
- **Class 1**: Mild NPDR (Non-Proliferative Diabetic Retinopathy)
- **Class 2**: Moderate NPDR
- **Class 3**: Severe NPDR
- **Class 4**: Proliferative DR (PDR)

## 🌟 Key Features

### ✅ Complete Training Pipeline
- State-of-the-art ResNet18 architecture with custom classifier
- Data augmentation for improved generalization
- Learning rate scheduling
- Automatic model checkpointing (saves best model)
- Comprehensive logging and metrics tracking

### 📊 Evaluation Metrics
- **Classification Metrics**: Accuracy, Precision, Recall, F1-Score
- **Clinical Metrics**: Sensitivity, Specificity, PPV, NPV (per class)
- **ROC Curves**: AUC scores for each class
- **Confusion Matrix**: Detailed misclassification analysis

### 🔍 Visualization Tools
- **Training History**: Loss and accuracy curves
- **GradCAM**: Visual explanations showing where the model focuses
- **Attention Maps**: Heatmaps highlighting pathological features
- **Prediction Dashboard**: Comprehensive result visualization

### 🚀 Inference Interface
- Single image prediction
- Batch processing capability
- Real-time visualization
- Clinical recommendations based on severity
- Confidence scores and probability distributions

## 📁 Project Structure

```
diabetic_retinopathy_detector/
├── train.py                    # Complete training pipeline
├── inference.py                # Inference interface with GradCAM
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── data/                       # Dataset directory
│   └── synthetic_dr_dataset/   # Auto-generated synthetic data
├── models/                     # Saved model checkpoints
│   └── best_model.pth         # Best performing model
├── results/                    # Training results
│   ├── training_history.png   # Loss/accuracy plots
│   ├── confusion_matrix.png   # Classification confusion matrix
│   ├── roc_curves.png         # ROC curves for all classes
│   ├── classification_report.txt  # Detailed metrics
│   └── training_results.json  # Complete results summary
└── visualizations/             # Inference visualizations
    └── *_prediction_*.png     # Individual predictions with GradCAM
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- CPU-based system (optimized for CPU training)

### Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- PyTorch & TorchVision (CPU version)
- NumPy, Pandas
- Matplotlib, Seaborn
- Scikit-learn
- OpenCV, Pillow
- TQDM

## 📚 Dataset

### Option 1: Synthetic Dataset (Demo/Testing)
The training script automatically generates synthetic fundus images for demonstration. These images simulate retinal features but should **NOT** be used for clinical applications.

### Option 2: Real Clinical Datasets (Recommended for Research)

For serious research, use one of these public datasets:

1. **Kaggle Diabetic Retinopathy Detection**
   - 35,126 training images
   - 5 severity classes
   - Download: https://www.kaggle.com/c/diabetic-retinopathy-detection

2. **EyePACS Dataset**
   - Large-scale retinal image dataset
   - Used for real DR screening
   - Contact: https://www.eyepacs.com/

3. **APTOS 2019 Blindness Detection**
   - 3,662 fundus images
   - 5 DR severity grades
   - Download: https://www.kaggle.com/c/aptos2019-blindness-detection

4. **Messidor & Messidor-2**
   - 1,200+ retinal images
   - Structured annotations
   - Download: http://www.adcis.net/en/third-party/messidor/

### Dataset Structure

Organize your dataset in this format:

```
data/
└── dr_dataset/
    ├── 0_No_DR/
    │   ├── image001.jpg
    │   ├── image002.jpg
    │   └── ...
    ├── 1_Mild/
    │   ├── image001.jpg
    │   └── ...
    ├── 2_Moderate/
    ├── 3_Severe/
    └── 4_Proliferative_DR/
```

## 🚀 Usage

### 1. Training the Model

Run the complete training pipeline:

```bash
python train.py
```

This will:
1. ✅ Generate/load dataset
2. ✅ Initialize ResNet18 model with pretrained weights
3. ✅ Train with data augmentation
4. ✅ Validate and save best model
5. ✅ Generate all evaluation metrics
6. ✅ Create visualization plots

**Training Output:**
- `models/best_model.pth` - Best model checkpoint
- `results/training_history.png` - Training curves
- `results/confusion_matrix.png` - Classification confusion matrix
- `results/roc_curves.png` - ROC curves
- `results/classification_report.txt` - Detailed metrics
- `results/training_results.json` - Complete results

### 2. Making Predictions (Inference)

#### Single Image Prediction

```bash
python inference.py --model models/best_model.pth --image path/to/fundus_image.jpg
```

#### Batch Processing (Multiple Images)

```bash
python inference.py --model models/best_model.pth --image path/to/images/ --batch --output visualizations/
```

**Inference Output:**
- Predicted class and severity score (0-4)
- Confidence percentage
- Clinical recommendation
- Probability distribution across all classes
- GradCAM visualization showing model attention
- Comprehensive visualization saved as PNG

### 3. Example Output

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

## 🧠 Model Architecture

### Base Model: ResNet18
- Pretrained on ImageNet
- Efficient for CPU training
- Proven performance on medical imaging tasks

### Custom Classifier
```
Input: 512 features from ResNet18
  ↓
Dropout(0.5)
  ↓
Linear(512 → 256) + ReLU
  ↓
Dropout(0.3)
  ↓
Linear(256 → 5) → Output (5 classes)
```

### Training Configuration
- **Optimizer**: Adam (lr=0.001, weight_decay=1e-4)
- **Loss**: CrossEntropyLoss
- **Scheduler**: ReduceLROnPlateau
- **Batch Size**: 16 (CPU-optimized)
- **Image Size**: 224×224
- **Epochs**: 15 (adjustable)

## 📊 Evaluation Metrics

### Classification Metrics (Per-Class)
- **Accuracy**: Overall classification accuracy
- **Precision**: Positive predictive value
- **Recall (Sensitivity)**: True positive rate
- **F1-Score**: Harmonic mean of precision and recall

### Clinical Metrics (Per-Class)
- **Sensitivity**: Ability to detect disease when present
- **Specificity**: Ability to correctly identify healthy cases
- **PPV**: Probability of disease given positive test
- **NPV**: Probability of no disease given negative test

### Model Performance Visualization
- **ROC Curves**: Trade-off between sensitivity and specificity
- **AUC Scores**: Area under ROC curve for each class
- **Confusion Matrix**: Detailed error analysis

## 🔬 GradCAM Visualization

Grad-CAM (Gradient-weighted Class Activation Mapping) highlights the regions of the fundus image that the model focuses on when making predictions.

**Interpretation:**
- 🔴 **Red areas**: High attention (strong influence on prediction)
- 🟡 **Yellow areas**: Moderate attention
- 🟢 **Green/Blue areas**: Low attention

This helps clinicians understand:
- Whether the model is looking at pathological features (hemorrhages, exudates, microaneurysms)
- If the model focuses on irrelevant areas (artifacts, image borders)
- Model reliability and interpretability for clinical use

## 🎓 Clinical Context

### Diabetic Retinopathy Severity Levels

1. **No DR (Class 0)**
   - No visible retinal abnormalities
   - Annual screening recommended

2. **Mild NPDR (Class 1)**
   - Microaneurysms only
   - Follow-up: 6-12 months

3. **Moderate NPDR (Class 2)**
   - More than microaneurysms but less than severe
   - Includes: Hemorrhages, exudates, cotton wool spots
   - Follow-up: 3-6 months

4. **Severe NPDR (Class 3)**
   - Any of: >20 intraretinal hemorrhages per quadrant, venous beading, IRMA
   - High risk of progression to PDR
   - Prompt ophthalmologist referral

5. **Proliferative DR (Class 4)**
   - Neovascularization (new abnormal blood vessels)
   - Vitreous/preretinal hemorrhage
   - **URGENT** ophthalmologist referral needed
   - Risk of vision loss

## ⚙️ Customization

### Modify Training Parameters

Edit the `config` dictionary in `train.py`:

```python
config = {
    'img_size': 224,              # Image resolution
    'batch_size': 16,             # Batch size (reduce for low memory)
    'num_epochs': 15,             # Training epochs
    'learning_rate': 0.001,       # Learning rate
    'num_classes': 5,             # Number of classes
    'train_split': 0.8,           # Train/val split ratio
    'num_samples_per_class': 150  # Samples per class (synthetic)
}
```

### Use Different Model Architecture

Replace in `train.py`:

```python
# Current: ResNet18
self.model = models.resnet18(pretrained=pretrained)

# Alternatives:
# self.model = models.resnet34(pretrained=pretrained)  # Larger ResNet
# self.model = models.efficientnet_b0(pretrained=pretrained)  # EfficientNet
# self.model = models.mobilenet_v2(pretrained=pretrained)  # Lighter model
```

### Adjust Data Augmentation

Modify transforms in `train.py`:

```python
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.5),
    transforms.RandomRotation(20),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    # Add more augmentations:
    # transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
    # transforms.GaussianBlur(kernel_size=3),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                        std=[0.229, 0.224, 0.225])
])
```

## 🔍 Troubleshooting

### Out of Memory (CPU)
- Reduce `batch_size` in config (try 8 or 4)
- Use smaller image size (`img_size`: 128 or 96)
- Reduce `num_samples_per_class`

### Training Too Slow
- Reduce `num_epochs`
- Use smaller dataset
- Consider GPU training if available

### Poor Performance
- Increase `num_epochs`
- Use real clinical dataset instead of synthetic
- Try different learning rates (0.0001 or 0.01)
- Adjust class imbalance with weighted loss

### Model Not Loading
- Ensure model path is correct
- Check that model architecture matches training

## 📈 Performance Expectations

### Synthetic Dataset (Demo)
- Training Accuracy: ~85-95%
- Validation Accuracy: ~75-85%
- **Note**: Synthetic data is for demonstration only

### Real Clinical Datasets
Expected performance on real datasets (with proper training):
- Accuracy: 85-92%
- AUC: 0.90-0.95 (per class)
- Sensitivity: 80-90% (varies by severity)

**Clinical Validation Required**: Before any clinical use, the model must be:
- Validated on diverse patient populations
- Tested against ophthalmologist assessments
- Approved by regulatory bodies (FDA, CE, etc.)

## ⚠️ Important Disclaimers

### Research Use Only
This system is designed for **research and educational purposes only**. It is NOT approved for clinical diagnosis or patient care.

### Not a Substitute for Professional Diagnosis
- Always consult a qualified ophthalmologist for diagnosis
- Automated systems can have errors and biases
- Clinical judgment is essential

### Data Privacy
- Ensure compliance with HIPAA, GDPR, and local regulations
- De-identify patient data before processing
- Use secure storage for medical images

### Model Limitations
- Performance depends heavily on image quality
- May not generalize to different imaging equipment
- Requires validation on target population
- Can have biases from training data

## 📖 References

### Key Papers on DR Detection
1. Gulshan et al. (2016) - "Development and Validation of a Deep Learning Algorithm for Detection of Diabetic Retinopathy"
2. Ting et al. (2017) - "Development and Validation of a Deep Learning System for Diabetic Retinopathy"
3. Selvaraju et al. (2017) - "Grad-CAM: Visual Explanations from Deep Networks"

### Clinical Guidelines
- American Academy of Ophthalmology - Diabetic Retinopathy Preferred Practice Pattern
- International Council of Ophthalmology - DR Screening Guidelines

## 🤝 Contributing

This is a research project. Improvements welcome:
- Enhanced data augmentation strategies
- Additional model architectures
- Better visualization tools
- Performance optimizations

## 📄 License

This project is for educational and research purposes. When using real clinical datasets, respect their individual licenses and usage terms.

## 📧 Support

For questions about the implementation or research collaboration:
- Check the documentation above
- Review the code comments
- Consult medical imaging literature

---

**Remember**: AI-assisted diagnosis is a tool to support, not replace, clinical expertise. Always prioritize patient safety and professional medical judgment.

---

*Last Updated: October 2025*
