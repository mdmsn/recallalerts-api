from sqlalchemy import Boolean, Column, Integer, String, Identity, Computed, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base


class Subscriber(Base):
    __tablename__ = "subscriber"

    username = Column(String(15), unique=True, nullable=False, index=True)
    mobile_number = Column(String(15), index=True)
    email = Column(String(320), index=True, nullable=False)
    deactivated = Column(Boolean, default=False, nullable=False)
    fcm_token = Column(String(255), index=True)
    id = Column(Integer, primary_key=True, index=True)
    password = Column(Text, nullable=False)
    subscriptions =  relationship("Subscription", back_populates="owner")
    recalls = relationship("RecalledSubscription", back_populates="recall_owner")


class Subscription(Base):
	__tablename__ = "subscription"

	product = Column(String(200), nullable=False, index=True)
	subscription_date = Column(Date, nullable=False, index=True)
	description = Column(String(1000), index=True)
	id = Column(Integer, primary_key=True, index=True)
	subscriber_id = Column(Integer, ForeignKey("subscriber.id"))
	owner = relationship("Subscriber", back_populates="subscriptions")


class RecalledSubscription(Base):
    __tablename__ = "recalled_subscription"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscription.id"))
    recall_id = Column(Integer, ForeignKey("recall.id"))
    subscriber_id = Column(Integer, ForeignKey("subscriber.id"))
    recall_owner = relationship("Subscriber", back_populates="recalls")


class Recall(Base):
    __tablename__ = "recall"

    recall_date = Column(Date, nullable=False, index=True)
    id = Column(Integer, primary_key=True, index=True)
    summary = Column(String(1000), nullable=False, index=True)
    product = Column(String(200), nullable=False, index=True)