"""
Simple Email and Password Validation using Pydantic with Regex
"""

import re
from pydantic import BaseModel, Field, field_validator, EmailStr


class EmailValidator(BaseModel):
    """Simple email validator."""
    email: EmailStr = Field(..., description="Email address")
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """Basic email validation with regex."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()


class PasswordValidator(BaseModel):
    """Simple password validator with regex."""
    password: str = Field(..., min_length=8, description="Password")
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Password validation with regex patterns."""
        errors = []
        
        # Regex patterns
        if not re.search(r'[A-Z]', v):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', v):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', v):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]', v):
            errors.append("Password must contain at least one special symbol")
        
        if re.search(r'\s', v):
            errors.append("Password cannot contain whitespace")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return v
    
    @classmethod
    def get_password_strength(cls, password: str) -> dict:
        """Simple password strength analysis."""
        score = 0
        
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]', password):
            score += 1
        
        if score <= 2:
            strength = "Weak"
        elif score <= 4:
            strength = "Fair"
        else:
            strength = "Strong"
        
        return {
            "strength": strength,
            "score": score,
            "max_score": 6
        }


class UserValidator(BaseModel):
    """Simple user validator for email and password."""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    username: str = Field(..., description="Username")
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """Validate email."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password."""
        errors = []
        
        if not re.search(r'[A-Z]', v):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', v):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', v):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]', v):
            errors.append("Password must contain at least one special symbol")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return v
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Validate username."""
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        
        return v
