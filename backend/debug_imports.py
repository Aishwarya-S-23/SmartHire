print("🔍 Debugging imports...")

try:
    import fastapi
    print("✅ fastapi imported")
except ImportError as e:
    print(f"❌ fastapi: {e}")

try:
    import uvicorn
    print("✅ uvicorn imported")
except ImportError as e:
    print(f"❌ uvicorn: {e}")

try:
    import pandas
    print("✅ pandas imported")
except ImportError as e:
    print(f"❌ pandas: {e}")

try:
    import sklearn
    print("✅ scikit-learn imported")
except ImportError as e:
    print(f"❌ scikit-learn: {e}")

try:
    import nltk
    print("✅ nltk imported")
except ImportError as e:
    print(f"❌ nltk: {e}")

try:
    import spacy
    print("✅ spacy imported")
except ImportError as e:
    print(f"❌ spacy: {e}")

try:
    import pdfplumber
    print("✅ pdfplumber imported")
except ImportError as e:
    print(f"❌ pdfplumber: {e}")

try:
    import docx
    print("✅ python-docx imported")
except ImportError as e:
    print(f"❌ python-docx: {e}")

print("🎯 Debug complete!")