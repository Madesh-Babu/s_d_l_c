from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    role: str = Field(..., pattern=r'^(staff|manager|admin)$')

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=80)
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[str] = Field(None, pattern=r'^(staff|manager|admin)$')

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
    access_token: str

# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

# Product Schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: Optional[str]

class ProductDelete(BaseModel):
    id: int

class DiscountRequest(BaseModel):
    id: int
    discount: float = Field(..., gt=0, le=100)
    tax: float = Field(0, ge=0, le=50)

class DiscountResponse(BaseModel):
    message: str
    new_price: float

# Response Wrappers
class SuccessResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str

class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    per_page: int
    pages: int