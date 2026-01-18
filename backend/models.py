from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    business = relationship("Business", back_populates="owner")
    business_id = Column(Integer, ForeignKey('businesses.id'))
class Business(Base):
    __tablename__ = 'businesses'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    industry = Column(String)
    owner = relationship("User", back_populates="business")

    services = relationship("Service", back_populates="business")
class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    duration = Column(Integer)  # duration in minutes
    price = Column(Integer)

    # Link to Business (Who offers this?)
    business_id = Column(Integer, ForeignKey('businesses.id'))
    business = relationship("Business", back_populates="services")

class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime)
    booking_time = Column(DateTime)

    # Link to User (Who booked?)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User")

    # Link to Service (What service?)
    service_id = Column(Integer, ForeignKey('services.id'))
    service = relationship("Service")