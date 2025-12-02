import pandas as pd
import numpy as np
import re
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

from data_loader import DataLoader

class SmartHireModel:
    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self.label_encoder = None
        self.is_trained = False
        self.data_loader = DataLoader()
        
        # Domain to Job Roles mapping with detailed skill requirements
        self.DOMAIN_ROLES = {
            'INFORMATION-TECHNOLOGY': {
                'Software Engineer': {
                    'skills': ['python', 'java', 'javascript', 'algorithms', 'data structures', 'software development', 'debugging', 'testing'],
                    'weight': 1.0
                },
                'Frontend Developer': {
                    'skills': ['javascript', 'react', 'html', 'css', 'typescript', 'responsive design', 'user interface', 'web development'],
                    'weight': 0.9
                },
                'Backend Developer': {
                    'skills': ['python', 'java', 'node.js', 'api', 'database', 'server', 'microservices', 'rest', 'graphql'],
                    'weight': 0.9
                },
                'Data Scientist': {
                    'skills': ['python', 'machine learning', 'statistics', 'data analysis', 'sql', 'tensorflow', 'pytorch', 'data visualization'],
                    'weight': 0.85
                },
                'DevOps Engineer': {
                    'skills': ['aws', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'terraform', 'linux', 'cloud', 'infrastructure'],
                    'weight': 0.8
                }
            },
            'ACCOUNTANT': {
                'Senior Accountant': {
                    'skills': ['accounting', 'financial reporting', 'gaap', 'general ledger', 'cpa', 'audit', 'tax preparation'],
                    'weight': 1.0
                },
                'Financial Analyst': {
                    'skills': ['financial analysis', 'excel', 'budgeting', 'forecasting', 'financial modeling', 'valuation'],
                    'weight': 0.9
                },
                'Tax Accountant': {
                    'skills': ['tax', 'taxation', 'irs', 'compliance', 'tax planning', 'tax returns'],
                    'weight': 0.85
                }
            },
            'ADVOCATE': {
                'Corporate Lawyer': {
                    'skills': ['corporate law', 'contracts', 'mergers', 'acquisitions', 'compliance', 'legal research'],
                    'weight': 1.0
                },
                'Litigation Lawyer': {
                    'skills': ['litigation', 'court', 'legal disputes', 'case preparation', 'trial', 'legal writing'],
                    'weight': 0.9
                },
                'Legal Advisor': {
                    'skills': ['legal counsel', 'contract review', 'regulatory compliance', 'risk management'],
                    'weight': 0.85
                }
            },
            'HEALTHCARE': {
                'Medical Doctor': {
                    'skills': ['medical', 'patient care', 'diagnosis', 'treatment', 'clinical', 'healthcare'],
                    'weight': 1.0
                },
                'Registered Nurse': {
                    'skills': ['nursing', 'patient care', 'medication', 'health assessment', 'clinical', 'healthcare'],
                    'weight': 0.9
                },
                'Healthcare Administrator': {
                    'skills': ['healthcare management', 'hospital operations', 'patient services', 'regulatory compliance'],
                    'weight': 0.8
                }
            },
            'HR': {
                'HR Manager': {
                    'skills': ['human resources', 'recruitment', 'employee relations', 'hr policies', 'talent management'],
                    'weight': 1.0
                },
                'Technical Recruiter': {
                    'skills': ['recruitment', 'talent acquisition', 'sourcing', 'interviewing', 'technical hiring'],
                    'weight': 0.9
                },
                'HR Business Partner': {
                    'skills': ['hr strategy', 'employee relations', 'performance management', 'organizational development'],
                    'weight': 0.85
                }
            },
            'ENGINEERING': {
                'Mechanical Engineer': {
                    'skills': ['mechanical', 'cad', 'solidworks', 'manufacturing', 'engineering design', 'thermodynamics'],
                    'weight': 1.0
                },
                'Civil Engineer': {
                    'skills': ['civil', 'structural', 'construction', 'autocad', 'project management', 'infrastructure'],
                    'weight': 0.9
                },
                'Electrical Engineer': {
                    'skills': ['electrical', 'circuits', 'power systems', 'electronics', 'embedded systems'],
                    'weight': 0.85
                }
            },
            'MARKETING': {
                'Digital Marketing Manager': {
                    'skills': ['digital marketing', 'seo', 'sem', 'social media', 'content strategy', 'google analytics'],
                    'weight': 1.0
                },
                'Content Marketing Specialist': {
                    'skills': ['content marketing', 'copywriting', 'seo', 'content strategy', 'social media'],
                    'weight': 0.9
                },
                'Social Media Manager': {
                    'skills': ['social media', 'community management', 'content creation', 'analytics', 'brand management'],
                    'weight': 0.85
                }
            }
        }
    
    # Remove the spaCy import at the top
# Change this line in train_model method:

# And in clean_text method, ensure it handles None:
    def clean_text(self, text):
        """Clean and preprocess text"""
        if not text or isinstance(text, float) and pd.isna(text):
            return ""
        
        text = str(text).lower()
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', '', text)
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        text = ' '.join(text.split())
        
        return text
    
    def train_model(self):
        """Train the domain classification model"""
        try:
            # Load dataset
            df = self.data_loader.load_dataset()
            
            print("🔄 Cleaning and preprocessing resumes...")
            df['cleaned_resume'] = df['resume_text'].apply(self.clean_text)
            
            # Encode domains
            self.label_encoder = LabelEncoder()
            df['domain_encoded'] = self.label_encoder.fit_transform(df['domain'])
            
            print(f"🎯 Training on {len(df)} resumes across {len(self.label_encoder.classes_)} domains")
            print("📊 Domain distribution:")
            print(df['domain'].value_counts())
            
            # Feature extraction
            self.vectorizer = TfidfVectorizer(
                max_features=2500,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95,
                sublinear_tf=True
            )
            
            X = self.vectorizer.fit_transform(df['cleaned_resume'])
            y = df['domain_encoded']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            print(f"📚 Training set: {X_train.shape[0]} samples")
            print(f"🧪 Testing set: {X_test.shape[0]} samples")
            
            # Train classifier
            self.classifier = MultinomialNB(alpha=0.1)
            self.classifier.fit(X_train, y_train)
            
            # Calculate accuracy
            y_pred = self.classifier.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"✅ Model trained successfully!")
            print(f"🎯 Overall Accuracy: {accuracy:.4f}")
            
            self.is_trained = True
            
            model_info = {
                "total_resumes": len(df),
                "domains": self.label_encoder.classes_.tolist(),
                "domain_counts": df['domain'].value_counts().to_dict(),
                "accuracy": round(accuracy, 4),
                "training_samples": X_train.shape[0],
                "testing_samples": X_test.shape[0]
            }
            
            return {
                "status": "success",
                "message": f"Model trained on {len(df)} resumes with {accuracy:.2%} accuracy",
                "model_info": model_info
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Training failed: {str(e)}"
            }
    
    def predict_domain(self, resume_text):
        """Predict the domain of a resume"""
        if not self.is_trained:
            return {
                "status": "error",
                "message": "Model not trained. Please train the model first."
            }
        
        try:
            # Clean and transform text
            cleaned_text = self.clean_text(resume_text)
            text_tfidf = self.vectorizer.transform([cleaned_text])
            
            # Get predictions and probabilities
            probabilities = self.classifier.predict_proba(text_tfidf)[0]
            predicted_idx = np.argmax(probabilities)
            predicted_domain = self.label_encoder.inverse_transform([predicted_idx])[0]
            confidence = probabilities[predicted_idx] * 100
            
            # Get top 3 domains with confidence scores
            top_3_indices = np.argsort(probabilities)[-3:][::-1]
            top_3_domains = self.label_encoder.inverse_transform(top_3_indices)
            top_3_confidences = probabilities[top_3_indices] * 100
            
            return {
                "status": "success",
                "domain_prediction": {
                    "primary_domain": predicted_domain,
                    "confidence": round(confidence, 2),
                    "top_domains": [
                        {"domain": domain, "confidence": round(conf, 2)} 
                        for domain, conf in zip(top_3_domains, top_3_confidences)
                    ]
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Domain prediction failed: {str(e)}"
            }
    
    def recommend_roles(self, resume_text, domain):
        """Recommend top 3 job roles within a domain based on skills"""
        if domain not in self.DOMAIN_ROLES:
            return {
                "status": "error",
                "message": f"No role data available for domain: {domain}"
            }
        
        try:
            cleaned_text = self.clean_text(resume_text)
            domain_roles = self.DOMAIN_ROLES[domain]
            
            role_scores = []
            
            for role, role_data in domain_roles.items():
                score = 0
                matched_skills = []
                
                # Calculate score based on skill matches
                for skill in role_data['skills']:
                    if skill in cleaned_text:
                        score += 3  # Base score for skill match
                        matched_skills.append(skill)
                
                # Apply role weight
                score *= role_data['weight']
                
                # Bonus for exact role mention
                if role.lower() in cleaned_text:
                    score += 10
                
                role_scores.append({
                    'role': role,
                    'score': score,
                    'matched_skills': matched_skills,
                    'total_skills_matched': len(matched_skills),
                    'total_skills_required': len(role_data['skills'])
                })
            
            # Sort by score and get top 3
            recommended_roles = sorted(role_scores, key=lambda x: x['score'], reverse=True)[:3]
            
            # Convert scores to confidence percentages
            max_score = max([role['score'] for role in recommended_roles]) if recommended_roles else 1
            for role in recommended_roles:
                confidence = min(95, (role['score'] / max(1, max_score)) * 100) if max_score > 0 else 60
                confidence = max(40, confidence)  # Minimum confidence threshold
                role['confidence'] = round(confidence, 2)
                del role['score']  # Remove raw score from response
            
            return {
                "status": "success",
                "recommended_roles": recommended_roles,
                "domain": domain
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Role recommendation failed: {str(e)}"
            }
    
    def full_analysis(self, resume_text):
        """Complete analysis: domain prediction + role recommendations"""
        # Step 1: Predict domain
        domain_result = self.predict_domain(resume_text)
        if domain_result['status'] == 'error':
            return domain_result
        
        primary_domain = domain_result['domain_prediction']['primary_domain']
        domain_confidence = domain_result['domain_prediction']['confidence']
        
        # Step 2: Recommend roles within the predicted domain
        role_result = self.recommend_roles(resume_text, primary_domain)
        
        return {
            "status": "success",
            "analysis": {
                "domain_prediction": domain_result['domain_prediction'],
                "role_recommendations": role_result.get('recommended_roles', []) if role_result['status'] == 'success' else [],
                "skills_analysis": self.extract_skills_analysis(resume_text)
            }
        }
    
    def extract_skills_analysis(self, resume_text):
        """Extract and analyze skills from resume"""
        cleaned_text = self.clean_text(resume_text)
        
        # Comprehensive skill categories
        skill_categories = {
            'Technical Skills': ['python', 'java', 'javascript', 'sql', 'aws', 'docker', 'react', 'node.js', 'machine learning'],
            'Soft Skills': ['leadership', 'communication', 'teamwork', 'problem solving', 'project management'],
            'Tools & Technologies': ['git', 'jenkins', 'tableau', 'power bi', 'jira', 'confluence'],
            'Domain Knowledge': ['financial analysis', 'medical', 'legal', 'marketing', 'engineering design']
        }
        
        found_skills = {}
        for category, skills in skill_categories.items():
            matched = [skill for skill in skills if skill in cleaned_text]
            if matched:
                found_skills[category] = matched
        
        return {
            'total_skills_identified': sum(len(skills) for skills in found_skills.values()),
            'skill_categories': found_skills
        }
    
    def get_domain_info(self):
        """Get information about available domains and roles"""
        if self.label_encoder:
            return {
                "domains": self.label_encoder.classes_.tolist(),
                "total_domains": len(self.label_encoder.classes_),
                "available_roles": {domain: list(roles.keys()) for domain, roles in self.DOMAIN_ROLES.items()}
            }
        return {"domains": [], "total_domains": 0}