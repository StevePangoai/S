# Shopify AI Agent

An AI-powered agent application for Shopify that enables users to interact with their Shopify store through natural language commands. Built with Flask backend and modern web frontend, featuring seamless Shopify API integration and OpenAI-powered AI assistant.

## Features

- **AI-Powered Chat Interface**: Natural language interaction with your Shopify store
- **Shopify Integration**: Full integration with Shopify Admin API
- **Modern UI**: Futuristic, responsive design with dark theme
- **Real-time Store Management**: View products, orders, customers, and store information
- **Quick Actions**: One-click access to common store operations
- **Store Statistics**: Live dashboard with key metrics

## Prerequisites

- Python 3.11 or higher
- Node.js 18+ (for development)
- Shopify store with Admin API access
- OpenAI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd shopify-ai-agent
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```env
   SHOPIFY_ACCESS_TOKEN=your_shopify_admin_api_token
   SHOPIFY_STOREFRONT_TOKEN=your_shopify_storefront_token
   MYSHOPIFY_DOMAIN=your-store.myshopify.com
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_API_BASE=https://api.openai.com/v1
   ```

## Getting Shopify API Credentials

### Admin API Access Token

1. Go to your Shopify admin panel
2. Navigate to **Apps** → **App and sales channel settings**
3. Click **Develop apps**
4. Create a new app or select an existing one
5. Configure the following scopes:
   - `read_products`
   - `write_products`
   - `read_orders`
   - `write_orders`
   - `read_customers`
   - `write_customers`
   - `read_inventory`
   - `write_inventory`
6. Install the app and copy the Admin API access token

### Storefront API Access Token

1. In the same app configuration
2. Enable **Storefront API access**
3. Configure the required permissions
4. Copy the Storefront access token

## Usage

1. **Start the application**
   ```bash
   source venv/bin/activate
   python src/main.py
   ```

2. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

3. **Interact with your store**
   - Use the chat interface to ask questions about your store
   - Click quick action buttons for common operations
   - View store statistics in the sidebar
   - Access detailed store information via the Store Info button

## API Endpoints

### Shopify API Routes (`/api/shopify/`)

- `GET /products` - Get products from store
- `GET /product/<id>` - Get specific product by ID
- `GET /orders` - Get orders from store
- `GET /customers` - Get customers from store
- `POST /product` - Create new product
- `GET /store-info` - Get store information

### AI Agent Routes (`/api/ai/`)

- `POST /chat` - Send message to AI agent
- `GET /health` - Health check endpoint

## AI Agent Capabilities

The AI agent can help you with:

- **Product Management**: View, search, and create products
- **Order Management**: Check order status, view order details
- **Customer Management**: View customer information and history
- **Store Analytics**: Get insights about your store performance
- **General Queries**: Answer questions about your store data

### Example Queries

- "Show me my recent orders"
- "What are my top-selling products?"
- "How many customers do I have?"
- "Create a new product called 'Premium T-Shirt'"
- "What's my store's total revenue this month?"

## Project Structure

```
shopify-ai-agent/
├── src/
│   ├── main.py                 # Flask application entry point
│   ├── routes/
│   │   ├── shopify.py         # Shopify API routes
│   │   ├── ai_agent.py        # AI agent routes
│   │   └── user.py            # User management routes
│   ├── models/
│   │   └── user.py            # Database models
│   ├── static/
│   │   ├── index.html         # Main HTML file
│   │   ├── styles.css         # CSS styles
│   │   └── script.js          # JavaScript functionality
│   └── database/
│       └── app.db             # SQLite database
├── venv/                      # Python virtual environment
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
└── README.md                  # This file
```

## Development

### Running in Development Mode

The Flask application runs in debug mode by default, which enables:
- Automatic reloading on code changes
- Detailed error messages
- Debug toolbar

### Adding New Features

1. **Backend**: Add new routes in the appropriate blueprint file
2. **Frontend**: Update the HTML, CSS, and JavaScript files
3. **AI Agent**: Extend the tool definitions in `ai_agent.py`

### Testing

Test the application by:
1. Starting the Flask server
2. Opening the web interface
3. Testing chat functionality
4. Verifying API endpoints with curl or Postman

## Deployment

### Local Deployment

The application is configured for local deployment by default. Simply run:

```bash
python src/main.py
```

### Production Deployment

For production deployment, consider:

1. **Use a production WSGI server** (e.g., Gunicorn)
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
   ```

2. **Set up environment variables** securely
3. **Configure HTTPS** with a reverse proxy (nginx, Apache)
4. **Set up monitoring** and logging
5. **Use a production database** (PostgreSQL, MySQL)

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure virtual environment is activated
   - Install dependencies: `pip install -r requirements.txt`

2. **Shopify API errors**
   - Verify API credentials in `.env` file
   - Check API scopes and permissions
   - Ensure store domain is correct

3. **OpenAI API errors**
   - Verify OpenAI API key
   - Check API quota and billing
   - Ensure correct API base URL

4. **Frontend not loading**
   - Check Flask server is running
   - Verify static files are in correct location
   - Check browser console for JavaScript errors

### Debug Mode

Enable debug logging by setting:
```env
FLASK_DEBUG=1
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For support and questions:
- Check the troubleshooting section
- Review Shopify API documentation
- Check OpenAI API documentation
- Create an issue in the repository

## Acknowledgments

- Built on the [shopify-mcp](https://github.com/GeLi2001/shopify-mcp) framework
- Uses OpenAI GPT models for AI functionality
- Shopify Admin API for store integration
- Flask web framework for backend
- Modern CSS and JavaScript for frontend

