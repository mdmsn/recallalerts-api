from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field


class UserAuthenticate(BaseModel):
    username: str
    password: str


class SubscriberUpdate(BaseModel):
	new_password: str
	new_email: str
	new_mobile: str


class SubscriptionBase(BaseModel):
	product: str
	description: str
	subscription_date: date
	subscriber_id: int


class Subscription(SubscriptionBase):
	id: int
	class Config:
		orm_mode = True


class SubscriptionCreate(SubscriptionBase):
    pass


class RecalledSubscriptionBase(BaseModel):
	pass
	
	
class RecalledSubscriptionCreate(RecalledSubscriptionBase):
    pass


class RecalledSubscription(RecalledSubscriptionBase):
	id: int
	subscription_id: int
	recall_id: int
	class Config:
		orm_mode = True
		
		
class RecallBase(BaseModel):
	recall_date: date
	summary: str
	product: str


class Recall(RecallBase):
	id: int
	class Config:
		orm_mode = True


class RecallCreate(RecallBase):
	pass
		
		
class SubscriberBase(BaseModel):
    username: str
    email: str
    mobile_number: str
    fcm_token: str
    deactivated: bool = Field(default=False)
    

class SubscriberCreate(SubscriberBase):
    password: str
    

class Subscriber(SubscriberBase):
	id: int
	subscriptions: List[Subscription] = []
	recalls: List[RecalledSubscription] = []

	class Config:
		orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None