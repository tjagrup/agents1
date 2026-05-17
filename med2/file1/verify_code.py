"""
Diabetic Retinopathy Detection - Code Structure Verification
This script verifies the code structure without requiring full package installation
"""

import ast
import os

def check_file_syntax(filepath):
    """Check if Python file has valid syntax"""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        ast.parse(code)
        return True, "✅ Valid syntax"
    except SyntaxError as e:
        return False, f"❌ Syntax Error: {e}"
    except Exception as e:
        return False, f"❌ Error: {e}"

def analyze_code_structure(filepath):
    """Analyze Python file structure"""
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())
    
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    
    return classes, functions

def main():
    print("=" * 70)
    print("DIABETIC RETINOPATHY DETECTION - CODE VERIFICATION")
    print("=" * 70)
    print()
    
    # Files to check
    files_to_check = {
        'train.py': 'Training Pipeline',
        'inference.py': 'Inference Interface',
        'requirements.txt': 'Dependencies',
        'README.md': 'Documentation'
    }
    
    print("📁 Checking project structure...\n")
    
    all_valid = True
    
    for filename, description in files_to_check.items():
        filepath = filename
        
        if not os.path.exists(filepath):
            print(f"❌ {description} ({filename}): NOT FOUND")
            all_valid = False
            continue
        
        filesize = os.path.getsize(filepath)
        
        if filename.endswith('.py'):
            valid, message = check_file_syntax(filepath)
            
            if valid:
                classes, functions = analyze_code_structure(filepath)
                print(f"✅ {description} ({filename})")
                print(f"   Size: {filesize:,} bytes")
                print(f"   Classes: {len(classes)} - {', '.join(classes[:3])}{', ...' if len(classes) > 3 else ''}")
                print(f"   Functions: {len(functions)} - {', '.join(functions[:3])}{', ...' if len(functions) > 3 else ''}")
                print()
            else:
                print(f"❌ {description} ({filename}): {message}\n")
                all_valid = False
        else:
            print(f"✅ {description} ({filename})")
            print(f"   Size: {filesize:,} bytes\n")
    
    print("=" * 70)
    print("CODE STRUCTURE COMPONENTS")
    print("=" * 70)
    print()
    
    # Analyze train.py
    print("📊 Training Pipeline (train.py):")
    classes, functions = analyze_code_structure('train.py')
    print(f"   • {len(classes)} Classes:")
    for cls in classes:
        print(f"     - {cls}")
    print(f"   • {len(functions)} Functions:")
    for func in functions[:10]:  # Show first 10
        print(f"     - {func}()")
    if len(functions) > 10:
        print(f"     ... and {len(functions) - 10} more")
    print()
    
    # Analyze inference.py
    print("🔍 Inference Interface (inference.py):")
    classes, functions = analyze_code_structure('inference.py')
    print(f"   • {len(classes)} Classes:")
    for cls in classes:
        print(f"     - {cls}")
    print(f"   • {len(functions)} Functions:")
    for func in functions[:10]:
        print(f"     - {func}()")
    if len(functions) > 10:
        print(f"     ... and {len(functions) - 10} more")
    print()
    
    print("=" * 70)
    
    if all_valid:
        print("✅ ALL CHECKS PASSED - Code structure is valid!")
        print()
        print("🚀 Ready to use:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Run training: python train.py")
        print("   3. Run inference: python inference.py --model models/best_model.pth --image <image_path>")
    else:
        print("❌ Some checks failed - please review the errors above")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
