const API_BASE_URL = window.location.origin;

const chatContainer = document.getElementById('chatContainer');
const queryForm = document.getElementById('queryForm');
const queryInput = document.getElementById('queryInput');
const sendBtn = document.getElementById('sendBtn');

let isProcessing = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    queryForm.addEventListener('submit', handleSubmit);
    queryInput.focus();
});

// Handle form submission
async function handleSubmit(e) {
    e.preventDefault();
    
    if (isProcessing) return;
    
    const query = queryInput.value.trim();
    if (!query) return;
    
    // Clear input
    queryInput.value = '';
    
    // Remove welcome message if present
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    // Add user message
    addUserMessage(query);
    
    // Show loading
    const loadingId = showLoading();
    
    // Disable input
    isProcessing = true;
    sendBtn.disabled = true;
    
    try {
        // Call API
        const response = await fetch(`${API_BASE_URL}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query, top_k: 3 })
        });
        
        if (!response.ok) {
            throw new Error('Failed to get response from server');
        }
        
        const data = await response.json();
        
        // Remove loading
        removeLoading(loadingId);
        
        // Add assistant response
        addAssistantMessage(data);
        
    } catch (error) {
        console.error('Error:', error);
        removeLoading(loadingId);
        addErrorMessage('Sorry, something went wrong. Please try again.');
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
        queryInput.focus();
    }
}

// Add user message to chat
function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-user';
    messageDiv.innerHTML = `
        <div class="message-content">${escapeHtml(text)}</div>
    `;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add assistant message with context
function addAssistantMessage(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-assistant';
    
    let contextHtml = '';
    if (data.context && data.context.length > 0) {
        const chunksHtml = data.context.map(chunk => `
            <div class="context-chunk">
                <div class="context-meta">
                    <span class="context-source">📄 ${escapeHtml(chunk.source)}</span>
                    <span class="context-score">Score: ${(chunk.score * 100).toFixed(1)}%</span>
                </div>
                <div class="context-text">${escapeHtml(chunk.text)}</div>
            </div>
        `).join('');
        
        contextHtml = `
            <div class="context-section">
                <div class="context-title">📚 Retrieved Context</div>
                ${chunksHtml}
            </div>
        `;
    }
    
    messageDiv.innerHTML = `
        <div class="message-content">${escapeHtml(data.answer)}</div>
        ${contextHtml}
    `;
    
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Show loading indicator
function showLoading() {
    const loadingId = `loading-${Date.now()}`;
    const loadingDiv = document.createElement('div');
    loadingDiv.id = loadingId;
    loadingDiv.className = 'loading';
    loadingDiv.innerHTML = `
        <div class="loading-spinner"></div>
        <span>Searching documents...</span>
    `;
    chatContainer.appendChild(loadingDiv);
    scrollToBottom();
    return loadingId;
}

// Remove loading indicator
function removeLoading(loadingId) {
    const loadingDiv = document.getElementById(loadingId);
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// Add error message
function addErrorMessage(text) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = text;
    chatContainer.appendChild(errorDiv);
    scrollToBottom();
}

// Scroll to bottom of chat
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Handle example button clicks
function askExample(query) {
    queryInput.value = query;
    queryForm.dispatchEvent(new Event('submit'));
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
