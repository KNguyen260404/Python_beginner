"""
Product routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import or_
from flasgger import swag_from

from app.models import db
from app.models.product import Product
from app.schemas.product import ProductSchema, ProductQuerySchema
from app.utils.pagination import get_pagination_params, get_paginated_response

products_bp = Blueprint('products', __name__)
product_schema = ProductSchema()
product_query_schema = ProductQuerySchema()

@products_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Products'],
    'summary': 'Get all products',
    'description': 'Returns a list of all products with pagination, filtering, and sorting',
    'parameters': [
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'default': 1,
            'description': 'Page number'
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'default': 10,
            'description': 'Items per page'
        },
        {
            'name': 'sort',
            'in': 'query',
            'type': 'string',
            'default': 'created_at',
            'description': 'Sort field (name, price, created_at)'
        },
        {
            'name': 'order',
            'in': 'query',
            'type': 'string',
            'default': 'desc',
            'enum': ['asc', 'desc'],
            'description': 'Sort order'
        },
        {
            'name': 'category',
            'in': 'query',
            'type': 'string',
            'description': 'Filter by category'
        },
        {
            'name': 'min_price',
            'in': 'query',
            'type': 'number',
            'description': 'Minimum price filter'
        },
        {
            'name': 'max_price',
            'in': 'query',
            'type': 'number',
            'description': 'Maximum price filter'
        },
        {
            'name': 'search',
            'in': 'query',
            'type': 'string',
            'description': 'Search term for product name or description'
        }
    ],
    'responses': {
        '200': {
            'description': 'List of products',
            'schema': {
                'type': 'object',
                'properties': {
                    'pagination': {'type': 'object'},
                    'items': {
                        'type': 'array',
                        'items': {'type': 'object'}
                    }
                }
            }
        }
    }
})
def get_products():
    """Get all products with filtering and pagination"""
    try:
        # Parse query parameters
        query_params = product_query_schema.load(request.args)
        
        # Get pagination parameters
        page = query_params.get('page', 1)
        per_page = query_params.get('per_page', 10)
        
        # Build query
        query = Product.query
        
        # Apply filters
        if 'category' in query_params:
            query = query.filter(Product.category == query_params['category'])
        
        if 'min_price' in query_params:
            query = query.filter(Product.price >= query_params['min_price'])
        
        if 'max_price' in query_params:
            query = query.filter(Product.price <= query_params['max_price'])
        
        if 'search' in query_params:
            search_term = f"%{query_params['search']}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
        
        # Apply sorting
        sort_field = query_params.get('sort', 'created_at')
        sort_order = query_params.get('order', 'desc')
        
        if hasattr(Product, sort_field):
            sort_attr = getattr(Product, sort_field)
            if sort_order == 'desc':
                query = query.order_by(sort_attr.desc())
            else:
                query = query.order_by(sort_attr.asc())
        
        # Return paginated response
        return jsonify(get_paginated_response(product_schema, query, page, per_page)), 200
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Invalid query parameters',
            'details': e.messages
        }), 400

@products_bp.route('/', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Products'],
    'summary': 'Create a new product',
    'description': 'Creates a new product',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Access token with Bearer prefix'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Product Name'},
                    'description': {'type': 'string', 'example': 'Product description'},
                    'price': {'type': 'number', 'example': 19.99},
                    'stock': {'type': 'integer', 'example': 100},
                    'category': {'type': 'string', 'example': 'Electronics'},
                    'image_url': {'type': 'string', 'example': 'https://example.com/image.jpg'}
                },
                'required': ['name', 'price']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Product created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'product': {'type': 'object'}
                }
            }
        },
        '400': {
            'description': 'Validation error'
        }
    }
})
def create_product():
    """Create a new product"""
    try:
        # Get current user ID
        current_user_id = get_jwt_identity()
        
        # Parse and validate request data
        product_data = request.get_json()
        
        # Create product
        product = product_schema.load(product_data)
        product.user_id = current_user_id
        
        # Save to database
        db.session.add(product)
        db.session.commit()
        
        # Return response
        return jsonify({
            'message': 'Product created successfully',
            'product': product_schema.dump(product)
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Invalid input data',
            'details': e.messages
        }), 400

@products_bp.route('/<int:product_id>', methods=['GET'])
@swag_from({
    'tags': ['Products'],
    'summary': 'Get product by ID',
    'description': 'Returns a specific product by ID',
    'parameters': [
        {
            'name': 'product_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Product ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'Product details',
            'schema': {
                'type': 'object'
            }
        },
        '404': {
            'description': 'Product not found'
        }
    }
})
def get_product(product_id):
    """Get product by ID"""
    # Get product from database
    product = Product.query.get_or_404(product_id)
    
    # Return product
    return jsonify(product_schema.dump(product)), 200

@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Products'],
    'summary': 'Update product',
    'description': 'Updates a specific product by ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Access token with Bearer prefix'
        },
        {
            'name': 'product_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Product ID'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'price': {'type': 'number'},
                    'stock': {'type': 'integer'},
                    'category': {'type': 'string'},
                    'image_url': {'type': 'string'},
                    'is_active': {'type': 'boolean'}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Product updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'product': {'type': 'object'}
                }
            }
        },
        '400': {
            'description': 'Validation error'
        },
        '403': {
            'description': 'Access denied'
        },
        '404': {
            'description': 'Product not found'
        }
    }
})
def update_product(product_id):
    """Update product by ID"""
    try:
        # Get current user ID
        current_user_id = get_jwt_identity()
        
        # Get product from database
        product = Product.query.get_or_404(product_id)
        
        # Check if current user owns the product
        if product.user_id != current_user_id:
            return jsonify({
                'error': 'Forbidden',
                'message': 'You do not have permission to update this product'
            }), 403
        
        # Parse and validate request data
        product_data = request.get_json()
        
        # Update product
        updated_product = product_schema.load(product_data, instance=product, partial=True)
        
        # Save to database
        db.session.commit()
        
        # Return response
        return jsonify({
            'message': 'Product updated successfully',
            'product': product_schema.dump(updated_product)
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Invalid input data',
            'details': e.messages
        }), 400

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['Products'],
    'summary': 'Delete product',
    'description': 'Deletes a specific product by ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Access token with Bearer prefix'
        },
        {
            'name': 'product_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Product ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'Product deleted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        },
        '403': {
            'description': 'Access denied'
        },
        '404': {
            'description': 'Product not found'
        }
    }
})
def delete_product(product_id):
    """Delete product by ID"""
    # Get current user ID
    current_user_id = get_jwt_identity()
    
    # Get product from database
    product = Product.query.get_or_404(product_id)
    
    # Check if current user owns the product
    if product.user_id != current_user_id:
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to delete this product'
        }), 403
    
    # Delete product
    db.session.delete(product)
    db.session.commit()
    
    # Return response
    return jsonify({
        'message': 'Product deleted successfully'
    }), 200 