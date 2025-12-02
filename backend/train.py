
import pandas as pd
import numpy as np
import pickle
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
import nltk
import warnings
import json
warnings.filterwarnings('ignore')

class CompleteJobRoleSystem:
    def __init__(self):
        self.job_roles_data = {}
        self.domain_to_roles = {}
        self.role_keywords = {}
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
        self.job_role_texts = []
        self.job_role_names = []
        self.results = []
        
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
        """Define all job roles with proper list format for all 22 domains"""
        # [Keep the same job structure as before - it's correct]
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
    
    def load_all_resumes(self, csv_path):
        """Load all resumes from dataset with correct column names and path handling"""
        print("📂 Loading resume dataset...")
        
        try:
            # Fix path issues - handle both forward and backward slashes
            csv_path = os.path.normpath(csv_path)
            
            # Check if file exists
            if not os.path.exists(csv_path):
                # Try to find the file in different locations
                possible_paths = [
                    csv_path,
                    os.path.join("data", csv_path),
                    os.path.join("dataset", "Resume", "Resume.csv"),
                    os.path.join("..", "dataset", "Resume", "Resume.csv"),
                    os.path.join(".", "dataset", "Resume", "Resume.csv")
                ]
                
                found_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        found_path = path
                        break
                
                if found_path:
                    csv_path = found_path
                    print(f"✅ Found CSV file at: {csv_path}")
                else:
                    raise FileNotFoundError(f"CSV file not found at any of these locations: {possible_paths}")
            
            print(f"📁 Attempting to load: {csv_path}")
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding)
                    print(f"✅ Successfully loaded with {encoding} encoding")
                    break
                except (UnicodeDecodeError, UnicodeError) as e:
                    print(f"❌ Failed with {encoding}: {e}")
                    continue
                except Exception as e:
                    print(f"❌ Unexpected error with {encoding}: {e}")
                    continue
            
            if df is None:
                raise ValueError("Could not read CSV file with any encoding")
            
            print(f"📊 CSV loaded successfully. Shape: {df.shape}")
            print(f"📋 Columns: {df.columns.tolist()}")
            
            # Validate required columns - check for case sensitivity and variations
            required_columns = ['ID', 'Resume_str', 'Resume_html', 'Category']
            available_columns = df.columns.tolist()
            
            # Check for case-insensitive matches
            column_mapping = {}
            for req_col in required_columns:
                for avail_col in available_columns:
                    if req_col.lower() == avail_col.lower():
                        column_mapping[req_col] = avail_col
                        break
            
            missing_columns = [col for col in required_columns if col not in column_mapping]
            
            if missing_columns:
                print(f"⚠️  Column mapping: {column_mapping}")
                print(f"⚠️  Available columns: {available_columns}")
                raise ValueError(f"Missing required columns: {missing_columns}. Available: {available_columns}")
            
            # Rename columns to standard names for easier processing
            df = df.rename(columns=column_mapping)
            
            # Clean data - use Resume_str for processing
            initial_count = len(df)
            print(f"📈 Initial resume count: {initial_count}")
            
            # Check for null values
            print(f"🔍 Null values - Resume_str: {df['Resume_str'].isna().sum()}, Category: {df['Category'].isna().sum()}")
            
            df = df.dropna(subset=['Resume_str', 'Category'])
            df = df[df['Resume_str'].str.strip() != '']
            df = df[df['Category'].str.strip() != '']
            
            final_count = len(df)
            removed_count = initial_count - final_count
            
            print(f"✅ Loaded {final_count} resumes (removed {removed_count} invalid entries)")
            
            if final_count == 0:
                raise ValueError("No valid resumes found after cleaning")
            
            print(f"📊 Domain distribution:")
            domain_counts = df['Category'].value_counts()
            print(domain_counts.head(15))  # Show top 15 domains
                
            return df
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            print("💡 Debug info:")
            print(f"   - Current working directory: {os.getcwd()}")
            print(f"   - Requested path: {csv_path}")
            print(f"   - Path exists: {os.path.exists(csv_path) if 'csv_path' in locals() else 'N/A'}")
            raise
    
    def prepare_job_role_corpus(self, job_structure):
        """Prepare job role descriptions for similarity matching"""
        print("🔄 Preparing job role corpus...")
        
        try:
            self.job_role_texts = []
            self.job_role_names = []
            self.role_keywords = {}
            self.domain_to_roles = {}
            
            role_count = 0
            for domain, roles in job_structure.items():
                for role_name, keywords in roles.items():
                    self.job_role_names.append(role_name)
                    # Convert list of keywords to space-separated string for TF-IDF
                    keyword_text = ' '.join(keywords)
                    self.job_role_texts.append(keyword_text)
                    self.role_keywords[role_name] = keywords  # Store as list for matching
                    
                    # Build domain to roles mapping
                    if domain not in self.domain_to_roles:
                        self.domain_to_roles[domain] = []
                    self.domain_to_roles[domain].append(role_name)
                    role_count += 1
            
            print(f"✅ Prepared {role_count} job roles across {len(self.domain_to_roles)} domains")
            
            # Show sample of roles
            print(f"🔍 Sample roles: {list(self.domain_to_roles.keys())[:5]}...")
            
        except Exception as e:
            print(f"❌ Error preparing job role corpus: {e}")
            raise
    
    def train_tfidf_model(self):
        """Train TF-IDF model safely"""
        print("🔄 Training TF-IDF model...")
        
        try:
            if len(self.job_role_texts) == 0:
                raise ValueError("No job role texts available for training")
            
            print(f"📝 Training on {len(self.job_role_texts)} job role descriptions")
            self.vectorizer.fit(self.job_role_texts)
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
            job_words = set(job_keywords)  # job_keywords is now a list
            
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
            
            return min(combined_score, 1.0)  # Ensure score doesn't exceed 1.0
            
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
            
            for role_name in self.job_role_names:
                job_keywords = self.role_keywords.get(role_name, [])
                match_score = self.calculate_keyword_match_score(cleaned_resume, job_keywords)
                
                # Find domain for this role
                domain = None
                for dom, roles in self.domain_to_roles.items():
                    if role_name in roles:
                        domain = dom
                        break
                
                match_scores.append({
                    'job_role': role_name,
                    'domain': domain,
                    'match_score': round(match_score * 100, 2),
                    'matching_keywords': list(set(cleaned_resume.split()) & set(job_keywords))[:5]  # Limit to 5 keywords
                })
            
            # Sort by match score and get top K
            match_scores.sort(key=lambda x: x['match_score'], reverse=True)
            top_roles = match_scores[:top_k]
            
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
    
    def train_and_evaluate_complete_system(self, csv_path):
        """Complete training and evaluation on all resumes"""
        print("🚀 Starting Complete Training & Evaluation System...")
        print("=" * 80)
        
        try:
            # Step 1: Ensure NLTK data
            self.ensure_nltk_data()
            
            # Step 2: Define job structure
            print("📋 Defining job structure...")
            job_structure = self.define_complete_job_structure()
            print(f"✅ Defined {len(job_structure)} domains")
            
            # Step 3: Prepare job role corpus
            self.prepare_job_role_corpus(job_structure)
            
            # Step 4: Train TF-IDF model
            self.train_tfidf_model()
            
            # Step 5: Load all resumes
            df = self.load_all_resumes(csv_path)
            
            # Step 6: Evaluate on all resumes
            print(f"\n🔍 Evaluating model on {len(df)} resumes...")
            self.results = []
            correct_predictions = 0
            domain_accuracy = defaultdict(lambda: {'correct': 0, 'total': 0})
            top_k_accuracy = {1: 0, 2: 0, 3: 0}
            
            for idx, row in df.iterrows():
                try:
                    resume_id = row['ID'] if 'ID' in row else idx
                    resume_text = row['Resume_str']  # Using Resume_str column
                    true_domain = row['Category']
                    
                    # Predict top job roles
                    top_roles, predicted_domain = self.predict_top_roles_for_resume(resume_text, top_k=3)
                    
                    # Check accuracy
                    is_correct = (predicted_domain == true_domain)
                    if is_correct:
                        correct_predictions += 1
                    
                    # Update Top-K accuracy
                    predicted_domains = [role['domain'] for role in top_roles if role['domain']]
                    for k in [1, 2, 3]:
                        if true_domain in predicted_domains[:k]:
                            top_k_accuracy[k] += 1
                    
                    # Store results
                    result = {
                        'resume_id': resume_id,
                        'true_domain': true_domain,
                        'predicted_domain': predicted_domain,
                        'is_correct': is_correct,
                        'top_roles': top_roles,
                        'top_role_names': [role['job_role'] for role in top_roles],
                        'top_role_scores': [role['match_score'] for role in top_roles]
                    }
                    self.results.append(result)
                    
                    # Update domain accuracy
                    domain_accuracy[true_domain]['total'] += 1
                    if is_correct:
                        domain_accuracy[true_domain]['correct'] += 1
                    
                    # Progress update
                    if (idx + 1) % 100 == 0:
                        current_accuracy = correct_predictions / (idx + 1)
                        print(f"   Processed {idx + 1}/{len(df)} resumes | Current Accuracy: {current_accuracy:.4f}")
                        
                except Exception as e:
                    print(f"⚠️  Error processing resume {idx}: {e}")
                    continue
            
            # Calculate final metrics
            total_resumes = len(self.results)
            if total_resumes == 0:
                raise ValueError("No results generated from evaluation")
            
            overall_accuracy = correct_predictions / total_resumes
            
            # Calculate domain-wise accuracy
            domain_wise_accuracy = {}
            for domain, stats in domain_accuracy.items():
                if stats['total'] > 0:
                    domain_wise_accuracy[domain] = {
                        'accuracy': stats['correct'] / stats['total'],
                        'correct': stats['correct'],
                        'total': stats['total']
                    }
            
            # Calculate Top-K accuracy percentages
            top_k_results = {}
            for k, count in top_k_accuracy.items():
                top_k_results[f'top_{k}'] = {
                    'accuracy': count / total_resumes,
                    'correct': count,
                    'total': total_resumes
                }
            
            return overall_accuracy, domain_wise_accuracy, top_k_results, df
            
        except Exception as e:
            print(f"❌ Error in training pipeline: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def generate_comprehensive_report(self, overall_accuracy, domain_accuracy, top_k_results, df):
        """Generate comprehensive evaluation report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TRAINING REPORT")
        print("="*80)
        
        # Overall metrics
        print(f"\n🎯 OVERALL PERFORMANCE:")
        print(f"   Resumes Processed: {len(df)}")
        print(f"   Overall Accuracy: {overall_accuracy:.4f} ({overall_accuracy*100:.2f}%)")
        
        # Top-K accuracy
        print(f"\n📈 TOP-K ACCURACY:")
        for k, result in top_k_results.items():
            acc_pct = result['accuracy'] * 100
            print(f"   {k.upper()}: {result['accuracy']:.4f} ({acc_pct:.2f}%) - {result['correct']}/{result['total']}")
        
        # Domain-wise accuracy (top 10 domains)
        print(f"\n🏢 DOMAIN-WISE ACCURACY (Top 10):")
        print("   Domain                Accuracy   Correct/Total")
        print("   " + "-" * 45)
        
        sorted_domains = sorted(domain_accuracy.items(), 
                              key=lambda x: x[1]['accuracy'], reverse=True)[:10]
        
        for domain, stats in sorted_domains:
            accuracy_pct = stats['accuracy'] * 100
            print(f"   {domain:<20} {accuracy_pct:6.2f}%     {stats['correct']:3d}/{stats['total']:3d}")
        
        # Performance summary
        high_acc = len([d for d, s in domain_accuracy.items() if s['accuracy'] >= 0.8])
        medium_acc = len([d for d, s in domain_accuracy.items() if 0.6 <= s['accuracy'] < 0.8])
        low_acc = len([d for d, s in domain_accuracy.items() if s['accuracy'] < 0.6])
        
        print(f"\n📋 PERFORMANCE SUMMARY:")
        print(f"   High Accuracy (≥80%): {high_acc} domains")
        print(f"   Medium Accuracy (60-80%): {medium_acc} domains")
        print(f"   Low Accuracy (<60%): {low_acc} domains")
    
    def save_complete_model(self, filepath='complete_job_matching_system.pkl'):
        """Save the complete trained system"""
        try:
            model_data = {
                'job_role_names': self.job_role_names,
                'job_role_texts': self.job_role_texts,
                'role_keywords': self.role_keywords,
                'domain_to_roles': self.domain_to_roles,
                'vectorizer': self.vectorizer
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            print(f"💾 Model saved to {filepath}")
            
        except Exception as e:
            print(f"❌ Error saving model: {e}")
            raise
    
    def save_evaluation_results(self, overall_accuracy, domain_accuracy, top_k_results, 
                              filepath='training_evaluation_report.json'):
        """Save detailed evaluation results"""
        try:
            results_data = {
                'training_info': {
                    'total_resumes_trained': len(self.results),
                    'total_job_roles': len(self.job_role_names),
                    'total_domains': len(self.domain_to_roles),
                    'overall_accuracy': overall_accuracy
                },
                'performance_metrics': {
                    'top_k_accuracy': top_k_results,
                    'domain_accuracy': {k: v for k, v in domain_accuracy.items()}
                }
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            print(f"📊 Evaluation report saved to {filepath}")
            
        except Exception as e:
            print(f"❌ Error saving evaluation results: {e}")

def main():
    """Main training and evaluation function"""
    print("🚀 Starting Robust Job Role Matching System Training")
    print("✅ Features: Error handling, Progress tracking, Accuracy evaluation")
    print("=" * 70)
    
    # Initialize system
    system = CompleteJobRoleSystem()
    
    # CSV path - FIXED PATH HANDLING
    csv_path = r"dataset\Resume\Resume.csv"  # Using raw string for Windows paths
    
    try:
        # Train and evaluate complete system
        overall_accuracy, domain_accuracy, top_k_results, df = system.train_and_evaluate_complete_system(csv_path)
        
        # Generate comprehensive report
        system.generate_comprehensive_report(overall_accuracy, domain_accuracy, top_k_results, df)
        
        # Save complete model
        system.save_complete_model('backend/complete_job_matching_system.pkl')
        
        # Save evaluation results
        system.save_evaluation_results(overall_accuracy, domain_accuracy, top_k_results,
                                     'backend/training_evaluation_report.json')
        
        # Final success message
        print(f"\n🎉 TRAINING COMPLETED SUCCESSFULLY!")
        print(f"📈 Final Accuracy: {overall_accuracy:.4f} ({overall_accuracy*100:.2f}%)")
        print(f"📁 Model saved: complete_job_matching_system.pkl")
        print(f"📋 Report saved: training_evaluation_report.json")
        
        # Test prediction
        print(f"\n🧪 Testing trained model...")
        test_text = "Python developer with django flask experience and machine learning"
        top_roles, predicted_domain = system.predict_top_roles_for_resume(test_text)
        if top_roles:
            print(f"   Test: '{test_text}'")
            print(f"   Predicted Domain: {predicted_domain}")
            print(f"   Top Role: {top_roles[0]['job_role']} ({top_roles[0]['match_score']}%)")
        
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        print("💡 Troubleshooting tips:")
        print("   1. Check if CSV file exists and path is correct")
        print("   2. Verify CSV has 'Resume_str' and 'Category' columns")
        print("   3. Ensure sufficient memory for 2400+ resumes")
        print("   4. Check file permissions in backend directory")
        print("   5. Try using forward slashes in path: dataset/Resume/Resume.csv")

if __name__ == "__main__":
    main()