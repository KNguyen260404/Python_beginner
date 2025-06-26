"""
Product schema for serialization and validation
"""

from marshmallow import fields, validate, validates_schema, ValidationError
from app.schemas import ma
from app.models.product import Product

class ProductSchema(ma.SQLAlchemySchema):
    """Schema for Product model"""
    
    class Meta:
        model = Product
        load_instance = True
    
    id = ma.auto_field(dump_only=True)
    name = ma.auto_field(
        required=True,
        validate=validate.Length(min=3, max=100)
    )
    description = ma.auto_field()
    price = ma.auto_field(
        required=True,
        validate=validate.Range(min=0.01)
    )
    stock = ma.auto_field(validate=validate.Range(min=0))
    category = ma.auto_field(validate=validate.Length(max=50))
    image_url = ma.auto_field(validate=validate.URL(require_tld=False, error="Invalid URL"))
    is_active = ma.auto_field()
    user_id = ma.auto_field(dump_only=True)
    created_at = ma.auto_field(dump_only=True)
    updated_at = ma.auto_field(dump_only=True)
    
    # Include user information
    user = fields.Nested(
        'UserSchema',
        only=('id', 'username'),
        dump_only=True
    )
    
    @validates_schema
    def validate_price_stock(self, data, **kwargs):
        """Validate price and stock are valid"""
        if 'price' in data and data['price'] <= 0:
            raise ValidationError('Price must be greater than zero', 'price')

class ProductQuerySchema(ma.Schema):
    """Schema for product query parameters"""
    
    page = fields.Integer(missing=1, validate=validate.Range(min=1))
    per_page = fields.Integer(missing=10, validate=validate.Range(min=1, max=100))
    sort = fields.String(missing='created_at')
    order = fields.String(missing='desc', validate=validate.OneOf(['asc', 'desc']))
    category = fields.String()
    min_price = fields.Float(validate=validate.Range(min=0))
    max_price = fields.Float(validate=validate.Range(min=0))
    search = fields.String()
    
    @validates_schema
    def validate_price_range(self, data, **kwargs):
        """Validate min_price is less than max_price"""
        if 'min_price' in data and 'max_price' in data:
            if data['min_price'] > data['max_price']:
                raise ValidationError('min_price must be less than max_price') 