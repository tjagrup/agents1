#!/bin/bash

echo "=============================================================="
echo "Diabetic Retinopathy Detection - Quick Start Demo"
echo "=============================================================="
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q torch torchvision numpy pandas matplotlib seaborn scikit-learn Pillow opencv-python tqdm --break-system-packages

echo ""
echo "✅ Dependencies installed"
echo ""

# Run training (quick demo with small dataset)
echo "🚀 Starting training pipeline..."
echo "   (Using small synthetic dataset for demo - only 3 epochs)"
echo ""

python train.py

echo ""
echo "=============================================================="
echo "Training Complete!"
echo "=============================================================="
echo ""
echo "📊 Check the results:"
echo "   - models/best_model.pth (trained model)"
echo "   - results/ (all evaluation metrics)"
echo ""
echo "🔍 To test inference on an image:"
echo "   python inference.py --model models/best_model.pth --image data/synthetic_dr_dataset/0_No_DR/image_0000.jpg"
echo ""
echo "=============================================================="
