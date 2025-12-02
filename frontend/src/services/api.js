const API_BASE = "http://localhost:8000";

class ApiService {
    constructor() {
        this.baseURL = API_BASE;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
                ...options,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Health check
    async healthCheck() {
        try {
            return await this.request('/health');
        } catch (error) {
            return {
                status: 'error',
                message: 'Cannot connect to backend service',
                model_loaded: false
            };
        }
    }

    // Get all domains
    async getDomains() {
        return await this.request('/domains');
    }

    // Get job roles
    async getJobRoles(domain = null) {
        const endpoint = domain ? `/job-roles?domain=${encodeURIComponent(domain)}` : '/job-roles';
        return await this.request(endpoint);
    }

    // Analyze resume text
    async analyzeResumeText(resumeText) {
        return await this.request('/analyze/text', {
            method: 'POST',
            body: JSON.stringify({ text: resumeText }),
        });
    }

    // Analyze uploaded resume file
    async analyzeResumeFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${this.baseURL}/analyze/upload`, {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('File upload failed:', error);
            throw error;
        }
    }

    // Get model info
    async getModelInfo() {
        return await this.request('/model-info');
    }
}

// Create singleton instance
const apiService = new ApiService();
export default apiService;