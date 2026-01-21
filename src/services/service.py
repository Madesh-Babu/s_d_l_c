from src.models.models import db, Category,Product
from src.core.interfaces import (IProductCreator, IProductReader, IProductUpdater, IProductDeleter, ICategoryDeleter, ICategoryCreator,ICategoryReader,ICategoryUpdater)
from src.services.price_decorator import Price, DiscountDecorator, TaxDecorator
from src.models.schemas import (
    CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate,
    DiscountRequest, UserCreate, UserUpdate
)
from pydantic import ValidationError

def validate_category_data(data):
    """Validate the category JSON payload using Pydantic."""
    try:
        category_data = CategoryCreate(**data)
        # Check for duplicate category name
        existing_category = Category.query.filter_by(name=category_data.name).first()
        if existing_category:
            return False, f"Category with name '{category_data.name}' already exists."
        return True, None
    except ValidationError as e:
        return False, str(e)


class CategoryService(ICategoryUpdater,ICategoryReader,ICategoryCreator,ICategoryDeleter):
    """Handles all category-related operations."""

    def create_category(self,name):
        if Category.query.filter_by(name=name).first():
            return None, {"error": "Category already exists"}

        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        return category, None

    def get_all_categories(self):
        return Category.query.all()

    def get_category(self,category_id):
        return Category.query.get_or_404(category_id)

    def update_category(self, category_id, data):
        category = Category.query.get(category_id)
        if not category:
            return None  # Category not found

        for key, value in data.items():
            setattr(category, key, value)

        db.session.commit()
        return category

    def delete_category(self,category_id):
        category = Category.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        return True


def validate_product_data(data):
    """Validate the product JSON payload using Pydantic."""
    try:
        product_data = ProductCreate(**data)
        return True, None
    except ValidationError as e:
        return False, str(e)


class ProductService(IProductCreator,IProductReader,IProductUpdater,IProductDeleter):
    """Handles all product-related database operations."""
    def create_product(self, data):
        new_product = Product(**data)
        db.session.add(new_product)
        db.session.commit()
        return new_product

    def get_all_products(self):
        return Product.query.all()

    def get_products(self, product_id):
        return Product.query.get(product_id)

    def update_product(self, product_id, data):
        product = Product.query.get(product_id)
        if not product:
            return None
        for key, value in data.items():
            setattr(product, key, value)
        db.session.commit()
        return product

    def delete_product(self, product_id):
        product = Product.query.get(product_id)
        if not product:
            return False
        db.session.delete(product)
        db.session.commit()
        return True


class DiscountedProductService(ProductService):
    """Extends base product logic with discount support."""
    
    @staticmethod
    def apply_discount(product, discount_percentage, tax_percentage=0):
        """Apply discount using Pydantic validation."""
        try:
            discount_request = DiscountRequest(
                id=product.id,
                discount=discount_percentage,
                tax=tax_percentage
            )
            
            base_price = Price(product.price)

            # Apply discount first
            discounted = DiscountDecorator(base_price, discount_percentage)

            # Then apply tax if any
            final_price = TaxDecorator(discounted, tax_percentage).get_price() if tax_percentage > 0 else discounted.get_price()

            product.price = round(final_price, 2)
            db.session.commit()
            return product
        except ValidationError as e:
            raise ValueError(str(e))