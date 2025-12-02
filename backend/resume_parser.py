import pdfplumber
import docx
import re
import io

class ResumeParser:
    def __init__(self):
        self.skill_keywords = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'sql', 'html', 'css', 'react', 'angular', 'vue', 'node', 'typescript'],
            'data_science': ['machine learning', 'data analysis', 'statistics', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'sql', 'tableau', 'power bi'],
            'cloud_devops': ['aws', 'azure', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ci/cd', 'devops'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sql server'],
            'tools': ['git', 'jira', 'confluence', 'slack', 'docker', 'jenkins'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'problem solving', 'project management', 'agile', 'scrum'],
            'finance': ['financial analysis', 'accounting', 'cpa', 'gaap', 'quickbooks', 'tax preparation', 'auditing'],
            'healthcare': ['patient care', 'medical', 'nursing', 'healthcare', 'clinical', 'pharmacy', 'healthcare administration'],
            'marketing': ['digital marketing', 'seo', 'sem', 'social media', 'content marketing', 'google analytics'],
            'design': ['ui/ux', 'figma', 'adobe creative suite', 'graphic design', 'web design']
        }
    
    def extract_text_from_pdf(self, file_content):
        """Extract text from PDF file"""
        try:
            text = ""
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"PDF parsing error: {str(e)}")
    
    def extract_text_from_docx(self, file_content):
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text:
                    text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"DOCX parsing error: {str(e)}")
    
    def parse_resume(self, file_content, filename):
        """Parse resume file and extract text"""
        try:
            text = ""
            
            if filename.lower().endswith('.pdf'):
                text = self.extract_text_from_pdf(file_content)
            elif filename.lower().endswith(('.docx', '.doc')):
                text = self.extract_text_from_docx(file_content)
            else:
                # Assume it's text
                text = file_content.decode('utf-8', errors='ignore')
            
            # Clean the text
            text = self.clean_text(text)
            
            # Extract skills
            skills = self.extract_skills(text)
            
            return {
                'success': True,
                'text': text,
                'skills': skills,
                'word_count': len(text.split())
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def clean_text(self, text):
        """Clean and normalize resume text"""
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-]', ' ', text)
        return text.strip().lower()
    
    def extract_skills(self, text):
        """Extract skills from resume text"""
        found_skills = {}
        text_lower = text.lower()
        
        for category, skills in self.skill_keywords.items():
            category_skills = []
            for skill in skills:
                if skill in text_lower:
                    category_skills.append(skill.title())
            if category_skills:
                found_skills[category] = category_skills
        
        return found_skills