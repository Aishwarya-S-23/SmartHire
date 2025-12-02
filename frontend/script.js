// API Configuration
const API_BASE_URL = 'http://localhost:5000';

// Application State
let currentFile = null;
let analysisHistory = [];
let currentAnalysisData = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    setupEventListeners();
    await checkSystemStatus();
    updateDashboardStats();
    updateRecentlyAssigned();
    
    // Set up periodic status checks
    setInterval(checkSystemStatus, 30000);
}

// Navigation and UI Management
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Remove active class from all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Show selected section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Activate corresponding nav item
    const navItem = document.querySelector(`.nav-item[onclick="showSection('${sectionId}')"]`);
    if (navItem) {
        navItem.classList.add('active');
    }
}

// Setup event listeners
function setupEventListeners() {
    // File input handlers
    const singleFileInput = document.getElementById('singleFileInput');
    const batchFileInput = document.getElementById('batchFileInput');
    
    if (singleFileInput) {
        singleFileInput.addEventListener('change', handleSingleFileSelect);
    }
    if (batchFileInput) {
        batchFileInput.addEventListener('change', handleBatchFileSelect);
    }
    
    // Analyze buttons
    const analyzeSingleBtn = document.getElementById('analyzeSingleBtn');
    const analyzeBatchBtn = document.getElementById('analyzeBatchBtn');
    
    if (analyzeSingleBtn) {
        analyzeSingleBtn.addEventListener('click', handleSingleAnalysis);
    }
    if (analyzeBatchBtn) {
        analyzeBatchBtn.addEventListener('click', handleBatchAnalysis);
    }
    
    // Setup drag and drop
    setupDragAndDrop();
}

// Drag and drop setup
function setupDragAndDrop() {
    const singleUploadArea = document.getElementById('singleUploadArea');
    const batchUploadArea = document.getElementById('batchUploadArea');
    
    if (singleUploadArea) {
        setupDragDropArea(singleUploadArea, 'single');
    }
    if (batchUploadArea) {
        setupDragDropArea(batchUploadArea, 'batch');
    }
}

function setupDragDropArea(area, type) {
    area.addEventListener('dragover', (e) => {
        e.preventDefault();
        area.style.borderColor = 'var(--primary-blue)';
        area.style.background = '#f0f7ff';
    });
    
    area.addEventListener('dragleave', () => {
        area.style.borderColor = 'var(--border-medium)';
        area.style.background = 'var(--bg-light)';
    });
    
    area.addEventListener('drop', (e) => {
        e.preventDefault();
        area.style.borderColor = 'var(--border-medium)';
        area.style.background = 'var(--bg-light)';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            if (type === 'single') {
                processSingleFile(files[0]);
            } else {
                handleBatchFileSelect({ target: { files: files } });
            }
        }
    });
}

// File selection handlers
function handleSingleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        processSingleFile(file);
    }
}

function handleBatchFileSelect(event) {
    const files = event.target.files;
    if (files.length > 0) {
        const fileNames = Array.from(files).map(f => f.name).join(', ');
        const batchFileNames = document.getElementById('batchFileNames');
        if (batchFileNames) {
            batchFileNames.textContent = `Selected ${files.length} files: ${fileNames}`;
        }
        const analyzeBatchBtn = document.getElementById('analyzeBatchBtn');
        if (analyzeBatchBtn) {
            analyzeBatchBtn.disabled = false;
        }
    }
}

function processSingleFile(file) {
    currentFile = file;
    
    // Update UI
    const singleFileName = document.getElementById('singleFileName');
    if (singleFileName) {
        singleFileName.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    }
    
    // Read file content for text area
    const reader = new FileReader();
    reader.onload = function(e) {
        const resumeText = document.getElementById('resumeText');
        if (resumeText) {
            resumeText.value = e.target.result;
        }
    };
    reader.onerror = function(e) {
        console.error('Error reading file:', e);
        const resumeText = document.getElementById('resumeText');
        if (resumeText) {
            resumeText.value = `Unable to read file: ${file.name}`;
        }
    };
    
    if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
        reader.readAsText(file);
    } else {
        const resumeText = document.getElementById('resumeText');
        if (resumeText) {
            resumeText.value = `File: ${file.name}\nType: ${file.type || 'Unknown'}\nSize: ${(file.size / 1024).toFixed(1)} KB\n\nPlease paste resume text below for analysis.`;
        }
    }
}

// Analysis handlers
async function handleSingleAnalysis() {
    const resumeTextElement = document.getElementById('resumeText');
    if (!resumeTextElement) return;
    
    const resumeText = resumeTextElement.value.trim();
    
    if (!resumeText) {
        alert('Please provide resume text to analyze. Either upload a file or paste text in the text area.');
        return;
    }
    
    if (resumeText.length < 20) {
        alert('Please provide more resume text (at least 20 characters).');
        return;
    }
    
    await analyzeResume(resumeText);
}

async function handleBatchAnalysis() {
    alert('Batch analysis feature is coming soon. For now, please use single resume analysis.');
}

// Main analysis function
async function analyzeResume(resumeText) {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                resume_text: resumeText,
                top_k: 5
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server returned ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        
        // Store in history
        analysisHistory.unshift({
            timestamp: new Date().toISOString(),
            data: data,
            resumePreview: resumeText.substring(0, 100) + '...'
        });
        
        // Store current analysis data
        currentAnalysisData = data;
        
        // Show results
        showSection('analysisResults');
        displayResults(data);
        
        // Update dashboard
        updateDashboardStats();
        
    } catch (error) {
        console.error('Analysis failed:', error);
        alert(`Analysis failed: ${error.message}\n\nPlease make sure:\n• Backend server is running on http://localhost:5000\n• No firewall is blocking the connection`);
    } finally {
        hideLoading();
    }
}

// Display results
function displayResults(data) {
    if (!data || !data.top_roles || data.top_roles.length === 0) {
        const resultsContainer = document.querySelector('.results-container');
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="no-results">
                    <h3>No Suitable Roles Found</h3>
                    <p>The resume content didn't match any of our predefined roles. Try adding more specific skills and experience details.</p>
                </div>
            `;
        }
        return;
    }
    
    const topRole = data.top_roles[0];
    const candidateName = currentFile ? currentFile.name.replace(/\.[^/.]+$/, "") : 'Candidate';
    
    // Update candidate info
    updateElementText('candidateName', `${candidateName} - Analysis Results`);
    updateElementText('candidateDetails', `Analyzed ${new Date().toLocaleDateString()}`);
    updateElementText('analysisTime', 'Just now');
    
    // Set confidence level
    const confidenceLevel = topRole.match_score >= 80 ? 'High Confidence' : 
                           topRole.match_score >= 60 ? 'Medium Confidence' : 'Low Confidence';
    updateElementText('analysisConfidence', confidenceLevel);
    
    // Primary recommendation
    updateElementText('primaryRoleName', topRole.job_role);
    updateElementText('primaryDomain', formatDomainName(topRole.domain));
    updateElementText('topConfidence', `${topRole.match_score}% Match`);
    updateElementText('roleDescription', 
        `Excellent match based on ${topRole.matching_keywords ? topRole.matching_keywords.length : 0} key skills alignment`);
    
    // Skills breakdown
    displaySkillsBreakdown(data);
    
    // Alternative recommendations
    displayAlternativeRecommendations(data.top_roles.slice(1));
    
    // AI Explanation Dashboard
    displayAIExplanations(data);
}

function updateElementText(elementId, text) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = text;
    }
}

// Display skills breakdown
function displaySkillsBreakdown(data) {
    const skillsGrid = document.getElementById('skillsGrid');
    if (!skillsGrid) return;
    
    const topRole = data.top_roles[0];
    
    if (!topRole.matching_keywords || topRole.matching_keywords.length === 0) {
        skillsGrid.innerHTML = `
            <div class="skill-item">
                <span class="skill-name">No specific skills identified</span>
                <span class="skill-match status-low">0%</span>
            </div>
        `;
        return;
    }
    
    const skills = topRole.matching_keywords.map(skill => ({
        name: skill,
        match: Math.min(95, 70 + Math.random() * 25) // Random match percentage for demo
    }));
    
    skillsGrid.innerHTML = skills.map(skill => `
        <div class="skill-item">
            <span class="skill-name">${skill.name}</span>
            <span class="skill-match status-${getMatchLevel(skill.match)}">${Math.round(skill.match)}%</span>
        </div>
    `).join('');
}

// Display alternative recommendations
function displayAlternativeRecommendations(alternativeRoles) {
    const recommendationsGrid = document.getElementById('recommendationsGrid');
    if (!recommendationsGrid) return;
    
    if (!alternativeRoles || alternativeRoles.length === 0) {
        recommendationsGrid.innerHTML = `
            <div class="recommendation-card">
                <p>No alternative roles found</p>
            </div>
        `;
        return;
    }
    
    recommendationsGrid.innerHTML = alternativeRoles.map(role => `
        <div class="recommendation-card">
            <div class="recommendation-card-header">
                <div class="recommendation-role">${role.job_role}</div>
                <div class="recommendation-match status-${getMatchLevel(role.match_score)}">
                    ${role.match_score}% Match
                </div>
            </div>
            <div class="recommendation-domain">${formatDomainName(role.domain)}</div>
            ${role.matching_keywords && role.matching_keywords.length > 0 ? `
                <div class="recommendation-skills">
                    ${role.matching_keywords.slice(0, 3).map(skill => 
                        `<span class="skill-tag">${skill}</span>`
                    ).join('')}
                    ${role.matching_keywords.length > 3 ? 
                        `<span class="skill-tag">+${role.matching_keywords.length - 3} more</span>` : ''
                    }
                </div>
            ` : ''}
            <div class="recommendation-actions">
                <button class="btn btn-primary btn-small" onclick="assignRole('${role.job_role}', ${role.match_score}, '${role.domain}')">
                    <i class="fas fa-user-check"></i> Assign
                </button>
                <button class="btn btn-secondary btn-small" onclick="viewRoleDetails('${role.job_role}')">
                    <i class="fas fa-info-circle"></i> Details
                </button>
            </div>
        </div>
    `).join('');
}

// Display AI explanations
function displayAIExplanations(data) {
    const explanationDashboard = document.querySelector('.explanation-dashboard');
    if (!explanationDashboard) return;
    
    const topRole = data.top_roles[0];
    
    if (topRole.explanation) {
        displayPrimaryExplanation(topRole);
        displayComparisonExplanations(data.top_roles);
        displayFeaturesBreakdown(data.top_roles);
    } else {
        // Generate fallback explanations
        const fallbackExplanation = generateFallbackExplanation(topRole);
        displayPrimaryExplanation({...topRole, explanation: fallbackExplanation});
        displayComparisonExplanations(data.top_roles.map(role => ({
            ...role, 
            explanation: role.explanation || generateFallbackExplanation(role)
        })));
        displayFeaturesBreakdown(data.top_roles.map(role => ({
            ...role,
            explanation: role.explanation || generateFallbackExplanation(role)
        })));
    }
}

function generateFallbackExplanation(role) {
    const matchedKeywords = role.matching_keywords || [];
    const explanations = matchedKeywords.map((keyword, index) => ({
        feature: keyword,
        impact: (1 / matchedKeywords.length) * (1 - index * 0.1),
        normalized_impact: (1 / matchedKeywords.length) * (1 - index * 0.1)
    }));
    
    return {
        method: 'Keyword Matching',
        explanations: explanations,
        total_impact: 1.0
    };
}

// Display primary explanation
function displayPrimaryExplanation(role) {
    const explanation = role.explanation;
    
    // Update explanation method
    const explanationMethod = document.getElementById('explanationMethod');
    if (explanationMethod) {
        explanationMethod.textContent = `${explanation.method} Analysis`;
    }
    
    // Display impact chart
    displayImpactChart(explanation.explanations, 'primaryImpactChart');
    
    // Display explanation summary
    displayExplanationSummary(role, explanation);
}

// Display impact chart
function displayImpactChart(explanations, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (!explanations || explanations.length === 0) {
        container.innerHTML = `
            <div class="no-explanation">
                <i class="fas fa-chart-bar"></i>
                <h5>No Detailed Analysis Available</h5>
                <p>Analysis is based on overall keyword matching and skill alignment.</p>
            </div>
        `;
        return;
    }
    
    // Sort by impact and take top 6
    const topExplanations = explanations
        .sort((a, b) => b.normalized_impact - a.normalized_impact)
        .slice(0, 6);
    
    container.innerHTML = topExplanations.map(exp => `
        <div class="impact-bar">
            <div class="feature-name">${exp.feature}</div>
            <div class="impact-bar-container">
                <div class="impact-bar-fill" style="width: ${exp.normalized_impact * 100}%">
                    <span class="impact-value">${(exp.normalized_impact * 100).toFixed(1)}%</span>
                </div>
            </div>
            <div class="impact-percentage">${(exp.normalized_impact * 100).toFixed(1)}%</div>
        </div>
    `).join('');
}

// Display explanation summary
function displayExplanationSummary(role, explanation) {
    const summaryContainer = document.getElementById('primaryExplanationSummary');
    if (!summaryContainer) return;
    
    const topFeatures = explanation.explanations.slice(0, 3);
    
    if (topFeatures.length === 0) {
        summaryContainer.innerHTML = `
            <h6>Analysis Summary:</h6>
            <p>The AI recommended <strong>${role.job_role}</strong> based on overall keyword matching and skill alignment with the role requirements.</p>
        `;
        return;
    }
    
    const featureList = topFeatures.map(exp => 
        `<strong>${exp.feature}</strong> (${(exp.normalized_impact * 100).toFixed(1)}%)`
    ).join(', ');
    
    summaryContainer.innerHTML = `
        <h6>Key Influencing Factors:</h6>
        <p>The AI recommended <strong>${role.job_role}</strong> primarily because of ${featureList}. 
        These features showed the strongest alignment with the role requirements.</p>
    `;
}

// Display comparison explanations
function displayComparisonExplanations(roles) {
    const comparisonContainer = document.getElementById('comparisonChart');
    if (!comparisonContainer) return;
    
    comparisonContainer.innerHTML = roles.map(role => {
        const topFeatures = role.explanation?.explanations?.slice(0, 3) || [];
        
        return `
            <div class="comparison-item">
                <div class="comparison-role-header">
                    <div class="comparison-role-name">${role.job_role}</div>
                    <div class="comparison-match-score confidence-${getMatchLevel(role.match_score)}">
                        ${role.match_score}% Match
                    </div>
                </div>
                <div class="comparison-features">
                    ${topFeatures.length > 0 ? 
                        topFeatures.map(exp => 
                            `<span class="comparison-feature">${exp.feature} (${(exp.normalized_impact * 100).toFixed(0)}%)</span>`
                        ).join('') :
                        '<span class="comparison-feature">Overall skill alignment</span>'
                    }
                </div>
                <div class="comparison-method">${role.explanation?.method || 'Keyword Analysis'}</div>
            </div>
        `;
    }).join('');
}

// Display features breakdown
function displayFeaturesBreakdown(roles) {
    const featuresContainer = document.getElementById('featuresBreakdown');
    if (!featuresContainer) return;
    
    // Collect all unique features across roles
    const allFeatures = new Map();
    
    roles.forEach(role => {
        if (role.explanation?.explanations) {
            role.explanation.explanations.forEach(exp => {
                if (allFeatures.has(exp.feature)) {
                    const existing = allFeatures.get(exp.feature);
                    existing.impact += exp.normalized_impact;
                    existing.count += 1;
                    if (!existing.roles.includes(role.job_role)) {
                        existing.roles.push(role.job_role);
                    }
                } else {
                    allFeatures.set(exp.feature, {
                        impact: exp.normalized_impact,
                        count: 1,
                        roles: [role.job_role],
                        method: role.explanation.method
                    });
                }
            });
        }
    });
    
    // Convert to array and sort by impact
    const featuresArray = Array.from(allFeatures.entries())
        .map(([feature, data]) => ({
            feature,
            impact: data.impact,
            count: data.count,
            roles: data.roles,
            method: data.method
        }))
        .sort((a, b) => b.impact - a.impact)
        .slice(0, 6);
    
    if (featuresArray.length === 0) {
        featuresContainer.innerHTML = `
            <div class="no-features">
                <i class="fas fa-puzzle-piece"></i>
                <h5>No Feature Analysis</h5>
                <p>Feature importance analysis requires detailed explanation data.</p>
            </div>
        `;
        return;
    }
    
    featuresContainer.innerHTML = featuresArray.map(feature => `
        <div class="feature-card">
            <h6>${feature.feature}</h6>
            <div class="feature-impact">${(feature.impact * 100).toFixed(1)}%</div>
            <div class="feature-description">
                Influenced ${feature.count} role${feature.count > 1 ? 's' : ''}
                <br>
                <small>${feature.method}</small>
            </div>
        </div>
    `).join('');
}

// Explanation tab management
function showExplanationTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.explanation-tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.explanation-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab
    const tabElement = document.getElementById(tabName + 'Explanation');
    if (tabElement) {
        tabElement.classList.add('active');
    }
    
    // Activate corresponding tab button
    const tabButton = document.querySelector(`.explanation-tab[onclick="showExplanationTab('${tabName}')"]`);
    if (tabButton) {
        tabButton.classList.add('active');
    }
}

// Role assignment function
function assignRole(roleType, matchScore, domain) {
    let roleName, confidence;
    
    if (roleType === 'primary') {
        const primaryRole = currentAnalysisData.top_roles[0];
        roleName = primaryRole.job_role;
        confidence = primaryRole.match_score;
        domain = primaryRole.domain;
    } else {
        roleName = roleType;
        confidence = matchScore;
    }
    
    // Add to recently assigned
    const newAssignment = {
        id: Date.now(),
        candidateName: currentFile ? currentFile.name.replace(/\.[^/.]+$/, "") : 'Candidate',
        role: roleName,
        domain: domain,
        confidence: confidence,
        assignedDate: new Date().toISOString(),
        status: 'Assigned'
    };
    
    // Save to localStorage (in real app, this would be API call)
    let assignments = JSON.parse(localStorage.getItem('recentAssignments') || '[]');
    assignments.unshift(newAssignment);
    // Keep only last 10 assignments
    assignments = assignments.slice(0, 10);
    localStorage.setItem('recentAssignments', JSON.stringify(assignments));
    
    // Show success message
    showNotification(`Successfully assigned ${roleName} to candidate`, 'success');
    
    // Update recently assigned section
    updateRecentlyAssigned();
    
    // Optionally redirect to recently assigned section
    setTimeout(() => showSection('recentAssigned'), 1500);
}

// View role details
function viewRoleDetails(roleName) {
    const modalContent = `
        <h3>${roleName} - Role Details</h3>
        <div class="role-details">
            <p><strong>Required Skills:</strong></p>
            <ul>
                <li>Technical proficiency in relevant technologies</li>
                <li>Problem-solving abilities</li>
                <li>Team collaboration skills</li>
                <li>Communication skills</li>
            </ul>
            <p><strong>Typical Responsibilities:</strong></p>
            <ul>
                <li>Develop and maintain software applications</li>
                <li>Collaborate with cross-functional teams</li>
                <li>Participate in code reviews</li>
                <li>Contribute to technical documentation</li>
            </ul>
        </div>
        <div class="modal-actions">
            <button class="btn btn-primary" onclick="closeModal()">Close</button>
        </div>
    `;
    
    showModal('Role Details', modalContent);
}

// Action panel functions
function scheduleInterview() {
    showNotification('Interview scheduling interface opened', 'info');
}

function saveToTalentPool() {
    showNotification('Candidate saved to talent pool database', 'success');
}

function generateReport() {
    showNotification('PDF report generation started', 'info');
}

function shareResults() {
    showNotification('Share options displayed', 'info');
}

function saveAllRecommendations() {
    showNotification('All recommendations saved to candidate profile', 'success');
}

// Modal management
function showModal(title, content) {
    let modal = document.getElementById('modalOverlay');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modalOverlay';
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close" onclick="closeModal()">&times;</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('modalOverlay');
    if (modal) {
        modal.style.display = 'none';
    }
}

// System status check
async function checkSystemStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            updateStatusElement('modelStatus', 'Ready', 'ready');
            updateStatusElement('apiStatus', 'Connected', 'ready');
            return true;
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.error('Status check failed:', error);
        updateStatusElement('modelStatus', 'Offline', 'loading');
        updateStatusElement('apiStatus', 'Disconnected', 'loading');
        return false;
    }
}

function updateStatusElement(elementId, text, className) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = text;
        element.className = `status-indicator ${className}`;
    }
}

// Update dashboard statistics
function updateDashboardStats() {
    updateElementText('totalCandidates', analysisHistory.length);
}

// Update recently assigned section
function updateRecentlyAssigned() {
    const assignments = JSON.parse(localStorage.getItem('recentAssignments') || '[]');
    const assignmentsGrid = document.querySelector('.assignments-grid');
    
    if (assignmentsGrid) {
        if (assignments.length === 0) {
            // Show default assignments if none exist
            assignmentsGrid.innerHTML = `
                <div class="assignment-card">
                    <div class="candidate-info">
                        <div class="candidate-avatar">
                            <i class="fas fa-user-tie"></i>
                        </div>
                        <div class="candidate-details">
                            <h4>Sarah Chen</h4>
                            <p class="candidate-role">Senior Data Scientist</p>
                        </div>
                    </div>
                    <div class="assignment-details">
                        <div class="match-score high">98% Match</div>
                        <div class="assigned-role">Data Science Team</div>
                        <div class="assignment-date">Assigned: Today</div>
                    </div>
                </div>
                <div class="assignment-card">
                    <div class="candidate-info">
                        <div class="candidate-avatar">
                            <i class="fas fa-user-tie"></i>
                        </div>
                        <div class="candidate-details">
                            <h4>Marcus Johnson</h4>
                            <p class="candidate-role">Full Stack Developer</p>
                        </div>
                    </div>
                    <div class="assignment-details">
                        <div class="match-score high">95% Match</div>
                        <div class="assigned-role">Web Development</div>
                        <div class="assignment-date">Assigned: 2 days ago</div>
                    </div>
                </div>
                <div class="assignment-card">
                    <div class="candidate-info">
                        <div class="candidate-avatar">
                            <i class="fas fa-user-tie"></i>
                        </div>
                        <div class="candidate-details">
                            <h4>Emily Rodriguez</h4>
                            <p class="candidate-role">UX Designer</p>
                        </div>
                    </div>
                    <div class="assignment-details">
                        <div class="match-score medium">88% Match</div>
                        <div class="assigned-role">Design Team</div>
                        <div class="assignment-date">Assigned: 3 days ago</div>
                    </div>
                </div>
            `;
        } else {
            assignmentsGrid.innerHTML = assignments.map(assignment => `
                <div class="assignment-card">
                    <div class="candidate-info">
                        <div class="candidate-avatar">
                            <i class="fas fa-user-tie"></i>
                        </div>
                        <div class="candidate-details">
                            <h4>${assignment.candidateName}</h4>
                            <p class="candidate-role">${assignment.role}</p>
                        </div>
                    </div>
                    <div class="assignment-details">
                        <div class="match-score ${getMatchLevel(assignment.confidence)}">${assignment.confidence}% Match</div>
                        <div class="assigned-role">${formatDomainName(assignment.domain)}</div>
                        <div class="assignment-date">Assigned: ${new Date(assignment.assignedDate).toLocaleDateString()}</div>
                    </div>
                </div>
            `).join('');
        }
    }
}

// Utility functions
function formatDomainName(domain) {
    if (!domain) return 'Unknown';
    return domain.split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
}

function getMatchLevel(score) {
    if (score >= 80) return 'high';
    if (score >= 60) return 'medium';
    return 'low';
}

function showNotification(message, type = 'info') {
    // Simple notification implementation
    alert(`${type.toUpperCase()}: ${message}`);
}

function showLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }
}

function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

// Manual testing function
window.testConnection = async function() {
    console.log('Testing backend connection...');
    await checkSystemStatus();
};