import os
import json
import openai
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from src.routes.shopify import make_shopify_request

load_dotenv()

ai_agent_bp = Blueprint('ai_agent', __name__)

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = os.getenv('OPENAI_API_BASE')

def get_shopify_tools():
    """Define available Shopify tools for the AI agent"""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_products",
                "description": "Get products from the Shopify store",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of products to retrieve (default: 10)",
                            "default": 10
                        },
                        "searchTitle": {
                            "type": "string",
                            "description": "Search for products by title"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_product_by_id",
                "description": "Get a specific product by its ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "productId": {
                            "type": "string",
                            "description": "The Shopify product ID"
                        }
                    },
                    "required": ["productId"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_orders",
                "description": "Get orders from the Shopify store",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of orders to retrieve (default: 10)",
                            "default": 10
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter orders by status",
                            "enum": ["any", "open", "closed", "cancelled"],
                            "default": "any"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_customers",
                "description": "Get customers from the Shopify store",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of customers to retrieve (default: 10)",
                            "default": 10
                        },
                        "searchQuery": {
                            "type": "string",
                            "description": "Search query for customers"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_product",
                "description": "Create a new product in the Shopify store",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Product title"
                        },
                        "descriptionHtml": {
                            "type": "string",
                            "description": "Product description in HTML format"
                        },
                        "vendor": {
                            "type": "string",
                            "description": "Product vendor"
                        },
                        "productType": {
                            "type": "string",
                            "description": "Product type"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Product tags"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["ACTIVE", "DRAFT", "ARCHIVED"],
                            "description": "Product status",
                            "default": "DRAFT"
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_store_info",
                "description": "Get basic information about the Shopify store",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]

def execute_shopify_function(function_name, arguments):
    """Execute a Shopify function based on the function name and arguments"""
    try:
        if function_name == "get_products":
            query = """
            query getProducts($first: Int!, $query: String) {
                products(first: $first, query: $query) {
                    edges {
                        node {
                            id
                            title
                            handle
                            description
                            vendor
                            productType
                            tags
                            status
                            createdAt
                            updatedAt
                            images(first: 1) {
                                edges {
                                    node {
                                        url
                                        altText
                                    }
                                }
                            }
                            variants(first: 5) {
                                edges {
                                    node {
                                        id
                                        title
                                        price
                                        inventoryQuantity
                                        sku
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """
            variables = {
                'first': arguments.get('limit', 10),
                'query': f'title:*{arguments.get("searchTitle", "")}*' if arguments.get("searchTitle") else ''
            }
            return make_shopify_request(query, variables)
            
        elif function_name == "get_product_by_id":
            product_id = arguments.get('productId')
            if not product_id.startswith('gid://shopify/Product/'):
                product_id = f'gid://shopify/Product/{product_id}'
                
            query = """
            query getProduct($id: ID!) {
                product(id: $id) {
                    id
                    title
                    handle
                    description
                    vendor
                    productType
                    tags
                    status
                    createdAt
                    updatedAt
                    images(first: 10) {
                        edges {
                            node {
                                url
                                altText
                            }
                        }
                    }
                    variants(first: 10) {
                        edges {
                            node {
                                id
                                title
                                price
                                inventoryQuantity
                                sku
                                weight
                                weightUnit
                            }
                        }
                    }
                }
            }
            """
            variables = {'id': product_id}
            return make_shopify_request(query, variables)
            
        elif function_name == "get_orders":
            query = """
            query getOrders($first: Int!) {
                orders(first: $first) {
                    edges {
                        node {
                            id
                            name
                            email
                            phone
                            createdAt
                            updatedAt
                            totalPrice
                            subtotalPrice
                            totalTax
                            currencyCode
                            financialStatus
                            fulfillmentStatus
                            tags
                            note
                            customer {
                                id
                                firstName
                                lastName
                                email
                            }
                            shippingAddress {
                                firstName
                                lastName
                                address1
                                address2
                                city
                                province
                                country
                                zip
                                phone
                            }
                            lineItems(first: 10) {
                                edges {
                                    node {
                                        id
                                        title
                                        quantity
                                        variant {
                                            id
                                            title
                                            price
                                            sku
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """
            variables = {'first': arguments.get('limit', 10)}
            return make_shopify_request(query, variables)
            
        elif function_name == "get_customers":
            query = """
            query getCustomers($first: Int!, $query: String) {
                customers(first: $first, query: $query) {
                    edges {
                        node {
                            id
                            firstName
                            lastName
                            email
                            phone
                            createdAt
                            updatedAt
                            tags
                            note
                            ordersCount
                            totalSpent
                            addresses(first: 5) {
                                id
                                firstName
                                lastName
                                address1
                                address2
                                city
                                province
                                country
                                zip
                                phone
                            }
                        }
                    }
                }
            }
            """
            variables = {
                'first': arguments.get('limit', 10),
                'query': arguments.get('searchQuery', '')
            }
            return make_shopify_request(query, variables)
            
        elif function_name == "create_product":
            query = """
            mutation productCreate($input: ProductInput!) {
                productCreate(input: $input) {
                    product {
                        id
                        title
                        handle
                        status
                        vendor
                        productType
                        tags
                        createdAt
                    }
                    userErrors {
                        field
                        message
                    }
                }
            }
            """
            product_input = {
                'title': arguments['title'],
                'descriptionHtml': arguments.get('descriptionHtml', ''),
                'vendor': arguments.get('vendor', ''),
                'productType': arguments.get('productType', ''),
                'tags': arguments.get('tags', []),
                'status': arguments.get('status', 'DRAFT')
            }
            variables = {'input': product_input}
            return make_shopify_request(query, variables)
            
        elif function_name == "get_store_info":
            query = """
            query {
                shop {
                    id
                    name
                    email
                    domain
                    myshopifyDomain
                    currencyCode
                    timezone
                    plan {
                        displayName
                    }
                }
            }
            """
            return make_shopify_request(query)
            
        else:
            return {"error": f"Unknown function: {function_name}"}
            
    except Exception as e:
        return {"error": str(e)}

@ai_agent_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages and execute Shopify operations via AI agent"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        conversation_history = data.get('history', [])
        
        # Build the conversation messages
        messages = [
            {
                "role": "system",
                "content": """You are a helpful AI assistant for a Shopify store. You can help users manage their store by:
                - Getting product information
                - Retrieving order details
                - Managing customer data
                - Creating new products
                - Getting store information
                
                When users ask about their store, use the available functions to get real-time data from their Shopify store.
                Always provide helpful, accurate responses based on the actual store data.
                
                If you need to perform any Shopify operations, use the appropriate function calls.
                Be conversational and helpful in your responses."""
            }
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add the current user message
        messages.append({"role": "user", "content": user_message})
        
        # Make the OpenAI API call with function calling
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=get_shopify_tools(),
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        
        # Check if the assistant wants to call a function
        if assistant_message.tool_calls:
            # Execute the function calls
            messages.append(assistant_message)
            
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Execute the Shopify function
                function_result = execute_shopify_function(function_name, function_args)
                
                # Add the function result to the conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(function_result)
                })
            
            # Get the final response from the assistant
            final_response = openai.chat.completions.create(
                model="gpt-4",
                messages=messages
            )
            
            final_message = final_response.choices[0].message.content
        else:
            final_message = assistant_message.content
        
        return jsonify({
            'response': final_message,
            'conversation_history': messages[1:]  # Exclude system message
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_agent_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'AI Agent'})

