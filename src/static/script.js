// Global variables
let conversationHistory = [];
let isLoading = false;

// DOM elements
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const storeInfoBtn = document.getElementById('storeInfoBtn');
const storeInfoModal = document.getElementById('storeInfoModal');
const closeStoreModal = document.getElementById('closeStoreModal');
const storeInfoContent = document.getElementById('storeInfoContent');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadStoreStats();
    checkConnection();
});

// Event listeners
function initializeEventListeners() {
    // Chat input and send button
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Suggested prompts
    document.querySelectorAll('.prompt-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const prompt = this.getAttribute('data-prompt');
            chatInput.value = prompt;
            sendMessage();
        });
    });

    // Quick action buttons
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            handleQuickAction(action);
        });
    });

    // Store info modal
    storeInfoBtn.addEventListener('click', showStoreInfo);
    closeStoreModal.addEventListener('click', hideStoreInfo);
    storeInfoModal.addEventListener('click', function(e) {
        if (e.target === storeInfoModal) {
            hideStoreInfo();
        }
    });
}

// Send message function
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || isLoading) return;

    // Add user message to chat
    addMessageToChat(message, 'user');
    chatInput.value = '';
    
    // Show loading
    setLoading(true);

    try {
        const response = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                history: conversationHistory
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Add assistant response to chat
        addMessageToChat(data.response, 'assistant');
        
        // Update conversation history
        conversationHistory = data.conversation_history || [];

    } catch (error) {
        console.error('Error sending message:', error);
        addMessageToChat('Sorry, I encountered an error while processing your request. Please try again.', 'assistant', true);
    } finally {
        setLoading(false);
    }
}

// Add message to chat
function addMessageToChat(message, sender, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (isError) {
        contentDiv.style.borderColor = 'rgba(239, 68, 68, 0.3)';
        contentDiv.style.background = 'rgba(239, 68, 68, 0.05)';
    }
    
    // Format message content (handle JSON responses)
    let formattedMessage = message;
    try {
        const parsed = JSON.parse(message);
        if (typeof parsed === 'object') {
            formattedMessage = formatObjectResponse(parsed);
        }
    } catch (e) {
        // Not JSON, use as is
        formattedMessage = message;
    }
    
    contentDiv.innerHTML = `<p>${formattedMessage}</p>`;
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format object responses for better display
function formatObjectResponse(obj) {
    if (obj.data && obj.data.products) {
        return formatProductsResponse(obj.data.products);
    } else if (obj.data && obj.data.orders) {
        return formatOrdersResponse(obj.data.orders);
    } else if (obj.data && obj.data.customers) {
        return formatCustomersResponse(obj.data.customers);
    } else if (obj.data && obj.data.shop) {
        return formatStoreInfoResponse(obj.data.shop);
    }
    
    return `<pre>${JSON.stringify(obj, null, 2)}</pre>`;
}

// Format products response
function formatProductsResponse(products) {
    if (!products.edges || products.edges.length === 0) {
        return 'No products found.';
    }
    
    let html = '<div class="response-list">';
    products.edges.forEach(edge => {
        const product = edge.node;
        html += `
            <div class="response-item">
                <h4>${product.title}</h4>
                <p><strong>Status:</strong> ${product.status}</p>
                <p><strong>Vendor:</strong> ${product.vendor || 'N/A'}</p>
                <p><strong>Type:</strong> ${product.productType || 'N/A'}</p>
                ${product.variants.edges.length > 0 ? `<p><strong>Price:</strong> $${product.variants.edges[0].node.price}</p>` : ''}
            </div>
        `;
    });
    html += '</div>';
    return html;
}

// Format orders response
function formatOrdersResponse(orders) {
    if (!orders.edges || orders.edges.length === 0) {
        return 'No orders found.';
    }
    
    let html = '<div class="response-list">';
    orders.edges.forEach(edge => {
        const order = edge.node;
        html += `
            <div class="response-item">
                <h4>Order ${order.name}</h4>
                <p><strong>Total:</strong> $${order.totalPrice} ${order.currencyCode}</p>
                <p><strong>Status:</strong> ${order.financialStatus}</p>
                <p><strong>Customer:</strong> ${order.customer ? `${order.customer.firstName} ${order.customer.lastName}` : 'N/A'}</p>
                <p><strong>Date:</strong> ${new Date(order.createdAt).toLocaleDateString()}</p>
            </div>
        `;
    });
    html += '</div>';
    return html;
}

// Format customers response
function formatCustomersResponse(customers) {
    if (!customers.edges || customers.edges.length === 0) {
        return 'No customers found.';
    }
    
    let html = '<div class="response-list">';
    customers.edges.forEach(edge => {
        const customer = edge.node;
        html += `
            <div class="response-item">
                <h4>${customer.firstName} ${customer.lastName}</h4>
                <p><strong>Email:</strong> ${customer.email}</p>
                <p><strong>Orders:</strong> ${customer.ordersCount}</p>
                <p><strong>Total Spent:</strong> $${customer.totalSpent}</p>
                <p><strong>Joined:</strong> ${new Date(customer.createdAt).toLocaleDateString()}</p>
            </div>
        `;
    });
    html += '</div>';
    return html;
}

// Format store info response
function formatStoreInfoResponse(shop) {
    return `
        <div class="store-info">
            <h4>${shop.name}</h4>
            <p><strong>Domain:</strong> ${shop.domain}</p>
            <p><strong>Email:</strong> ${shop.email}</p>
            <p><strong>Currency:</strong> ${shop.currencyCode}</p>
            <p><strong>Timezone:</strong> ${shop.timezone}</p>
            <p><strong>Plan:</strong> ${shop.plan ? shop.plan.displayName : 'N/A'}</p>
        </div>
    `;
}

// Handle quick actions
function handleQuickAction(action) {
    const actionMessages = {
        'products': 'Show me my products',
        'orders': 'Show me my recent orders',
        'customers': 'Show me my customers',
        'create-product': 'How can I create a new product?'
    };
    
    const message = actionMessages[action];
    if (message) {
        chatInput.value = message;
        sendMessage();
    }
}

// Show/hide loading state
function setLoading(loading) {
    isLoading = loading;
    sendBtn.disabled = loading;
    
    if (loading) {
        loadingOverlay.classList.add('active');
        sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    } else {
        loadingOverlay.classList.remove('active');
        sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
    }
}

// Load store statistics
async function loadStoreStats() {
    try {
        // Load products count
        const productsResponse = await fetch('/api/shopify/products?limit=1');
        if (productsResponse.ok) {
            const productsData = await productsResponse.json();
            if (productsData.data && productsData.data.products) {
                document.getElementById('productCount').textContent = productsData.data.products.edges.length > 0 ? '1+' : '0';
            }
        }

        // Load orders count
        const ordersResponse = await fetch('/api/shopify/orders?limit=1');
        if (ordersResponse.ok) {
            const ordersData = await ordersResponse.json();
            if (ordersData.data && ordersData.data.orders) {
                document.getElementById('orderCount').textContent = ordersData.data.orders.edges.length > 0 ? '1+' : '0';
            }
        }

        // Load customers count
        const customersResponse = await fetch('/api/shopify/customers?limit=1');
        if (customersResponse.ok) {
            const customersData = await customersResponse.json();
            if (customersData.data && customersData.data.customers) {
                document.getElementById('customerCount').textContent = customersData.data.customers.edges.length > 0 ? '1+' : '0';
            }
        }
    } catch (error) {
        console.error('Error loading store stats:', error);
    }
}

// Check connection status
async function checkConnection() {
    try {
        const response = await fetch('/api/ai/health');
        const connectionStatus = document.getElementById('connectionStatus');
        
        if (response.ok) {
            connectionStatus.innerHTML = '<div class="status-indicator"></div><span>Connected</span>';
            connectionStatus.style.background = 'rgba(34, 197, 94, 0.1)';
            connectionStatus.style.borderColor = 'rgba(34, 197, 94, 0.3)';
        } else {
            throw new Error('Connection failed');
        }
    } catch (error) {
        const connectionStatus = document.getElementById('connectionStatus');
        connectionStatus.innerHTML = '<div class="status-indicator" style="background: #ef4444;"></div><span>Disconnected</span>';
        connectionStatus.style.background = 'rgba(239, 68, 68, 0.1)';
        connectionStatus.style.borderColor = 'rgba(239, 68, 68, 0.3)';
    }
}

// Show store info modal
async function showStoreInfo() {
    storeInfoModal.classList.add('active');
    storeInfoContent.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>Loading store information...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/api/shopify/store-info');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.data && data.data.shop) {
            storeInfoContent.innerHTML = formatStoreInfoResponse(data.data.shop);
        } else {
            throw new Error('Invalid response format');
        }
    } catch (error) {
        console.error('Error loading store info:', error);
        storeInfoContent.innerHTML = `
            <div class="error-message">
                <p>Failed to load store information. Please try again.</p>
                <p class="error-details">${error.message}</p>
            </div>
        `;
    }
}

// Hide store info modal
function hideStoreInfo() {
    storeInfoModal.classList.remove('active');
}

// Add CSS for response formatting
const style = document.createElement('style');
style.textContent = `
    .response-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-top: 0.5rem;
    }
    
    .response-item {
        background: rgba(59, 130, 246, 0.05);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 0.5rem;
        padding: 1rem;
    }
    
    .response-item h4 {
        color: #3b82f6;
        margin-bottom: 0.5rem;
        font-size: 1rem;
        font-weight: 600;
    }
    
    .response-item p {
        margin-bottom: 0.25rem;
        font-size: 0.875rem;
        line-height: 1.4;
    }
    
    .response-item p:last-child {
        margin-bottom: 0;
    }
    
    .store-info {
        background: rgba(59, 130, 246, 0.05);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 0.5rem;
        padding: 1.5rem;
    }
    
    .store-info h4 {
        color: #3b82f6;
        margin-bottom: 1rem;
        font-size: 1.25rem;
        font-weight: 700;
    }
    
    .store-info p {
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
        line-height: 1.4;
    }
    
    .error-message {
        text-align: center;
        color: #ef4444;
    }
    
    .error-details {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.5rem;
    }
    
    pre {
        background: rgba(15, 15, 35, 0.8);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 0.5rem;
        padding: 1rem;
        overflow-x: auto;
        font-size: 0.875rem;
        line-height: 1.4;
    }
`;
document.head.appendChild(style);

