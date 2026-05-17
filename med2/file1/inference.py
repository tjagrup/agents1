"""
Diabetic Retinopathy Detection - Inference Interface with Visualization
Includes GradCAM for model interpretability
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
import torchvision.models as models
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import os
import argparse
from datetime import datetime

class DRModel(nn.Module):
    """
    Diabetic Retinopathy Detection Model
    Must match the architecture used in training
    """
    
    def __init__(self, num_classes=5):
        super(DRModel, self).__init__()
        self.model = models.resnet18(pretrained=False)
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

class GradCAM:
    """
    Gradient-weighted Class Activation Mapping (Grad-CAM)
    for visualizing model attention
    """
    
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks
        target_layer.register_forward_hook(self.save_activation)
        target_layer.register_backward_hook(self.save_gradient)
    
    def save_activation(self, module, input, output):
        self.activations = output.detach()
    
    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()
    
    def generate_cam(self, input_image, target_class=None):
        """Generate class activation map"""
        # Forward pass
        model_output = self.model(input_image)
        
        if target_class is None:
            target_class = model_output.argmax(dim=1).item()
        
        # Zero gradients
        self.model.zero_grad()
        
        # Backward pass
        class_loss = model_output[0, target_class]
        class_loss.backward()
        
        # Get gradients and activations
        gradients = self.gradients[0].cpu().numpy()
        activations = self.activations[0].cpu().numpy()
        
        # Calculate weights
        weights = np.mean(gradients, axis=(1, 2))
        
        # Generate CAM
        cam = np.zeros(activations.shape[1:], dtype=np.float32)
        for i, w in enumerate(weights):
            cam += w * activations[i]
        
        # Apply ReLU
        cam = np.maximum(cam, 0)
        
        # Normalize
        if cam.max() > 0:
            cam = cam / cam.max()
        
        return cam, target_class

class DRInference:
    """Inference engine for diabetic retinopathy detection"""
    
    def __init__(self, model_path, device='cpu'):
        self.device = torch.device(device)
        self.model = DRModel(num_classes=5)
        
        # Load trained weights
        checkpoint = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        
        # Class names
        self.class_names = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative DR']
        self.class_descriptions = {
            0: "No Diabetic Retinopathy - Healthy retina with no signs of DR",
            1: "Mild NPDR - Microaneurysms only",
            2: "Moderate NPDR - More than just microaneurysms but less than Severe NPDR",
            3: "Severe NPDR - Any of the following: >20 intraretinal hemorrhages in each quadrant, "
               "definite venous beading in 2+ quadrants, prominent IRMA in 1+ quadrant",
            4: "Proliferative DR - Neovascularization or vitreous/preretinal hemorrhage"
        }
        
        # Transform
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Setup GradCAM
        self.gradcam = GradCAM(self.model, self.model.model.layer4[-1])
        
        print(f"✓ Model loaded successfully from {model_path}")
        print(f"✓ Using device: {self.device}\n")
    
    def preprocess_image(self, image_path):
        """Preprocess image for inference"""
        image = Image.open(image_path).convert('RGB')
        return image, self.transform(image).unsqueeze(0)
    
    def predict(self, image_path, visualize=True, save_dir='./visualizations'):
        """
        Make prediction on a single image
        
        Args:
            image_path: Path to input image
            visualize: Whether to generate visualization
            save_dir: Directory to save visualizations
        
        Returns:
            Dictionary with prediction results
        """
        # Load and preprocess image
        original_image, input_tensor = self.preprocess_image(image_path)
        input_tensor = input_tensor.to(self.device)
        
        # Make prediction
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = F.softmax(outputs, dim=1)[0]
            predicted_class = outputs.argmax(dim=1).item()
            confidence = probabilities[predicted_class].item()
        
        # Get all class probabilities
        class_probs = {self.class_names[i]: float(probabilities[i]) 
                      for i in range(len(self.class_names))}
        
        # Generate GradCAM
        cam, _ = self.gradcam.generate_cam(input_tensor, target_class=predicted_class)
        
        # Prepare results
        results = {
            'predicted_class': self.class_names[predicted_class],
            'predicted_class_idx': predicted_class,
            'confidence': confidence,
            'description': self.class_descriptions[predicted_class],
            'all_probabilities': class_probs,
            'severity_score': predicted_class  # 0-4 scale
        }
        
        # Clinical recommendation
        if predicted_class == 0:
            results['recommendation'] = "No diabetic retinopathy detected. Continue annual screening."
        elif predicted_class == 1:
            results['recommendation'] = "Mild NPDR detected. Follow-up in 6-12 months."
        elif predicted_class == 2:
            results['recommendation'] = "Moderate NPDR detected. Follow-up in 3-6 months."
        elif predicted_class == 3:
            results['recommendation'] = "Severe NPDR detected. Refer to ophthalmologist promptly."
        else:
            results['recommendation'] = "Proliferative DR detected. URGENT referral to ophthalmologist required!"
        
        # Visualize if requested
        if visualize:
            os.makedirs(save_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.basename(image_path).split('.')[0]
            save_path = os.path.join(save_dir, f'{filename}_prediction_{timestamp}.png')
            
            self.visualize_prediction(original_image, cam, results, save_path)
            results['visualization_path'] = save_path
        
        return results
    
    def visualize_prediction(self, original_image, cam, results, save_path):
        """
        Create comprehensive visualization of prediction
        """
        fig = plt.figure(figsize=(18, 6))
        
        # Original image
        ax1 = plt.subplot(1, 3, 1)
        ax1.imshow(original_image)
        ax1.set_title('Original Fundus Image', fontsize=14, fontweight='bold')
        ax1.axis('off')
        
        # GradCAM overlay
        ax2 = plt.subplot(1, 3, 2)
        
        # Resize CAM to match image size
        cam_resized = cv2.resize(cam, (original_image.width, original_image.height))
        
        # Convert to heatmap
        heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        # Overlay
        original_np = np.array(original_image)
        overlay = cv2.addWeighted(original_np, 0.6, heatmap, 0.4, 0)
        
        ax2.imshow(overlay)
        ax2.set_title('GradCAM Attention Map\n(Areas the model focused on)', 
                     fontsize=14, fontweight='bold')
        ax2.axis('off')
        
        # Prediction details
        ax3 = plt.subplot(1, 3, 3)
        ax3.axis('off')
        
        # Prediction text
        pred_class = results['predicted_class']
        confidence = results['confidence']
        severity = results['severity_score']
        
        # Color coding based on severity
        colors = ['green', 'yellow', 'orange', 'red', 'darkred']
        pred_color = colors[severity]
        
        text_y = 0.95
        ax3.text(0.5, text_y, 'PREDICTION RESULTS', 
                ha='center', va='top', fontsize=16, fontweight='bold',
                transform=ax3.transAxes)
        
        text_y -= 0.12
        ax3.text(0.5, text_y, f'{pred_class}',
                ha='center', va='top', fontsize=20, fontweight='bold',
                color=pred_color, transform=ax3.transAxes,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                         edgecolor=pred_color, linewidth=2))
        
        text_y -= 0.12
        ax3.text(0.5, text_y, f'Confidence: {confidence:.1%}',
                ha='center', va='top', fontsize=14, transform=ax3.transAxes)
        
        text_y -= 0.10
        ax3.text(0.5, text_y, f'Severity Score: {severity}/4',
                ha='center', va='top', fontsize=12, transform=ax3.transAxes)
        
        # Probability distribution
        text_y -= 0.10
        ax3.text(0.5, text_y, 'Class Probabilities:',
                ha='center', va='top', fontsize=12, fontweight='bold',
                transform=ax3.transAxes)
        
        text_y -= 0.08
        all_probs = results['all_probabilities']
        for class_name, prob in all_probs.items():
            bar_color = 'lightcoral' if class_name == pred_class else 'lightblue'
            ax3.barh(text_y, prob, height=0.04, left=0.1, color=bar_color,
                    transform=ax3.transAxes, alpha=0.7)
            ax3.text(0.05, text_y, f'{class_name}:', 
                    ha='right', va='center', fontsize=9, transform=ax3.transAxes)
            ax3.text(0.1 + prob + 0.02, text_y, f'{prob:.1%}',
                    ha='left', va='center', fontsize=9, transform=ax3.transAxes)
            text_y -= 0.06
        
        # Recommendation
        text_y -= 0.05
        recommendation = results['recommendation']
        ax3.text(0.5, text_y, 'Clinical Recommendation:',
                ha='center', va='top', fontsize=11, fontweight='bold',
                transform=ax3.transAxes)
        
        text_y -= 0.08
        # Wrap text
        import textwrap
        wrapped_text = textwrap.fill(recommendation, width=40)
        ax3.text(0.5, text_y, wrapped_text,
                ha='center', va='top', fontsize=9,
                transform=ax3.transAxes,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', 
                         edgecolor='gray', linewidth=1))
        
        plt.suptitle('Diabetic Retinopathy Detection Results', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Visualization saved to: {save_path}")
    
    def batch_predict(self, image_paths, save_dir='./visualizations'):
        """
        Make predictions on multiple images
        """
        results_list = []
        
        print(f"\nProcessing {len(image_paths)} images...\n")
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"[{i}/{len(image_paths)}] Processing: {os.path.basename(image_path)}")
            
            try:
                results = self.predict(image_path, visualize=True, save_dir=save_dir)
                results['image_path'] = image_path
                results_list.append(results)
                
                print(f"  → Prediction: {results['predicted_class']} "
                      f"(Confidence: {results['confidence']:.1%})")
                print(f"  → {results['recommendation']}\n")
                
            except Exception as e:
                print(f"  → Error processing image: {str(e)}\n")
                continue
        
        return results_list
    
    def print_results(self, results):
        """Pretty print prediction results"""
        print("\n" + "=" * 70)
        print("DIABETIC RETINOPATHY DETECTION RESULTS")
        print("=" * 70)
        
        print(f"\n📊 Prediction: {results['predicted_class']}")
        print(f"   Confidence: {results['confidence']:.2%}")
        print(f"   Severity Score: {results['severity_score']}/4")
        
        print(f"\n📝 Description:")
        print(f"   {results['description']}")
        
        print(f"\n💡 Clinical Recommendation:")
        print(f"   {results['recommendation']}")
        
        print(f"\n📈 Class Probabilities:")
        for class_name, prob in results['all_probabilities'].items():
            bar = '█' * int(prob * 40)
            print(f"   {class_name:20s} {prob:6.2%} {bar}")
        
        if 'visualization_path' in results:
            print(f"\n🖼️  Visualization: {results['visualization_path']}")
        
        print("\n" + "=" * 70 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description='Diabetic Retinopathy Detection - Inference Interface'
    )
    parser.add_argument('--model', type=str, default='./models/best_model.pth',
                       help='Path to trained model')
    parser.add_argument('--image', type=str, required=True,
                       help='Path to input image or directory of images')
    parser.add_argument('--output', type=str, default='./visualizations',
                       help='Output directory for visualizations')
    parser.add_argument('--batch', action='store_true',
                       help='Process multiple images from directory')
    
    args = parser.parse_args()
    
    # Initialize inference engine
    print("=" * 70)
    print("DIABETIC RETINOPATHY DETECTION - INFERENCE")
    print("=" * 70 + "\n")
    
    inference = DRInference(args.model, device='cpu')
    
    # Process image(s)
    if args.batch and os.path.isdir(args.image):
        # Batch processing
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_paths = [
            os.path.join(args.image, f) for f in os.listdir(args.image)
            if os.path.splitext(f)[1].lower() in image_extensions
        ]
        
        if not image_paths:
            print(f"No images found in {args.image}")
            return
        
        results_list = inference.batch_predict(image_paths, save_dir=args.output)
        
        print("\n" + "=" * 70)
        print(f"BATCH PROCESSING COMPLETE - {len(results_list)} images processed")
        print("=" * 70)
        
    else:
        # Single image processing
        if not os.path.exists(args.image):
            print(f"Error: Image not found at {args.image}")
            return
        
        results = inference.predict(args.image, visualize=True, save_dir=args.output)
        inference.print_results(results)

if __name__ == "__main__":
    main()
