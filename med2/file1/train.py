"""
Diabetic Retinopathy Detection - Complete Training Pipeline
Multi-class classification: 0-No DR, 1-Mild, 2-Moderate, 3-Severe, 4-Proliferative DR
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import torchvision.transforms as transforms
import torchvision.models as models
from torchvision.datasets import ImageFolder
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
from sklearn.preprocessing import label_binarize
from PIL import Image
import os
from tqdm import tqdm
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set random seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)

class DiabeticRetinopathyDataset(Dataset):
    """Custom Dataset for Diabetic Retinopathy Images"""
    
    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

class DRModel(nn.Module):
    """
    Diabetic Retinopathy Detection Model
    Based on EfficientNet-B0 for CPU efficiency
    """
    
    def __init__(self, num_classes=5, pretrained=True):
        super(DRModel, self).__init__()
        # Use ResNet18 for better CPU performance
        self.model = models.resnet18(pretrained=pretrained)
        
        # Modify final layer for 5-class classification
        num_features = self.model.fc.in_features
        self.model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        return self.model(x)

class DRTrainer:
    """Complete training pipeline for DR detection"""
    
    def __init__(self, model, device, save_dir='./models'):
        self.model = model.to(device)
        self.device = device
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
        self.train_losses = []
        self.val_losses = []
        self.train_accs = []
        self.val_accs = []
        
    def train_epoch(self, train_loader, criterion, optimizer):
        """Train for one epoch"""
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(train_loader, desc='Training')
        for images, labels in pbar:
            images, labels = images.to(self.device), labels.to(self.device)
            
            optimizer.zero_grad()
            outputs = self.model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            pbar.set_postfix({'loss': f'{running_loss/len(pbar):.4f}',
                            'acc': f'{100.*correct/total:.2f}%'})
        
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100. * correct / total
        return epoch_loss, epoch_acc
    
    def validate(self, val_loader, criterion):
        """Validate the model"""
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        all_preds = []
        all_labels = []
        all_probs = []
        
        with torch.no_grad():
            for images, labels in tqdm(val_loader, desc='Validation'):
                images, labels = images.to(self.device), labels.to(self.device)
                
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                
                running_loss += loss.item()
                probs = torch.softmax(outputs, dim=1)
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
                
                all_preds.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                all_probs.extend(probs.cpu().numpy())
        
        epoch_loss = running_loss / len(val_loader)
        epoch_acc = 100. * correct / total
        
        return epoch_loss, epoch_acc, all_preds, all_labels, all_probs
    
    def train(self, train_loader, val_loader, num_epochs=20, lr=0.001):
        """Complete training loop"""
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=lr, weight_decay=1e-4)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', 
                                                         factor=0.5, patience=3)
        
        best_val_acc = 0.0
        
        print("=" * 60)
        print("Starting Training")
        print("=" * 60)
        
        for epoch in range(num_epochs):
            print(f"\nEpoch {epoch+1}/{num_epochs}")
            print("-" * 60)
            
            # Train
            train_loss, train_acc = self.train_epoch(train_loader, criterion, optimizer)
            self.train_losses.append(train_loss)
            self.train_accs.append(train_acc)
            
            # Validate
            val_loss, val_acc, val_preds, val_labels, val_probs = self.validate(val_loader, criterion)
            self.val_losses.append(val_loss)
            self.val_accs.append(val_acc)
            
            # Learning rate scheduling
            scheduler.step(val_loss)
            
            print(f"\nTrain Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
            print(f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'val_acc': val_acc,
                    'val_loss': val_loss,
                }, os.path.join(self.save_dir, 'best_model.pth'))
                print(f"✓ Best model saved! (Val Acc: {val_acc:.2f}%)")
        
        print("\n" + "=" * 60)
        print(f"Training Complete! Best Val Acc: {best_val_acc:.2f}%")
        print("=" * 60)
        
        return val_preds, val_labels, val_probs

def create_synthetic_dataset(num_samples_per_class=200, img_size=224):
    """
    Create synthetic dataset for demonstration
    In practice, you would use real fundus images from Kaggle or EyePACS
    """
    print("Creating synthetic dataset for demonstration...")
    print("NOTE: In production, replace this with real fundus images from:")
    print("  - Kaggle Diabetic Retinopathy Detection dataset")
    print("  - EyePACS dataset")
    print("  - APTOS 2019 Blindness Detection dataset\n")
    
    data_dir = './data/synthetic_dr_dataset'
    classes = ['0_No_DR', '1_Mild', '2_Moderate', '3_Severe', '4_Proliferative_DR']
    
    for class_name in classes:
        class_dir = os.path.join(data_dir, class_name)
        os.makedirs(class_dir, exist_ok=True)
        
        for i in range(num_samples_per_class):
            # Create synthetic retinal-like images with different patterns per class
            class_idx = int(class_name[0])
            
            # Base image with circular retina shape
            img = np.zeros((img_size, img_size, 3), dtype=np.uint8)
            center = img_size // 2
            radius = img_size // 2 - 10
            
            # Create circular mask for retina
            y, x = np.ogrid[:img_size, :img_size]
            mask = (x - center)**2 + (y - center)**2 <= radius**2
            
            # Base retina color (reddish)
            img[mask] = [180 - class_idx*20, 80 - class_idx*10, 60 - class_idx*10]
            
            # Add vessels (darker lines)
            for _ in range(5 + class_idx * 2):
                angle = np.random.rand() * 2 * np.pi
                length = np.random.randint(50, radius)
                x_end = int(center + length * np.cos(angle))
                y_end = int(center + length * np.sin(angle))
                
                # Draw vessel
                for t in np.linspace(0, 1, 100):
                    x_pos = int(center + t * (x_end - center))
                    y_pos = int(center + t * (y_end - center))
                    if 0 <= x_pos < img_size and 0 <= y_pos < img_size:
                        img[max(0, y_pos-1):min(img_size, y_pos+2),
                            max(0, x_pos-1):min(img_size, x_pos+2)] = [60, 30, 20]
            
            # Add pathological features based on severity
            if class_idx > 0:  # Mild to Proliferative
                # Add microaneurysms (small dots)
                num_dots = class_idx * 5
                for _ in range(num_dots):
                    dot_x = np.random.randint(center-radius+20, center+radius-20)
                    dot_y = np.random.randint(center-radius+20, center+radius-20)
                    if mask[dot_y, dot_x]:
                        img[dot_y-2:dot_y+2, dot_x-2:dot_x+2] = [255, 0, 0]
            
            if class_idx > 1:  # Moderate to Proliferative
                # Add hemorrhages (larger red spots)
                num_spots = class_idx * 2
                for _ in range(num_spots):
                    spot_x = np.random.randint(center-radius+30, center+radius-30)
                    spot_y = np.random.randint(center-radius+30, center+radius-30)
                    spot_size = np.random.randint(3, 8)
                    if mask[spot_y, spot_x]:
                        img[spot_y-spot_size:spot_y+spot_size,
                            spot_x-spot_size:spot_x+spot_size] = [200, 0, 0]
            
            if class_idx > 2:  # Severe and Proliferative
                # Add exudates (yellow/white spots)
                num_exudates = class_idx * 3
                for _ in range(num_exudates):
                    ex_x = np.random.randint(center-radius+30, center+radius-30)
                    ex_y = np.random.randint(center-radius+30, center+radius-30)
                    ex_size = np.random.randint(2, 5)
                    if mask[ex_y, ex_x]:
                        img[ex_y-ex_size:ex_y+ex_size,
                            ex_x-ex_size:ex_x+ex_size] = [255, 255, 180]
            
            # Add optic disc (bright spot)
            disc_x = center + radius // 2
            disc_y = center
            disc_radius = 15
            for dy in range(-disc_radius, disc_radius):
                for dx in range(-disc_radius, disc_radius):
                    if dx**2 + dy**2 <= disc_radius**2:
                        px, py = disc_x + dx, disc_y + dy
                        if 0 <= px < img_size and 0 <= py < img_size and mask[py, px]:
                            img[py, px] = [250, 220, 180]
            
            # Add some noise
            noise = np.random.randint(-15, 15, img.shape, dtype=np.int16)
            img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            
            # Save image
            img_pil = Image.fromarray(img)
            img_pil.save(os.path.join(class_dir, f'image_{i:04d}.jpg'))
    
    print(f"✓ Created {num_samples_per_class * len(classes)} synthetic images")
    print(f"  Distribution: {num_samples_per_class} images per class\n")
    
    return data_dir

def plot_training_history(trainer, save_path='./results/training_history.png'):
    """Plot training history"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # Loss plot
    axes[0].plot(trainer.train_losses, label='Train Loss', marker='o')
    axes[0].plot(trainer.val_losses, label='Val Loss', marker='s')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Training and Validation Loss')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Accuracy plot
    axes[1].plot(trainer.train_accs, label='Train Accuracy', marker='o')
    axes[1].plot(trainer.val_accs, label='Val Accuracy', marker='s')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy (%)')
    axes[1].set_title('Training and Validation Accuracy')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Training history saved to {save_path}")
    plt.close()

def plot_confusion_matrix(y_true, y_pred, save_path='./results/confusion_matrix.png'):
    """Plot confusion matrix"""
    cm = confusion_matrix(y_true, y_pred)
    class_names = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative']
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names,
                cbar_kws={'label': 'Count'})
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix - Diabetic Retinopathy Detection')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Confusion matrix saved to {save_path}")
    plt.close()
    
    return cm

def plot_roc_curves(y_true, y_probs, save_path='./results/roc_curves.png'):
    """Plot ROC curves for each class"""
    n_classes = 5
    class_names = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative']
    
    # Binarize the output
    y_true_bin = label_binarize(y_true, classes=[0, 1, 2, 3, 4])
    y_probs_array = np.array(y_probs)
    
    # Compute ROC curve and AUC for each class
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    
    plt.figure(figsize=(10, 8))
    
    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_probs_array[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])
        plt.plot(fpr[i], tpr[i], label=f'{class_names[i]} (AUC = {roc_auc[i]:.3f})', linewidth=2)
    
    plt.plot([0, 1], [0, 1], 'k--', linewidth=2, label='Random Classifier')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curves - Multi-class Diabetic Retinopathy Detection')
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ ROC curves saved to {save_path}")
    plt.close()
    
    return roc_auc

def generate_classification_report(y_true, y_pred, save_path='./results/classification_report.txt'):
    """Generate and save classification report"""
    class_names = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative']
    report = classification_report(y_true, y_pred, target_names=class_names, digits=4)
    
    with open(save_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("CLASSIFICATION REPORT - DIABETIC RETINOPATHY DETECTION\n")
        f.write("=" * 70 + "\n\n")
        f.write(report)
        f.write("\n" + "=" * 70 + "\n")
    
    print(f"✓ Classification report saved to {save_path}")
    print("\nClassification Report:")
    print(report)

def calculate_clinical_metrics(cm):
    """Calculate clinical metrics: sensitivity, specificity, PPV, NPV"""
    class_names = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative']
    n_classes = len(class_names)
    
    metrics = {}
    
    print("\n" + "=" * 70)
    print("CLINICAL METRICS (Per-Class)")
    print("=" * 70)
    
    for i in range(n_classes):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        tn = cm.sum() - tp - fp - fn
        
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0
        
        metrics[class_names[i]] = {
            'Sensitivity (Recall)': sensitivity,
            'Specificity': specificity,
            'PPV (Precision)': ppv,
            'NPV': npv
        }
        
        print(f"\n{class_names[i]}:")
        print(f"  Sensitivity (Recall): {sensitivity:.4f}")
        print(f"  Specificity: {specificity:.4f}")
        print(f"  PPV (Precision): {ppv:.4f}")
        print(f"  NPV: {npv:.4f}")
    
    return metrics

def main():
    """Main training pipeline"""
    print("=" * 70)
    print("DIABETIC RETINOPATHY DETECTION - ML TRAINING PIPELINE")
    print("=" * 70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Configuration
    config = {
        'img_size': 224,
        'batch_size': 16,  # Small batch size for CPU
        'num_epochs': 15,  # Reduced for CPU training
        'learning_rate': 0.001,
        'num_classes': 5,
        'train_split': 0.8,
        'num_samples_per_class': 150  # Reduced for faster training
    }
    
    print("Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()
    
    # Create results directory
    os.makedirs('./results', exist_ok=True)
    os.makedirs('./models', exist_ok=True)
    os.makedirs('./visualizations', exist_ok=True)
    
    # Create or load dataset
    data_dir = create_synthetic_dataset(num_samples_per_class=config['num_samples_per_class'],
                                       img_size=config['img_size'])
    
    # Data transforms
    train_transform = transforms.Compose([
        transforms.Resize((config['img_size'], config['img_size'])),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((config['img_size'], config['img_size'])),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Load dataset
    print("Loading dataset...")
    full_dataset = ImageFolder(data_dir)
    
    # Split dataset
    train_size = int(config['train_split'] * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
    
    # Apply transforms
    train_dataset.dataset.transform = train_transform
    val_dataset.dataset.transform = val_transform
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=config['batch_size'], 
                             shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=config['batch_size'], 
                           shuffle=False, num_workers=0)
    
    print(f"✓ Dataset loaded")
    print(f"  Training samples: {train_size}")
    print(f"  Validation samples: {val_size}\n")
    
    # Initialize model
    device = torch.device('cpu')
    print(f"Using device: {device}\n")
    
    model = DRModel(num_classes=config['num_classes'], pretrained=True)
    print("✓ Model initialized (ResNet18 with custom classifier)\n")
    
    # Initialize trainer
    trainer = DRTrainer(model, device, save_dir='./models')
    
    # Train model
    val_preds, val_labels, val_probs = trainer.train(
        train_loader, 
        val_loader, 
        num_epochs=config['num_epochs'],
        lr=config['learning_rate']
    )
    
    # Generate visualizations and metrics
    print("\n" + "=" * 70)
    print("GENERATING EVALUATION METRICS AND VISUALIZATIONS")
    print("=" * 70 + "\n")
    
    # Training history
    plot_training_history(trainer, save_path='./results/training_history.png')
    
    # Confusion matrix
    cm = plot_confusion_matrix(val_labels, val_preds, save_path='./results/confusion_matrix.png')
    
    # ROC curves
    roc_auc = plot_roc_curves(val_labels, val_probs, save_path='./results/roc_curves.png')
    
    # Classification report
    generate_classification_report(val_labels, val_preds, 
                                   save_path='./results/classification_report.txt')
    
    # Clinical metrics
    clinical_metrics = calculate_clinical_metrics(cm)
    
    # Save configuration and results
    results = {
        'config': config,
        'best_val_accuracy': max(trainer.val_accs),
        'final_train_accuracy': trainer.train_accs[-1],
        'final_val_accuracy': trainer.val_accs[-1],
        'roc_auc_scores': {f'Class_{i}': float(roc_auc[i]) for i in range(5)},
        'clinical_metrics': {k: {mk: float(mv) for mk, mv in v.items()} 
                           for k, v in clinical_metrics.items()},
        'training_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open('./results/training_results.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"\n✓ All results saved to ./results/")
    print("\n" + "=" * 70)
    print("TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nBest Validation Accuracy: {max(trainer.val_accs):.2f}%")
    print(f"Model saved to: ./models/best_model.pth")
    print("=" * 70)

if __name__ == "__main__":
    main()
