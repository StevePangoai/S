import os
import requests
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

load_dotenv()

shopify_bp = Blueprint('shopify', __name__)

SHOPIFY_ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
MYSHOPIFY_DOMAIN = os.getenv('MYSHOPIFY_DOMAIN')
SHOPIFY_API_VERSION = '2023-07'

def make_shopify_request(query, variables=None):
    """Make a GraphQL request to Shopify Admin API"""
    url = f"https://{MYSHOPIFY_DOMAIN}/admin/api/{SHOPIFY_API_VERSION}/graphql.json"
    headers = {
        'X-Shopify-Access-Token': SHOPIFY_ACCESS_TOKEN,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'query': query
    }
    
    if variables:
        payload['variables'] = variables
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

@shopify_bp.route('/products', methods=['GET'])
def get_products():
    """Get products from Shopify store"""
    limit = request.args.get('limit', 10, type=int)
    search_title = request.args.get('searchTitle', '')
    
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
        'first': limit,
        'query': f'title:*{search_title}*' if search_title else ''
    }
    
    result = make_shopify_request(query, variables)
    return jsonify(result)

@shopify_bp.route('/product/<product_id>', methods=['GET'])
def get_product_by_id(product_id):
    """Get a specific product by ID"""
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
    
    # Ensure the product ID has the proper GraphQL format
    if not product_id.startswith('gid://shopify/Product/'):
        product_id = f'gid://shopify/Product/{product_id}'
    
    variables = {'id': product_id}
    result = make_shopify_request(query, variables)
    return jsonify(result)

@shopify_bp.route('/orders', methods=['GET'])
def get_orders():
    """Get orders from Shopify store"""
    limit = request.args.get('limit', 10, type=int)
    status = request.args.get('status', 'any')
    
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
    
    variables = {'first': limit}
    result = make_shopify_request(query, variables)
    return jsonify(result)

@shopify_bp.route('/customers', methods=['GET'])
def get_customers():
    """Get customers from Shopify store"""
    limit = request.args.get('limit', 10, type=int)
    search_query = request.args.get('searchQuery', '')
    
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
        'first': limit,
        'query': search_query if search_query else ''
    }
    
    result = make_shopify_request(query, variables)
    return jsonify(result)

@shopify_bp.route('/product', methods=['POST'])
def create_product():
    """Create a new product"""
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Product title is required'}), 400
    
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
        'title': data['title'],
        'descriptionHtml': data.get('descriptionHtml', ''),
        'vendor': data.get('vendor', ''),
        'productType': data.get('productType', ''),
        'tags': data.get('tags', []),
        'status': data.get('status', 'DRAFT')
    }
    
    variables = {'input': product_input}
    result = make_shopify_request(query, variables)
    return jsonify(result)

@shopify_bp.route('/store-info', methods=['GET'])
def get_store_info():
    """Get basic store information"""
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
    
    result = make_shopify_request(query)
    return jsonify(result)

