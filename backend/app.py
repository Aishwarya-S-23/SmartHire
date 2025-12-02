from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from model import SmartHireModel
from resume_parser import ResumeParser
import uvicorn
from typing import List

# Initialize FastAPI app
app = FastAPI(
    title="Smart Hire API",
    description="AI-Powered Resume Classification and Role Recommendation System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
smart_hire_model = SmartHireModel()
resume_parser = ResumeParser()

# Request models
class ResumeAnalysisRequest(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    status: str
    analysis: dict = None
    message: str = None

# Routes
@app.get("/")
async def root():
    return {
        "message": "Smart Hire - AI Recruitment Assistant",
        "status": "running",
        "version": "1.0.0",
        "features": [
            "Domain Classification (22 Domains)",
            "Top 3 Role Recommendations",
            "Skill-based Matching",
            "Resume Parsing (PDF/DOCX)",
            "HR Dashboard Integration"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "model_trained": smart_hire_model.is_trained,
        "domains_available": len(smart_hire_model.label_encoder.classes_) if smart_hire_model.label_encoder else 0
    }

@app.post("/train")
async def train_model():
    """Train the classification model with the dataset"""
    result = smart_hire_model.train_model()
    return result

@app.post("/analyze/resume")
async def analyze_resume(request: ResumeAnalysisRequest):
    """Complete analysis: domain + role recommendations"""
    result = smart_hire_model.full_analysis(request.text)
    return result

@app.post("/analyze/upload")
async def analyze_uploaded_resume(file: UploadFile = File(...)):
    """Analyze uploaded resume file"""
    try:
        # Read file content
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Parse resume
        parse_result = resume_parser.parse_resume(file_content, file.filename)
        if not parse_result['success']:
            raise HTTPException(status_code=400, detail=parse_result['error'])
        
        # Analyze with AI model
        analysis_result = smart_hire_model.full_analysis(parse_result['text'])
        
        return {
            "status": "success",
            "filename": file.filename,
            "parsing_info": {
                "word_count": parse_result['word_count'],
                "skills_extracted": parse_result['skills']
            },
            "analysis": analysis_result.get('analysis', {}) if analysis_result['status'] == 'success' else {}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/batch")
async def analyze_batch_resumes(files: List[UploadFile] = File(...)):
    """Analyze multiple resumes in batch"""
    results = []
    
    for file in files:
        try:
            file_content = await file.read()
            
            if len(file_content) == 0:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": "Empty file"
                })
                continue
                
            parse_result = resume_parser.parse_resume(file_content, file.filename)
            
            if parse_result['success']:
                analysis_result = smart_hire_model.full_analysis(parse_result['text'])
                results.append({
                    "filename": file.filename,
                    "status": "success",
                    "analysis": analysis_result.get('analysis', {}) if analysis_result['status'] == 'success' else {}
                })
            else:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": parse_result['error']
                })
                
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "total_processed": len(results),
        "successful": len([r for r in results if r['status'] == 'success']),
        "failed": len([r for r in results if r['status'] == 'error']),
        "results": results
    }

@app.get("/domains")
async def get_domains():
    """Get available domains and roles"""
    info = smart_hire_model.get_domain_info()
    return info

@app.get("/model/status")
async def model_status():
    """Get model training status"""
    return {
        "is_trained": smart_hire_model.is_trained,
        "domains_count": len(smart_hire_model.label_encoder.classes_) if smart_hire_model.label_encoder else 0,
        "available_roles": len(smart_hire_model.DOMAIN_ROLES) if smart_hire_model.DOMAIN_ROLES else 0
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )