#https://news.ycombinator.com/item?id=32366759
#https://news.ycombinator.com/item?id=36382614

import typing as t
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, select, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
import strawberry
from pydantic import BaseModel

# ====== SQLAlchemy Models ======
Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    accounts = relationship("Account", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.name}, email={self.email})>"


class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True)
    account_number = Column(String(20), nullable=False, unique=True)
    balance = Column(Integer, default=0)  # stored in cents
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    account_type = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
    
    def __repr__(self):
        return f"<Account(id={self.id}, account_number={self.account_number}, balance={self.balance/100})>"


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # stored in cents
    description = Column(Text)
    transaction_type = Column(String(20), nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    account = relationship("Account", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount/100}, type={self.transaction_type})>"


# ====== Approach 1: Python Attribute-Based Updates ======

class DomainModelUpdater:
    """Generic class for updating SQLAlchemy domain models."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def update_model(self, model_class, model_id: int, attributes: dict) -> t.Optional[Base]:
        """
        Update specific attributes of a domain model.
        
        Args:
            model_class: SQLAlchemy model class
            model_id: ID of the model to update
            attributes: Dictionary of attributes to update
        
        Returns:
            Updated model instance or None if not found
        """
        instance = self.session.query(model_class).get(model_id)
        if not instance:
            return None
        
        # Update only the specified attributes
        for attr_name, attr_value in attributes.items():
            if hasattr(instance, attr_name):
                setattr(instance, attr_name, attr_value)
        
        self.session.commit()
        return instance
    
    def update_model_batch(self, model_class, filter_criteria: dict, attributes: dict) -> int:
        """
        Update specific attributes for all models matching filter criteria.
        
        Args:
            model_class: SQLAlchemy model class
            filter_criteria: Dictionary of filter criteria
            attributes: Dictionary of attributes to update
        
        Returns:
            Number of updated rows
        """
        query = self.session.query(model_class)
        
        # Apply filter criteria
        for attr_name, attr_value in filter_criteria.items():
            if hasattr(model_class, attr_name):
                query = query.filter(getattr(model_class, attr_name) == attr_value)
        
        # Execute update
        result = query.update(attributes, synchronize_session=False)
        self.session.commit()
        
        return result
    
    def update_with_validation(self, model_class, model_id: int, attributes: dict, 
                              validator_func: t.Callable[[dict], t.Tuple[bool, str]]) -> t.Tuple[t.Optional[Base], str]:
        """
        Update specific attributes of a domain model with validation.
        
        Args:
            model_class: SQLAlchemy model class
            model_id: ID of the model to update
            attributes: Dictionary of attributes to update
            validator_func: Function that validates the attributes
            
        Returns:
            Tuple of (updated model instance or None if not found, error message if any)
        """
        # Validate attributes first
        is_valid, error_msg = validator_func(attributes)
        if not is_valid:
            return None, error_msg
        
        instance = self.update_model(model_class, model_id, attributes)
        return instance, "" if instance else "Model not found"


# Example usage with predictor for Account balance update
class BalanceUpdatePredictor:
    """Predicts the effect of balance updates on accounts."""
    
    def predict_balance_impact(self, account: Account, new_balance: int) -> dict:
        """
        Predict the impact of updating an account balance.
        
        Args:
            account: Account model instance
            new_balance: New balance amount in cents
            
        Returns:
            Dictionary with prediction results
        """
        balance_diff = new_balance - account.balance
        percentage_change = (balance_diff / account.balance * 100) if account.balance != 0 else float('inf')
        
        prediction = {
            "original_balance": account.balance / 100,  # Convert to dollars
            "new_balance": new_balance / 100,  # Convert to dollars
            "change_amount": balance_diff / 100,  # Convert to dollars
            "percentage_change": round(percentage_change, 2),
            "requires_approval": abs(percentage_change) > 50,  # Example business rule
            "risk_level": self._calculate_risk_level(account, new_balance)
        }
        
        return prediction
    
    def _calculate_risk_level(self, account: Account, new_balance: int) -> str:
        """Calculate risk level based on account history and new balance."""
        if new_balance < 0:
            return "High"
        
        # Example logic - could be replaced with a more sophisticated model
        total_transactions = len(account.transactions)
        avg_transaction = sum(t.amount for t in account.transactions) / total_transactions if total_transactions > 0 else 0
        
        if new_balance < avg_transaction and avg_transaction > 0:
            return "Medium"
        elif new_balance < 10000:  # Less than $100
            return "Low-Medium"
        else:
            return "Low"


# ====== Approach 2: GraphQL-Based Updates ======

# Strawberry GraphQL types
@strawberry.type
class AccountType:
    id: int
    account_number: str
    balance: float  # Use float for dollars
    account_type: str
    is_active: bool
    
    @classmethod
    def from_model(cls, model: Account) -> "AccountType":
        return cls(
            id=model.id,
            account_number=model.account_number,
            balance=model.balance / 100,  # Convert to dollars
            account_type=model.account_type,
            is_active=model.is_active
        )


@strawberry.type
class CustomerType:
    id: int
    name: str
    email: str
    phone: str
    is_active: bool
    
    @classmethod
    def from_model(cls, model: Customer) -> "CustomerType":
        return cls(
            id=model.id,
            name=model.name,
            email=model.email,
            phone=model.phone or "",
            is_active=model.is_active
        )


@strawberry.input
class AccountUpdateInput:
    balance: t.Optional[float] = None
    account_type: t.Optional[str] = None
    is_active: t.Optional[bool] = None


@strawberry.input
class CustomerUpdateInput:
    name: t.Optional[str] = None
    email: t.Optional[str] = None
    phone: t.Optional[str] = None
    is_active: t.Optional[bool] = None


@strawberry.type
class BalancePrediction:
    original_balance: float
    new_balance: float
    change_amount: float
    percentage_change: float
    requires_approval: bool
    risk_level: str


@strawberry.type
class Mutation:
    @strawberry.mutation
    def update_account(self, id: int, data: AccountUpdateInput, session: Session = None) -> AccountType:
        """Update specific attributes of an account."""
        account = session.query(Account).get(id)
        if not account:
            raise ValueError(f"Account with ID {id} not found")
        
        # Update only the provided attributes
        update_data = {}
        if data.balance is not None:
            update_data["balance"] = int(data.balance * 100)  # Convert to cents
        if data.account_type is not None:
            update_data["account_type"] = data.account_type
        if data.is_active is not None:
            update_data["is_active"] = data.is_active
        
        # Update the model
        for attr_name, attr_value in update_data.items():
            setattr(account, attr_name, attr_value)
        
        session.commit()
        return AccountType.from_model(account)
    
    @strawberry.mutation
    def update_customer(self, id: int, data: CustomerUpdateInput, session: Session = None) -> CustomerType:
        """Update specific attributes of a customer."""
        customer = session.query(Customer).get(id)
        if not customer:
            raise ValueError(f"Customer with ID {id} not found")
        
        # Update only the provided attributes
        if data.name is not None:
            customer.name = data.name
        if data.email is not None:
            customer.email = data.email
        if data.phone is not None:
            customer.phone = data.phone
        if data.is_active is not None:
            customer.is_active = data.is_active
        
        session.commit()
        return CustomerType.from_model(customer)
    
    @strawberry.mutation
    def predict_account_balance_update(self, id: int, new_balance: float, session: Session = None) -> BalancePrediction:
        """Predict the impact of updating an account balance."""
        account = session.query(Account).get(id)
        if not account:
            raise ValueError(f"Account with ID {id} not found")
        
        # Use the predictor to generate predictions
        predictor = BalanceUpdatePredictor()
        prediction = predictor.predict_balance_impact(account, int(new_balance * 100))
        
        return BalancePrediction(
            original_balance=prediction["original_balance"],
            new_balance=prediction["new_balance"],
            change_amount=prediction["change_amount"],
            percentage_change=prediction["percentage_change"],
            requires_approval=prediction["requires_approval"],
            risk_level=prediction["risk_level"]
        )


@strawberry.type
class Query:
    @strawberry.field
    def account(self, id: int, session: Session = None) -> t.Optional[AccountType]:
        account = session.query(Account).get(id)
        return AccountType.from_model(account) if account else None
    
    @strawberry.field
    def customer(self, id: int, session: Session = None) -> t.Optional[CustomerType]:
        customer = session.query(Customer).get(id)
        return CustomerType.from_model(customer) if customer else None


# ====== Approach 3: Pydantic Models for Validation ======

class AccountUpdate(BaseModel):
    balance: t.Optional[float] = None
    account_type: t.Optional[str] = None
    is_active: t.Optional[bool] = None
    
    class Config:
        orm_mode = True
    
    def to_orm_dict(self) -> dict:
        """Convert to dict appropriate for ORM updates."""
        result = {}
        if self.balance is not None:
            result["balance"] = int(self.balance * 100)  # Convert to cents
        if self.account_type is not None:
            result["account_type"] = self.account_type
        if self.is_active is not None:
            result["is_active"] = self.is_active
        return result


class CustomerUpdate(BaseModel):
    name: t.Optional[str] = None
    email: t.Optional[str] = None
    phone: t.Optional[str] = None
    is_active: t.Optional[bool] = None
    
    class Config:
        orm_mode = True


# Example usage with Pydantic models
def update_account_with_pydantic(session: Session, account_id: int, update_data: AccountUpdate) -> Account:
    """Update an account using a Pydantic model for validation."""
    account = session.query(Account).get(account_id)
    if not account:
        raise ValueError(f"Account with ID {account_id} not found")
    
    # Convert Pydantic model to ORM-compatible dict
    update_dict = update_data.to_orm_dict()
    
    # Update the account
    for key, value in update_dict.items():
        setattr(account, key, value)
    
    session.commit()
    return account


# ====== Main Example Usage ======

def example_usage():
    """Example of how to use the different update approaches."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Create engine and session
    engine = create_engine("sqlite:///banking.db")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    # Example 1: Python attribute-based update
    updater = DomainModelUpdater(session)
    result = updater.update_model(Account, 1, {"balance": 15000, "is_active": True})
    print(f"Updated account: {result}")
    
    # Example 2: Update with validation and prediction
    account = session.query(Account).get(1)
    predictor = BalanceUpdatePredictor()
    prediction = predictor.predict_balance_impact(account, 20000)
    print(f"Balance update prediction: {prediction}")
    
    if not prediction["requires_approval"]:
        updater.update_model(Account, 1, {"balance": 20000})
        print("Account updated based on prediction")
    else:
        print("Account update requires approval")
    
    # Example 3: Using Pydantic models
    try:
        update_data = AccountUpdate(balance=250.50, is_active=True)
        updated_account = update_account_with_pydantic(session, 1, update_data)
        print(f"Updated account with Pydantic: {updated_account}")
    except ValueError as e:
        print(f"Error: {e}")
    
    # Example 4: Batch update
    count = updater.update_model_batch(Account, {"is_active": False}, {"is_active": True})
    print(f"Batch updated {count} accounts")


if __name__ == "__main__":
    example_usage()