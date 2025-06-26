"""
Pagination utilities
"""

from flask import request, url_for, current_app

def get_pagination_params():
    """
    Get pagination parameters from request
    
    Returns:
        Tuple of (page, per_page)
    """
    # Get page and per_page from request args
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', current_app.config['DEFAULT_PAGE_SIZE'], type=int)
    
    # Ensure per_page doesn't exceed maximum
    max_per_page = current_app.config['MAX_PAGE_SIZE']
    per_page = min(per_page, max_per_page)
    
    return page, per_page

def get_paginated_response(schema, query, page, per_page):
    """
    Create a paginated response
    
    Args:
        schema: Marshmallow schema for serialization
        query: SQLAlchemy query object
        page: Page number
        per_page: Items per page
        
    Returns:
        Dictionary with pagination metadata and results
    """
    # Paginate query
    paginated_query = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get pagination metadata
    pagination = {
        'total': paginated_query.total,
        'pages': paginated_query.pages,
        'page': page,
        'per_page': per_page,
        'has_next': paginated_query.has_next,
        'has_prev': paginated_query.has_prev
    }
    
    # Add next and prev page URLs if available
    if paginated_query.has_next:
        pagination['next'] = url_for(
            request.endpoint,
            page=page + 1,
            per_page=per_page,
            **{key: value for key, value in request.args.items() if key != 'page'}
        )
    
    if paginated_query.has_prev:
        pagination['prev'] = url_for(
            request.endpoint,
            page=page - 1,
            per_page=per_page,
            **{key: value for key, value in request.args.items() if key != 'page'}
        )
    
    # Serialize items
    items = schema.dump(paginated_query.items, many=True)
    
    # Return response
    return {
        'pagination': pagination,
        'items': items
    } 