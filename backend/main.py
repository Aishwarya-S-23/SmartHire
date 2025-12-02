from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os
import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
import nltk
import warnings
from flask_cors import CORS

warnings.filterwarnings('ignore')

# Initialize Flask app
app = Flask(__name__)
CORS(app)

class CompleteJobRoleSystem:
    def __init__(self):
        self.job_roles_data = {}
        self.domain_to_roles = {}
        self.role_keywords = {}
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
        self.job_role_texts = []
        self.job_role_names = []
        self.results = []
        self.explainer = None
        self.feature_names = None
        self.use_lime = False
    
    def ensure_nltk_data(self):
        """Ensure NLTK data is available"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            print("📥 Downloading NLTK punkt...")
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            print("📥 Downloading NLTK stopwords...")
            nltk.download('stopwords', quiet=True)

    def define_complete_job_structure(self):
        """Define all job roles with proper list format for all domains"""
        job_structure = {
        'HR': {
            'HR Manager': ['recruitment', 'talent acquisition', 'employee relations', 'hr policies', 'performance management', 'team leadership'],
            'Recruitment Specialist': ['recruitment', 'sourcing', 'interviewing', 'candidate screening', 'job posting', 'applicant tracking'],
            'Training Manager': ['training', 'development', 'learning management', 'workshop facilitation', 'skill assessment', 'training needs'],
            'Compensation Analyst': ['compensation', 'benefits', 'payroll', 'salary benchmarking', 'reward systems', 'incentive plans'],
            'HR Business Partner': ['business partnership', 'strategic hr', 'organizational development', 'change management', 'stakeholder management'],
            'Talent Management Specialist': ['talent management', 'succession planning', 'career development', 'performance appraisal', 'talent retention'],
            'Employee Relations Manager': ['employee relations', 'conflict resolution', 'labor laws', 'grievance handling', 'disciplinary procedures'],
            'HR Analytics Specialist': ['hr analytics', 'data analysis', 'metrics', 'reporting', 'workforce planning', 'predictive analytics'],
            'Recruitment Coordinator': ['recruitment coordination', 'scheduling', 'onboarding', 'candidate communication', 'interview coordination'],
            'HR Generalist': ['hr operations', 'policy implementation', 'employee engagement', 'hr administration', 'payroll processing']
        },
        'Designer': {
            'UI/UX Designer': ['ui design', 'ux design', 'figma', 'user research', 'wireframing', 'prototyping'],
            'Graphic Designer': ['graphic design', 'adobe photoshop', 'illustrator', 'branding', 'visual design', 'layout'],
            'Product Designer': ['product design', 'user centered design', 'design thinking', 'interaction design', 'product strategy'],
            'Web Designer': ['web design', 'html', 'css', 'responsive design', 'wordpress', 'elementor'],
            'Motion Graphics Designer': ['motion graphics', 'after effects', 'animation', 'video editing', 'visual effects'],
            'Industrial Designer': ['industrial design', 'product design', 'cad', '3d modeling', 'prototyping', 'ergonomics'],
            'Fashion Designer': ['fashion design', 'textile', 'pattern making', 'fashion illustration', 'trend analysis'],
            'Interior Designer': ['interior design', 'space planning', 'autocad', '3d max', 'material selection'],
            'Game Designer': ['game design', 'game development', 'level design', 'game mechanics', 'unity'],
            'Creative Director': ['creative direction', 'brand strategy', 'art direction', 'team leadership', 'concept development']
        },
        'Information-Technology': {
            'Python Developer': ['python', 'django', 'flask', 'rest api', 'sql', 'git', 'numpy', 'pandas'],
            'Java Developer': ['java', 'spring boot', 'hibernate', 'microservices', 'maven', 'junit'],
            'Frontend Developer': ['javascript', 'react', 'html', 'css', 'redux', 'typescript', 'webpack'],
            'Data Scientist': ['python', 'machine learning', 'pandas', 'tensorflow', 'statistics', 'data analysis'],
            'DevOps Engineer': ['aws', 'docker', 'kubernetes', 'jenkins', 'linux', 'ci/cd', 'terraform'],
            'Full Stack Developer': ['javascript', 'node.js', 'react', 'mongodb', 'express', 'sql'],
            'Cloud Architect': ['aws', 'azure', 'cloud computing', 'terraform', 'networking', 'security'],
            'Mobile Developer': ['react native', 'android', 'ios', 'flutter', 'mobile development'],
            'QA Engineer': ['testing', 'selenium', 'automation', 'junit', 'test cases', 'quality assurance'],
            'Data Engineer': ['python', 'sql', 'etl', 'data pipeline', 'apache spark', 'hadoop']
        },
        'Teacher': {
            'Mathematics Teacher': ['mathematics', 'curriculum development', 'lesson planning', 'student assessment', 'algebra', 'calculus'],
            'Science Teacher': ['science', 'physics', 'chemistry', 'biology', 'laboratory', 'scientific methods'],
            'English Teacher': ['english', 'literature', 'grammar', 'language teaching', 'communication skills'],
            'Computer Science Teacher': ['computer science', 'programming', 'algorithms', 'computer fundamentals'],
            'Primary School Teacher': ['primary education', 'child development', 'classroom management', 'creative teaching'],
            'Special Education Teacher': ['special education', 'inclusive education', 'individualized education plans'],
            'University Professor': ['higher education', 'research', 'academic publishing', 'lecturing', 'mentoring'],
            'Music Teacher': ['music', 'instrument training', 'music theory', 'performance', 'vocal training'],
            'Physical Education Teacher': ['physical education', 'sports', 'fitness training', 'health education'],
            'Language Instructor': ['language teaching', 'linguistics', 'conversation practice', 'language proficiency']
        },
        'Advocate': {
            'Criminal Lawyer': ['criminal law', 'litigation', 'court procedures', 'legal research', 'case management'],
            'Corporate Lawyer': ['corporate law', 'contract drafting', 'mergers acquisitions', 'compliance', 'business law'],
            'Civil Lawyer': ['civil law', 'dispute resolution', 'property law', 'family law', 'legal documentation'],
            'Intellectual Property Lawyer': ['intellectual property', 'patents', 'trademarks', 'copyright', 'ip law'],
            'Tax Lawyer': ['tax law', 'tax planning', 'tax compliance', 'gst', 'income tax'],
            'Legal Advisor': ['legal advice', 'contract review', 'risk assessment', 'regulatory compliance'],
            'Public Prosecutor': ['prosecution', 'criminal justice', 'evidence', 'court proceedings'],
            'Immigration Lawyer': ['immigration law', 'visa processing', 'immigration compliance', 'citizenship'],
            'Environmental Lawyer': ['environmental law', 'sustainability', 'regulatory compliance', 'environmental policy'],
            'Labor Lawyer': ['labor law', 'employment law', 'industrial relations', 'wage compliance']
        },
        'Business-Development': {
            'Business Development Manager': ['business development', 'strategy', 'client acquisition', 'market research'],
            'Sales Manager': ['sales management', 'team leadership', 'revenue growth', 'customer relationship'],
            'Partnership Manager': ['partnerships', 'collaboration', 'strategic alliances', 'negotiation'],
            'Market Analyst': ['market research', 'competitive analysis', 'trend analysis', 'data interpretation'],
            'Product Manager': ['product management', 'product strategy', 'roadmapping', 'user research', 'agile'],
            'Strategy Consultant': ['strategic planning', 'business strategy', 'market analysis', 'competitive strategy'],
            'Account Manager': ['account management', 'client relations', 'customer success', 'account growth'],
            'Entrepreneur': ['business planning', 'startup', 'fundraising', 'innovation', 'leadership'],
            'Operations Manager': ['operations management', 'process improvement', 'efficiency', 'team management'],
            'Project Manager': ['project management', 'agile', 'scrum', 'budget management', 'stakeholder management']
        },
        'Healthcare': {
            'Medical Doctor': ['patient care', 'diagnosis', 'treatment', 'medical knowledge', 'healthcare'],
            'Registered Nurse': ['nursing', 'patient care', 'medication', 'health assessment', 'emergency care'],
            'Pharmacist': ['pharmacy', 'medicines', 'prescription', 'drug interactions', 'inventory'],
            'Medical Lab Technician': ['laboratory', 'diagnostic testing', 'specimen analysis', 'medical equipment'],
            'Physiotherapist': ['physical therapy', 'rehabilitation', 'exercise therapy', 'patient assessment'],
            'Healthcare Administrator': ['hospital management', 'healthcare operations', 'staff management', 'budgeting'],
            'Medical Researcher': ['clinical research', 'data analysis', 'research methodology', 'scientific writing'],
            'Radiologist': ['medical imaging', 'x-ray', 'mri', 'ct scan', 'diagnostic radiology'],
            'Nutritionist': ['diet planning', 'nutritional assessment', 'health education', 'meal planning'],
            'Medical Coder': ['medical coding', 'icd-10', 'billing', 'healthcare documentation', 'insurance']
        },
        'Fitness': {
            'Personal Trainer': ['personal training', 'fitness assessment', 'exercise programming', 'nutrition guidance'],
            'Yoga Instructor': ['yoga', 'meditation', 'flexibility training', 'mindfulness', 'asanas'],
            'Gym Manager': ['gym management', 'fitness operations', 'member services', 'facility management'],
            'Sports Coach': ['sports coaching', 'athlete training', 'performance analysis', 'team management'],
            'Nutrition Coach': ['nutrition coaching', 'diet planning', 'weight management', 'health assessment'],
            'Group Fitness Instructor': ['group fitness', 'class instruction', 'motivation', 'fitness programs'],
            'Physical Therapist': ['physical therapy', 'rehabilitation', 'injury prevention', 'therapeutic exercises'],
            'Sports Nutritionist': ['sports nutrition', 'athlete diet', 'performance nutrition', 'supplementation'],
            'Fitness Consultant': ['fitness consulting', 'program design', 'health assessment', 'wellness coaching'],
            'Athletic Trainer': ['athletic training', 'sports medicine', 'injury management', 'rehabilitation']
        },
        'Agriculture': {
            'Agricultural Engineer': ['agricultural engineering', 'farm machinery', 'irrigation systems', 'crop processing'],
            'Farm Manager': ['farm management', 'crop production', 'livestock management', 'agricultural operations'],
            'Agronomist': ['agronomy', 'soil science', 'crop management', 'plant nutrition', 'pest control'],
            'Horticulturist': ['horticulture', 'plant cultivation', 'landscaping', 'nursery management'],
            'Agricultural Scientist': ['agricultural research', 'crop science', 'plant breeding', 'sustainable agriculture'],
            'Livestock Specialist': ['livestock management', 'animal husbandry', 'veterinary care', 'breeding programs'],
            'Agricultural Economist': ['agricultural economics', 'market analysis', 'supply chain', 'farm budgeting'],
            'Organic Farming Specialist': ['organic farming', 'sustainable agriculture', 'soil health', 'natural pest control'],
            'Precision Agriculture Specialist': ['precision agriculture', 'gps technology', 'data analytics', 'farm automation'],
            'Food Processing Manager': ['food processing', 'quality control', 'food safety', 'processing technology']
        },
        'BPO': {
            'Customer Service Representative': ['customer service', 'call handling', 'problem solving', 'communication'],
            'Technical Support Specialist': ['technical support', 'troubleshooting', 'customer assistance', 'product knowledge'],
            'BPO Team Leader': ['team leadership', 'performance management', 'quality monitoring', 'process improvement'],
            'Operations Manager': ['operations management', 'process optimization', 'team management', 'kpi monitoring'],
            'Customer Experience Manager': ['customer experience', 'service quality', 'customer satisfaction', 'feedback analysis'],
            'Call Center Manager': ['call center management', 'workforce management', 'service level agreement'],
            'Quality Analyst': ['quality assurance', 'process compliance', 'performance monitoring', 'feedback coaching'],
            'Training Coordinator': ['training', 'onboarding', 'skill development', 'process training'],
            'Workforce Manager': ['workforce management', 'scheduling', 'capacity planning', 'attendance management'],
            'Client Services Manager': ['client management', 'account management', 'service delivery', 'relationship management']
        },
        'Sales': {
            'Sales Executive': ['sales', 'lead generation', 'client acquisition', 'negotiation', 'relationship building'],
            'Account Executive': ['account management', 'client relations', 'revenue generation', 'sales strategy'],
            'Sales Manager': ['sales management', 'team leadership', 'target achievement', 'sales planning'],
            'Business Development Executive': ['business development', 'market expansion', 'partnerships', 'revenue growth'],
            'Retail Sales Associate': ['retail sales', 'customer service', 'product knowledge', 'point of sale'],
            'Sales Consultant': ['sales consulting', 'solution selling', 'client advisory', 'needs analysis'],
            'Channel Sales Manager': ['channel sales', 'distribution management', 'partner development', 'channel strategy'],
            'Inside Sales Representative': ['inside sales', 'tele sales', 'lead qualification', 'remote selling'],
            'Key Account Manager': ['key account management', 'strategic accounts', 'relationship management', 'account growth'],
            'Sales Operations Analyst': ['sales operations', 'data analysis', 'sales metrics', 'process optimization']
        },
        'Consultant': {
            'Management Consultant': ['management consulting', 'business strategy', 'process improvement', 'organizational change'],
            'IT Consultant': ['it consulting', 'technology advisory', 'system implementation', 'digital transformation'],
            'Financial Consultant': ['financial consulting', 'investment advisory', 'financial planning', 'wealth management'],
            'HR Consultant': ['hr consulting', 'talent management', 'organizational development', 'hr transformation'],
            'Marketing Consultant': ['marketing consulting', 'brand strategy', 'digital marketing', 'market research'],
            'Operations Consultant': ['operations consulting', 'process optimization', 'efficiency improvement', 'supply chain'],
            'Strategy Consultant': ['strategic planning', 'market analysis', 'competitive strategy', 'business planning'],
            'Technology Consultant': ['technology consulting', 'digital solutions', 'system architecture', 'tech advisory'],
            'Business Consultant': ['business consulting', 'performance improvement', 'change management', 'business analysis'],
            'SAP Consultant': ['sap', 'erp implementation', 'business process', 'sap modules']
        },
        'Digital-Media': {
            'Digital Marketing Manager': ['digital marketing', 'seo', 'social media', 'content strategy', 'analytics'],
            'Social Media Manager': ['social media management', 'content creation', 'community management', 'social analytics'],
            'Content Strategist': ['content strategy', 'content marketing', 'editorial planning', 'seo content'],
            'SEO Specialist': ['seo', 'search engine optimization', 'keyword research', 'link building', 'analytics'],
            'Video Producer': ['video production', 'video editing', 'script writing', 'video marketing', 'production'],
            'Graphic Designer': ['graphic design', 'adobe creative suite', 'visual design', 'branding', 'layout'],
            'Web Content Manager': ['content management', 'web content', 'cms', 'content publishing', 'seo'],
            'Media Planner': ['media planning', 'advertising', 'media buying', 'campaign management', 'audience analysis'],
            'Digital Analyst': ['digital analytics', 'web analytics', 'data analysis', 'reporting', 'kpi tracking'],
            'UX Writer': ['ux writing', 'content design', 'microcopy', 'user experience', 'content strategy']
        },
        'Automobile': {
            'Automotive Engineer': ['automotive engineering', 'vehicle design', 'cad', 'automotive systems', 'testing'],
            'Automotive Technician': ['automotive repair', 'diagnostics', 'maintenance', 'vehicle systems', 'troubleshooting'],
            'Service Advisor': ['service advisory', 'customer service', 'maintenance scheduling', 'repair estimation'],
            'Auto Electrician': ['auto electrical', 'wiring', 'electrical systems', 'diagnostics', 'repair'],
            'Quality Control Inspector': ['quality control', 'inspection', 'quality assurance', 'defect analysis'],
            'Production Supervisor': ['production supervision', 'manufacturing', 'assembly line', 'quality control'],
            'Automotive Designer': ['automotive design', 'styling', 'cad', '3d modeling', 'concept development'],
            'Parts Manager': ['parts management', 'inventory', 'supply chain', 'parts identification', 'ordering'],
            'Service Manager': ['service management', 'workshop operations', 'team management', 'customer satisfaction'],
            'Diagnostic Technician': ['diagnostics', 'troubleshooting', 'electronic systems', 'problem solving']
        },
        'Chef': {
            'Executive Chef': ['culinary arts', 'kitchen management', 'menu planning', 'food costing', 'team leadership'],
            'Sous Chef': ['food preparation', 'cooking', 'kitchen operations', 'recipe development', 'quality control'],
            'Pastry Chef': ['baking', 'pastry', 'desserts', 'cake decoration', 'baking techniques'],
            'Line Cook': ['cooking', 'food preparation', 'kitchen operations', 'recipe following', 'safety standards'],
            'Food Stylist': ['food styling', 'photography', 'presentation', 'creative plating', 'visual appeal'],
            'Catering Manager': ['catering', 'event planning', 'menu design', 'client coordination', 'logistics'],
            'Recipe Developer': ['recipe development', 'food testing', 'culinary innovation', 'flavor profiling'],
            'Kitchen Manager': ['kitchen management', 'inventory', 'staff scheduling', 'cost control', 'sanitation'],
            'Nutritional Chef': ['nutrition', 'healthy cooking', 'dietary planning', 'wellness cuisine'],
            'Banquet Chef': ['banquet operations', 'large scale cooking', 'event catering', 'buffet management']
        },
        'Finance': {
            'Financial Analyst': ['financial modeling', 'excel', 'financial analysis', 'reporting', 'forecasting'],
            'Investment Banker': ['investment banking', 'mergers acquisitions', 'financial markets', 'valuation'],
            'Accountant': ['accounting', 'tally', 'gst', 'taxation', 'financial statements'],
            'Auditor': ['auditing', 'internal controls', 'compliance', 'risk assessment', 'gaap'],
            'Wealth Manager': ['wealth management', 'investment planning', 'portfolio management', 'financial advisory'],
            'Risk Analyst': ['risk management', 'risk assessment', 'financial risk', 'compliance', 'analytics'],
            'Tax Consultant': ['taxation', 'tax planning', 'gst', 'income tax', 'tax compliance'],
            'Financial Planner': ['financial planning', 'investment advisory', 'retirement planning', 'estate planning'],
            'Credit Analyst': ['credit analysis', 'lending', 'risk assessment', 'financial statements', 'banking'],
            'Actuary': ['actuarial science', 'risk modeling', 'statistics', 'insurance', 'probability']
        },
        'Apparel': {
            'Fashion Designer': ['fashion design', 'textile', 'pattern making', 'fashion illustration', 'trend analysis'],
            'Merchandiser': ['merchandising', 'inventory management', 'product assortment', 'visual merchandising'],
            'Production Manager': ['production management', 'garment manufacturing', 'quality control', 'supply chain'],
            'Textile Designer': ['textile design', 'fabric development', 'printing', 'weaving', 'material knowledge'],
            'Quality Control Manager': ['quality control', 'garment inspection', 'quality standards', 'defect analysis'],
            'Retail Store Manager': ['retail management', 'store operations', 'team leadership', 'customer service'],
            'Fashion Buyer': ['fashion buying', 'vendor management', 'trend analysis', 'purchasing', 'inventory'],
            'Pattern Maker': ['pattern making', 'grading', 'drafting', 'garment construction', 'technical drawing'],
            'Fashion Stylist': ['fashion styling', 'wardrobe consulting', 'personal styling', 'trend forecasting'],
            'Apparel Technologist': ['apparel technology', 'fabric testing', 'product development', 'technical specifications']
        },
        'Engineering': {
            'Mechanical Engineer': ['mechanical design', 'autocad', 'solidworks', 'thermodynamics', 'manufacturing'],
            'Civil Engineer': ['civil engineering', 'construction', 'project management', 'structural design', 'autocad'],
            'Electrical Engineer': ['electrical systems', 'circuit design', 'power systems', 'matlab', 'automation'],
            'Software Engineer': ['software development', 'programming', 'algorithms', 'data structures', 'debugging'],
            'Chemical Engineer': ['chemical processes', 'process engineering', 'safety protocols', 'chemical reactions'],
            'Aerospace Engineer': ['aerospace', 'aircraft design', 'aerodynamics', 'propulsion', 'avionics'],
            'Biomedical Engineer': ['biomedical', 'medical devices', 'physiology', 'biomechanics', 'fda regulations'],
            'Environmental Engineer': ['environmental science', 'sustainability', 'waste management', 'regulatory compliance'],
            'Industrial Engineer': ['industrial processes', 'optimization', 'production planning', 'quality control'],
            'Robotics Engineer': ['robotics', 'automation', 'control systems', 'artificial intelligence', 'mechatronics']
        },
        'Accountant': {
            'Chartered Accountant': ['chartered accountancy', 'auditing', 'taxation', 'financial reporting', 'compliance'],
            'Management Accountant': ['management accounting', 'cost accounting', 'budgeting', 'financial analysis'],
            'Tax Accountant': ['tax accounting', 'tax preparation', 'gst', 'income tax', 'tax compliance'],
            'Forensic Accountant': ['forensic accounting', 'fraud examination', 'investigation', 'legal support'],
            'Financial Accountant': ['financial accounting', 'financial statements', 'gaap', 'reporting', 'reconciliation'],
            'Cost Accountant': ['cost accounting', 'cost analysis', 'budgeting', 'cost control', 'profitability analysis'],
            'Audit Manager': ['audit management', 'internal audit', 'risk assessment', 'compliance', 'audit planning'],
            'Accounts Payable Specialist': ['accounts payable', 'invoice processing', 'payment processing', 'vendor management'],
            'Accounts Receivable Specialist': ['accounts receivable', 'collections', 'billing', 'customer accounts'],
            'Payroll Administrator': ['payroll processing', 'payroll taxes', 'employee benefits', 'payroll compliance']
        },
        'Construction': {
            'Project Manager': ['project management', 'construction management', 'budgeting', 'scheduling', 'team leadership'],
            'Site Engineer': ['site engineering', 'construction supervision', 'quality control', 'safety compliance'],
            'Civil Engineer': ['civil engineering', 'structural design', 'autocad', 'construction methods', 'site inspection'],
            'Architect': ['architecture', 'building design', 'autocad', 'revit', 'construction documents'],
            'Quantity Surveyor': ['quantity surveying', 'cost estimation', 'tender documents', 'bill of quantities'],
            'Safety Manager': ['safety management', 'osh standards', 'risk assessment', 'safety training', 'compliance'],
            'Construction Supervisor': ['construction supervision', 'workforce management', 'progress monitoring', 'quality control'],
            'MEP Engineer': ['mep engineering', 'mechanical electrical plumbing', 'building systems', 'coordination'],
            'Construction Estimator': ['cost estimation', 'bid preparation', 'material takeoff', 'pricing'],
            'Site Manager': ['site management', 'operations management', 'resource allocation', 'progress reporting']
        },
        'Public-Relations': {
            'PR Manager': ['public relations', 'media relations', 'crisis management', 'brand reputation', 'communication'],
            'Communications Specialist': ['corporate communications', 'internal communications', 'content creation', 'messaging'],
            'Media Relations Manager': ['media relations', 'press releases', 'media pitching', 'journalist relations'],
            'Event Manager': ['event management', 'event planning', 'logistics', 'vendor management', 'coordination'],
            'Brand Manager': ['brand management', 'brand strategy', 'brand positioning', 'brand communication'],
            'Corporate Communications Manager': ['corporate communications', 'stakeholder communication', 'crisis communication'],
            'PR Consultant': ['pr consulting', 'strategy development', 'campaign management', 'reputation management'],
            'Social Media PR Specialist': ['social media pr', 'online reputation', 'social listening', 'community management'],
            'Crisis Communications Manager': ['crisis communication', 'issues management', 'risk mitigation', 'response planning'],
            'PR Account Executive': ['account management', 'client servicing', 'campaign execution', 'media monitoring']
        },
        'Banking': {
            'Relationship Manager': ['relationship management', 'client servicing', 'banking products', 'customer relationship'],
            'Loan Officer': ['loan processing', 'credit analysis', 'underwriting', 'lending', 'documentation'],
            'Branch Manager': ['branch management', 'banking operations', 'team leadership', 'customer service'],
            'Investment Advisor': ['investment advisory', 'portfolio management', 'financial planning', 'wealth management'],
            'Risk Manager': ['risk management', 'credit risk', 'market risk', 'compliance', 'risk assessment'],
            'Operations Manager': ['banking operations', 'process management', 'compliance', 'operational efficiency'],
            'Treasury Manager': ['treasury management', 'cash management', 'liquidity management', 'foreign exchange'],
            'Compliance Officer': ['compliance', 'regulatory compliance', 'aml', 'kyc', 'banking regulations'],
            'Private Banker': ['private banking', 'wealth management', 'high net worth', 'investment advisory'],
            'Credit Analyst': ['credit analysis', 'financial analysis', 'risk assessment', 'lending decisions']
        },
        'Arts': {
            'Visual Artist': ['visual arts', 'painting', 'drawing', 'artistic techniques', 'creative expression'],
            'Art Director': ['art direction', 'creative direction', 'visual design', 'team leadership', 'concept development'],
            'Gallery Manager': ['gallery management', 'art curation', 'exhibition planning', 'artist relations'],
            'Art Teacher': ['art education', 'art instruction', 'technique teaching', 'creative development'],
            'Illustrator': ['illustration', 'digital art', 'drawing', 'visual storytelling', 'character design'],
            'Sculptor': ['sculpture', '3d art', 'material knowledge', 'spatial design', 'artistic techniques'],
            'Art Conservator': ['art conservation', 'restoration', 'preservation', 'art history', 'conservation techniques'],
            'Muralist': ['mural painting', 'large scale art', 'public art', 'wall painting', 'community art'],
            'Printmaker': ['printmaking', 'printing techniques', 'editioning', 'traditional print methods'],
            'Art Therapist': ['art therapy', 'therapeutic techniques', 'mental health', 'creative expression therapy']
        },
        'Aviation': {
            'Commercial Pilot': ['commercial pilot', 'flight operations', 'aviation safety', 'navigation', 'cockpit procedures'],
            'Aircraft Maintenance Engineer': ['aircraft maintenance', 'aviation maintenance', 'troubleshooting', 'safety standards'],
            'Air Traffic Controller': ['air traffic control', 'radar operations', 'flight safety', 'communication', 'coordination'],
            'Flight Attendant': ['flight attending', 'customer service', 'safety procedures', 'cabin crew', 'hospitality'],
            'Aviation Manager': ['aviation management', 'airport operations', 'airline management', 'regulatory compliance'],
            'Aerospace Engineer': ['aerospace engineering', 'aircraft design', 'avionics', 'propulsion systems'],
            'Flight Dispatcher': ['flight dispatch', 'flight planning', 'weather analysis', 'fuel calculation', 'safety'],
            'Aviation Safety Inspector': ['aviation safety', 'safety inspection', 'regulatory compliance', 'safety audits'],
            'Airport Operations Manager': ['airport operations', 'terminal management', 'ground handling', 'security operations'],
            'Cabin Crew Manager': ['cabin crew management', 'training', 'scheduling', 'performance management']
        }
    }
        
        # Build the data structures
        self.job_roles_data = job_structure
        self.domain_to_roles = {}
        self.role_keywords = {}
        self.job_role_names = []
        self.job_role_texts = []
        
        for domain, roles in job_structure.items():
            self.domain_to_roles[domain] = list(roles.keys())
            for role_name, keywords in roles.items():
                self.role_keywords[role_name] = keywords
                self.job_role_names.append(role_name)
                # Create a text representation for TF-IDF
                role_text = f"{role_name} {' '.join(keywords)} {domain}"
                self.job_role_texts.append(role_text)
        
        print(f"✅ Defined {len(self.job_role_names)} job roles across {len(self.domain_to_roles)} domains")
        return job_structure

    def clean_text(self, text):
        """Clean and preprocess text safely"""
        try:
            if pd.isna(text) or text is None:
                return ""
            
            text = str(text).lower()
            text = re.sub(r'<.*?>', '', text)
            text = re.sub(r'http\S+', '', text)
            text = re.sub(r'[^a-zA-Z\s]', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        except Exception as e:
            print(f"⚠️  Text cleaning error: {e}")
            return ""

    def load_complete_model(self, model_path=None):
        """Complete model loading with comprehensive error handling"""
        try:
            print("🔄 Initializing job matching system...")
            
            # Ensure NLTK data is available
            self.ensure_nltk_data()
            
            # If no pre-trained model, use the default job structure
            self.define_complete_job_structure()
            
            # Train TF-IDF model
            self.train_tfidf_model()
            
            print(f"✅ System initialized with {len(self.job_role_names)} job roles")
            print(f"✅ Loaded {len(self.domain_to_roles)} domains")
            print(f"✅ TF-IDF vectorizer trained on {len(self.job_role_texts)} role descriptions")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            import traceback
            traceback.print_exc()
            return False

    def validate_loaded_model(self):
        """Validate that all required model components are loaded"""
        required_components = {
            'job_role_names': self.job_role_names,
            'role_keywords': self.role_keywords,
            'domain_to_roles': self.domain_to_roles,
            'vectorizer': self.vectorizer
        }
        
        for name, component in required_components.items():
            if not component:
                print(f"⚠️ Missing component: {name}")
                return False
        
        print(f"✅ Model validated: {len(self.job_role_names)} roles, {len(self.domain_to_roles)} domains")
        return True

    def train_tfidf_model(self):
        """Train TF-IDF model"""
        print("🔄 Training TF-IDF model...")
        
        try:
            if len(self.job_role_texts) == 0:
                raise ValueError("No job role texts available for training")
            
            print(f"📝 Training on {len(self.job_role_texts)} job role descriptions")
            self.vectorizer.fit(self.job_role_texts)
            
            # Create feature names
            self.feature_names = self.vectorizer.get_feature_names_out()
            
            print("✅ TF-IDF model trained successfully")
            
        except Exception as e:
            print(f"❌ Error training TF-IDF model: {e}")
            raise

    def calculate_keyword_match_score(self, resume_text, job_keywords):
        """Calculate match score based on keyword overlap safely"""
        try:
            if not resume_text or not job_keywords:
                return 0.0
            
            resume_words = set(resume_text.lower().split())
            job_words = set(job_keywords)
            
            if not job_words:
                return 0.0
            
            # Calculate Jaccard similarity
            intersection = len(resume_words.intersection(job_words))
            union = len(resume_words.union(job_words))
            
            if union == 0:
                return 0.0
            
            jaccard_similarity = intersection / union
            
            # Calculate keyword coverage
            keyword_coverage = intersection / len(job_words)
            
            # Combined score (weighted average)
            combined_score = (jaccard_similarity * 0.4) + (keyword_coverage * 0.6)
            
            return min(combined_score, 1.0)
            
        except Exception as e:
            print(f"⚠️  Match score calculation error: {e}")
            return 0.0

    def predict_top_roles_for_resume(self, resume_text, top_k=3):
        """Predict top job roles for a single resume safely"""
        try:
            cleaned_resume = self.clean_text(resume_text)
            
            if not cleaned_resume or len(cleaned_resume.split()) < 5:
                return [], "Unknown"
            
            # Calculate match scores for all job roles
            match_scores = []
            
            for role_idx, role_name in enumerate(self.job_role_names):
                job_keywords = self.role_keywords.get(role_name, [])
                match_score = self.calculate_keyword_match_score(cleaned_resume, job_keywords)
                
                # Find domain for this role
                domain = None
                for dom, roles in self.domain_to_roles.items():
                    if role_name in roles:
                        domain = dom
                        break
                
                # Get matching keywords (actual matches)
                resume_words = set(cleaned_resume.split())
                job_keyword_set = set(job_keywords)
                matching_keywords = list(resume_words.intersection(job_keyword_set))[:5]
                
                match_scores.append({
                    'job_role': role_name,
                    'domain': domain,
                    'match_score': round(match_score * 100, 2),
                    'matching_keywords': matching_keywords,
                    'role_index': role_idx
                })
            
            # Sort by match score and get top K
            match_scores.sort(key=lambda x: x['match_score'], reverse=True)
            top_roles = match_scores[:top_k]
            
            # Generate explanations for top roles
            for role in top_roles:
                explanation = self.explain_prediction(cleaned_resume, role['role_index'])
                role['explanation'] = explanation
            
            # Predict domain from top roles
            predicted_domain = self.predict_domain_from_roles(top_roles)
            
            return top_roles, predicted_domain
            
        except Exception as e:
            print(f"⚠️  Prediction error: {e}")
            return [], "Unknown"

    def predict_domain_from_roles(self, top_roles):
        """Predict domain based on top job roles safely"""
        try:
            if not top_roles:
                return "Unknown"
            
            # Count domain occurrences in top roles
            domain_counts = defaultdict(int)
            for role in top_roles:
                if role['domain']:
                    domain_counts[role['domain']] += 1
            
            if not domain_counts:
                return "Unknown"
            
            # Return domain with highest count
            predicted_domain = max(domain_counts.items(), key=lambda x: x[1])[0]
            return predicted_domain
            
        except Exception as e:
            print(f"⚠️  Domain prediction error: {e}")
            return "Unknown"

    def get_all_domains(self):
        """Get all available domains"""
        return list(self.domain_to_roles.keys()) if self.domain_to_roles else []

    def get_roles_by_domain(self, domain):
        """Get all roles for a specific domain"""
        return self.domain_to_roles.get(domain, [])

    def get_role_details(self, role_name):
        """Get details for a specific role"""
        return {
            'keywords': self.role_keywords.get(role_name, []),
            'domain': next((dom for dom, roles in self.domain_to_roles.items() if role_name in roles), None)
        }

    def explain_prediction(self, resume_text, top_role_index):
        """Generate explanation for why a role was predicted"""
        try:
            return self.explain_with_keywords(resume_text, top_role_index)
                
        except Exception as e:
            print(f"⚠️  Explanation generation failed: {e}")
            return self.explain_with_keywords(resume_text, top_role_index)

    def explain_with_keywords(self, resume_text, top_role_index):
        """Fallback keyword-based explanation"""
        try:
            role_name = self.job_role_names[top_role_index]
            job_keywords = self.role_keywords.get(role_name, [])
            
            resume_words = set(resume_text.lower().split())
            matched_keywords = [kw for kw in job_keywords if kw in resume_words]
            
            explanations = []
            if matched_keywords:
                # Calculate impact based on keyword importance
                total_keywords = len(job_keywords)
                impact_per_keyword = 1.0 / len(matched_keywords) if matched_keywords else 0
                
                for keyword in matched_keywords[:5]:
                    # Give more weight to keywords that appear earlier in the list (assumed more important)
                    keyword_index = job_keywords.index(keyword) if keyword in job_keywords else len(job_keywords)
                    importance_weight = 1.0 - (keyword_index / total_keywords) * 0.5
                    
                    explanations.append({
                        'feature': keyword,
                        'impact': impact_per_keyword * importance_weight,
                        'normalized_impact': impact_per_keyword * importance_weight
                    })
                
                # Normalize the impacts to sum to 1
                total_impact = sum(exp['impact'] for exp in explanations)
                if total_impact > 0:
                    for exp in explanations:
                        exp['normalized_impact'] = exp['impact'] / total_impact
            
            return {
                'method': 'Keyword Matching',
                'explanations': explanations,
                'total_impact': 1.0 if explanations else 0
            }
            
        except Exception as e:
            print(f"⚠️  Keyword explanation failed: {e}")
            return {
                'method': 'Basic',
                'explanations': [],
                'total_impact': 0
            }

# Global system instance
job_system = CompleteJobRoleSystem()

def load_job_matching_system():
    """Load the job matching system with error handling"""
    print("🚀 Loading Job Role Matching System...")
    print("=" * 50)
    
    # Try to load pre-trained model
    model_loaded = job_system.load_complete_model()
    
    if model_loaded:
        if job_system.validate_loaded_model():
            print("🎉 System loaded successfully!")
            return True
        else:
            print("❌ Loaded model validation failed")
            return False
    else:
        print("❌ No pre-trained model found or model loading failed")
        return False

# Load the system when the app starts
system_loaded = load_job_matching_system()

# Flask Routes
@app.route('/')
def home():
    return jsonify({
        "message": "Smart Hire Job Matching System API",
        "status": "running",
        "model_loaded": system_loaded,
        "endpoints": {
            "/predict": "POST - Predict job roles from resume text",
            "/domains": "GET - Get all available domains",
            "/health": "GET - Health check",
            "/roles/<domain>": "GET - Get roles by domain",
            "/role/<role_name>": "GET - Get role details",
            "/explain": "POST - Explain prediction",
            "/demo": "GET - Demo predictions"
        }
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "model_loaded": system_loaded,
        "domains_loaded": len(job_system.get_all_domains()) if system_loaded else 0,
        "roles_loaded": len(job_system.job_role_names) if system_loaded else 0
    })

@app.route('/domains')
def get_domains():
    if not system_loaded:
        return jsonify({"error": "Model not loaded"}), 500
    
    domains = job_system.get_all_domains()
    return jsonify({
        "domains": domains,
        "count": len(domains)
    })

@app.route('/predict', methods=['POST'])
def predict_job_roles():
    if not system_loaded:
        return jsonify({"error": "Model not loaded. Please train the model first."}), 500
    
    try:
        data = request.get_json()
        
        if not data or 'resume_text' not in data:
            return jsonify({"error": "Missing 'resume_text' in request body"}), 400
        
        resume_text = data['resume_text']
        top_k = data.get('top_k', 3)
        
        if not resume_text or len(resume_text.strip()) < 10:
            return jsonify({"error": "Resume text too short"}), 400
        
        # Make prediction
        top_roles, predicted_domain = job_system.predict_top_roles_for_resume(resume_text, top_k=top_k)
        
        # Prepare response
        response = {
            "predicted_domain": predicted_domain,
            "top_roles": top_roles,
            "resume_length": len(resume_text),
            "top_k": top_k
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@app.route('/roles/<domain>')
def get_roles_by_domain(domain):
    if not system_loaded:
        return jsonify({"error": "Model not loaded"}), 500
    
    roles = job_system.get_roles_by_domain(domain)
    if not roles:
        return jsonify({"error": f"Domain '{domain}' not found"}), 404
    
    return jsonify({
        "domain": domain,
        "roles": roles,
        "count": len(roles)
    })

@app.route('/role/<role_name>')
def get_role_details(role_name):
    if not system_loaded:
        return jsonify({"error": "Model not loaded"}), 500
    
    role_details = job_system.get_role_details(role_name)
    if not role_details['keywords']:
        return jsonify({"error": f"Role '{role_name}' not found"}), 404
    
    return jsonify({
        "role": role_name,
        "details": role_details
    })

@app.route('/explain', methods=['POST'])
def explain_prediction():
    if not system_loaded:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        data = request.get_json()
        
        if not data or 'resume_text' not in data or 'role_name' not in data:
            return jsonify({"error": "Missing 'resume_text' or 'role_name' in request body"}), 400
        
        resume_text = data['resume_text']
        role_name = data['role_name']
        
        if not resume_text or len(resume_text.strip()) < 10:
            return jsonify({"error": "Resume text too short"}), 400
        
        # Find the role index
        role_index = None
        for idx, name in enumerate(job_system.job_role_names):
            if name == role_name:
                role_index = idx
                break
        
        if role_index is None:
            return jsonify({"error": f"Role '{role_name}' not found"}), 404
        
        # Generate explanation
        explanation = job_system.explain_prediction(resume_text, role_index)
        
        return jsonify({
            "role_name": role_name,
            "explanation": explanation,
            "resume_length": len(resume_text)
        })
        
    except Exception as e:
        return jsonify({"error": f"Explanation failed: {str(e)}"}), 500

@app.route('/demo')
def demo_predictions():
    if not system_loaded:
        return jsonify({"error": "Model not loaded"}), 500
    
    demo_resumes = [
        "Python developer with django flask experience and machine learning data science pandas numpy",
        "Graphic designer with adobe photoshop illustrator and UI UX design skills",
        "HR manager with talent acquisition recruitment and employee relations experience",
        "Sales executive with lead generation client acquisition and negotiation skills",
        "Financial analyst with excel financial modeling and data analysis experience"
    ]
    
    results = []
    for i, resume_text in enumerate(demo_resumes):
        top_roles, predicted_domain = job_system.predict_top_roles_for_resume(resume_text)
        results.append({
            "demo_id": i + 1,
            "resume_sample": resume_text[:50] + "...",
            "predicted_domain": predicted_domain,
            "top_role": top_roles[0]['job_role'] if top_roles else "None",
            "top_score": top_roles[0]['match_score'] if top_roles else 0
        })
    
    return jsonify({
        "demo_predictions": results,
        "system_info": {
            "domains": len(job_system.get_all_domains()),
            "roles": len(job_system.job_role_names)
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Smart Hire Flask Server...")
    print(f"📊 Model loaded: {system_loaded}")
    if system_loaded:
        print(f"🏢 Domains available: {len(job_system.get_all_domains())}")
        print(f"💼 Job roles available: {len(job_system.job_role_names)}")
    
    print("\n🌐 Server running on: http://localhost:5000")
    print("📚 Available endpoints:")
    print("   - GET  /health - System health check")
    print("   - GET  /domains - List all domains")
    print("   - POST /predict - Analyze resume text")
    print("   - GET  /demo - Demo predictions")
    print("\n⚡ Ready to process requests!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)