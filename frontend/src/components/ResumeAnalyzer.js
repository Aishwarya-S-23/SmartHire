import React, { useState, useEffect } from 'react';

// Simple API service directly in the component
const API_BASE = "http://localhost:8000";

const apiService = {
  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  },

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
  },

  async analyzeResumeText(resumeText) {
    return await this.request('/analyze/text', {
      method: 'POST',
      body: JSON.stringify({ text: resumeText }),
    });
  },

  async analyzeResumeFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE}/analyze/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('File upload failed:', error);
      throw error;
    }
  }
};

const ResumeAnalyzer = () => {
    const [resumeText, setResumeText] = useState('');
    const [selectedFile, setSelectedFile] = useState(null);
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState('text');
    const [apiStatus, setApiStatus] = useState(null);

    // Check API health on component mount
    useEffect(() => {
        checkApiHealth();
    }, []);

    const checkApiHealth = async () => {
        try {
            const health = await apiService.healthCheck();
            setApiStatus(health);
        } catch (err) {
            setApiStatus({ status: 'error', message: 'Cannot connect to backend' });
        }
    };

    const handleTextAnalysis = async () => {
        if (!resumeText.trim()) {
            setError('Please enter resume text');
            return;
        }

        setLoading(true);
        setError('');
        setAnalysis(null);
        
        try {
            console.log("Sending analysis request...");
            const result = await apiService.analyzeResumeText(resumeText);
            console.log("Analysis result:", result);
            
            if (result.status === 'success') {
                setAnalysis(result);
            } else {
                setError(result.message || 'Analysis failed');
            }
        } catch (err) {
            console.error("Analysis error:", err);
            setError(err.message || 'Analysis failed. Please check if backend is running.');
        } finally {
            setLoading(false);
        }
    };

    const handleFileAnalysis = async () => {
        if (!selectedFile) {
            setError('Please select a file');
            return;
        }

        setLoading(true);
        setError('');
        setAnalysis(null);
        
        try {
            console.log("Sending file analysis request...");
            const result = await apiService.analyzeResumeFile(selectedFile);
            console.log("File analysis result:", result);
            
            if (result.status === 'success') {
                setAnalysis(result);
            } else {
                setError(result.message || 'File analysis failed');
            }
        } catch (err) {
            console.error("File analysis error:", err);
            setError(err.message || 'File analysis failed. Please check if backend is running.');
        } finally {
            setLoading(false);
        }
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        setSelectedFile(file);
        setError('');
    };

    const resetForm = () => {
        setResumeText('');
        setSelectedFile(null);
        setAnalysis(null);
        setError('');
    };

    return (
        <div className="resume-analyzer" style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
            <h2>Smart Hire - Resume Analysis</h2>
            
            {/* API Status */}
            {apiStatus && (
                <div style={{ 
                    padding: '10px', 
                    marginBottom: '20px', 
                    borderRadius: '5px',
                    backgroundColor: apiStatus.status === 'healthy' ? '#d4edda' : '#f8d7da',
                    color: apiStatus.status === 'healthy' ? '#155724' : '#721c24',
                    border: `1px solid ${apiStatus.status === 'healthy' ? '#c3e6cb' : '#f5c6cb'}`
                }}>
                    <strong>Backend Status:</strong> {apiStatus.status === 'healthy' ? '✅ Connected' : '❌ Disconnected'}
                    {apiStatus.message && ` - ${apiStatus.message}`}
                    {apiStatus.model_loaded !== undefined && (
                        <div>
                            <strong>Model:</strong> {apiStatus.model_loaded ? '✅ Loaded' : '❌ Not Loaded'}
                        </div>
                    )}
                </div>
            )}

            {/* Tabs */}
            <div className="tabs" style={{ marginBottom: '20px', borderBottom: '1px solid #ccc' }}>
                <button 
                    style={{ 
                        padding: '10px 20px', 
                        border: 'none', 
                        backgroundColor: activeTab === 'text' ? '#007bff' : 'transparent',
                        color: activeTab === 'text' ? 'white' : '#007bff',
                        cursor: 'pointer',
                        borderRadius: '5px 5px 0 0'
                    }}
                    onClick={() => setActiveTab('text')}
                >
                    📝 Text Input
                </button>
                <button 
                    style={{ 
                        padding: '10px 20px', 
                        border: 'none', 
                        backgroundColor: activeTab === 'file' ? '#007bff' : 'transparent',
                        color: activeTab === 'file' ? 'white' : '#007bff',
                        cursor: 'pointer',
                        borderRadius: '5px 5px 0 0'
                    }}
                    onClick={() => setActiveTab('file')}
                >
                    📎 File Upload
                </button>
            </div>

            {/* Text Input Tab */}
            {activeTab === 'text' && (
                <div className="tab-content">
                    <textarea
                        value={resumeText}
                        onChange={(e) => setResumeText(e.target.value)}
                        placeholder="Paste your resume text here... (Minimum 50 words for better results)"
                        rows="12"
                        style={{ 
                            width: '100%', 
                            padding: '10px', 
                            border: '1px solid #ddd',
                            borderRadius: '5px',
                            fontSize: '14px',
                            fontFamily: 'inherit'
                        }}
                    />
                    <button 
                        onClick={handleTextAnalysis} 
                        disabled={loading || !resumeText.trim()}
                        style={{ 
                            marginTop: '10px', 
                            padding: '10px 20px', 
                            backgroundColor: loading || !resumeText.trim() ? '#6c757d' : '#007bff',
                            color: 'white',
                            border: 'none',
                            borderRadius: '5px',
                            cursor: loading || !resumeText.trim() ? 'not-allowed' : 'pointer'
                        }}
                    >
                        {loading ? '🔍 Analyzing...' : '🚀 Analyze Resume'}
                    </button>
                </div>
            )}

            {/* File Upload Tab */}
            {activeTab === 'file' && (
                <div className="tab-content">
                    <div style={{ marginBottom: '15px' }}>
                        <input
                            type="file"
                            accept=".pdf,.docx,.doc"
                            onChange={handleFileChange}
                            style={{ marginBottom: '10px' }}
                        />
                        <div style={{ fontSize: '12px', color: '#666' }}>
                            Supported formats: PDF, DOCX, DOC (Max 10MB)
                        </div>
                    </div>
                    <button 
                        onClick={handleFileAnalysis} 
                        disabled={loading || !selectedFile}
                        style={{ 
                            padding: '10px 20px', 
                            backgroundColor: loading || !selectedFile ? '#6c757d' : '#007bff',
                            color: 'white',
                            border: 'none',
                            borderRadius: '5px',
                            cursor: loading || !selectedFile ? 'not-allowed' : 'pointer'
                        }}
                    >
                        {loading ? '🔍 Analyzing...' : '🚀 Analyze File'}
                    </button>
                    {selectedFile && (
                        <p style={{ marginTop: '10px' }}>📄 Selected: {selectedFile.name}</p>
                    )}
                </div>
            )}

            {/* Error Display */}
            {error && (
                <div style={{ 
                    color: '#721c24', 
                    backgroundColor: '#f8d7da',
                    border: '1px solid #f5c6cb',
                    padding: '10px',
                    borderRadius: '5px',
                    margin: '20px 0'
                }}>
                    ❌ Error: {error}
                </div>
            )}

            {/* Results Display */}
            {analysis && analysis.status === 'success' && (
                <div className="results" style={{ 
                    marginTop: '20px', 
                    padding: '20px', 
                    border: '1px solid #28a745',
                    borderRadius: '5px',
                    backgroundColor: '#f8fff9'
                }}>
                    <h3 style={{ color: '#28a745', marginBottom: '15px' }}>✅ Analysis Results</h3>
                    
                    <div style={{ marginBottom: '15px' }}>
                        <strong>Predicted Domain:</strong> 
                        <span style={{ 
                            backgroundColor: '#28a745', 
                            color: 'white', 
                            padding: '2px 8px', 
                            borderRadius: '15px',
                            marginLeft: '10px',
                            fontSize: '14px'
                        }}>
                            {analysis.domain_prediction} {/* Changed from predicted_domain */}
                        </span>
                    </div>
                    
                    <h4>Top 3 Job Role Matches:</h4>
                    {analysis.top_roles && analysis.top_roles.map((role, index) => (
                        <div key={index} style={{ 
                            marginBottom: '15px', 
                            padding: '15px', 
                            border: '1px solid #dee2e6',
                            borderRadius: '5px',
                            backgroundColor: 'white'
                        }}>
                            <p style={{ margin: '0 0 8px 0' }}>
                                <strong>{index + 1}. {role.job_role}</strong> 
                                <span style={{ 
                                    backgroundColor: '#17a2b8', 
                                    color: 'white', 
                                    padding: '2px 8px', 
                                    borderRadius: '15px',
                                    marginLeft: '10px',
                                    fontSize: '12px'
                                }}>
                                    {role.domain}
                                </span>
                            </p>
                            <p style={{ margin: '5px 0' }}>
                                <strong>Match Score:</strong> 
                                <span style={{ 
                                    fontWeight: 'bold',
                                    color: role.match_score > 70 ? '#28a745' : role.match_score > 50 ? '#ffc107' : '#dc3545',
                                    marginLeft: '5px'
                                }}>
                                    {role.match_score}%
                                </span>
                            </p>
                            {role.matching_keywords && role.matching_keywords.length > 0 && (
                                <p style={{ margin: '5px 0', fontSize: '14px' }}>
                                    <strong>Matching Keywords:</strong> 
                                    <span style={{ marginLeft: '5px' }}>
                                        {role.matching_keywords.map((keyword, idx) => (
                                            <span key={idx} style={{
                                                backgroundColor: '#e9ecef',
                                                padding: '2px 6px',
                                                borderRadius: '3px',
                                                margin: '0 2px',
                                                fontSize: '12px'
                                            }}>
                                                {keyword}
                                            </span>
                                        ))}
                                    </span>
                                </p>
                            )}
                        </div>
                    ))}
                    
                    <button 
                        onClick={resetForm} 
                        style={{ 
                            marginTop: '15px', 
                            padding: '8px 16px',
                            backgroundColor: '#6c757d',
                            color: 'white',
                            border: 'none',
                            borderRadius: '5px',
                            cursor: 'pointer'
                        }}
                    >
                        🔄 Analyze Another Resume
                    </button>
                </div>
            )}

            {/* No results or error in analysis */}
            {analysis && analysis.status === 'error' && (
                <div style={{ 
                    marginTop: '20px', 
                    padding: '15px', 
                    border: '1px solid #dc3545',
                    borderRadius: '5px',
                    backgroundColor: '#f8d7da',
                    color: '#721c24'
                }}>
                    ❌ Analysis failed: {analysis.message}
                </div>
            )}
        </div>
    );
};

export default ResumeAnalyzer;