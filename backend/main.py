from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, SessionLocal
from auth import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM # <--- New import
from jose import JWTError, jwt
# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = [
    "http://localhost:5173", # This is where React will live
    "http://localhost:3000", # Alternate React port
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# @app.get("/")
# def read_root():
#     return {"message": "Welcome to Universal Booking API"}

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Find the user in the DB
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user
@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Check if email already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Create new user object (In a real app, we would hash the password here!)
    new_business = models.Business(name=user.business.name, industry=user.business.industry)
    db.add(new_business)
    db.flush()  # To get the new_business.id
    # 3. Create the User, linking it to the new business
    print("DEBUG: The password type is:", type(user.password))
    print("DEBUG: The password value is:", user.password)
    new_user = models.User(
        email=user.email, 
        hashed_password=get_password_hash(user.password), # Hash the password
        business_id=new_business.id # We can use the ID now!
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/services/", response_model=schemas.ServiceResponse)
def create_service(service: schemas.ServiceCreate, business_id: int, db: Session = Depends(get_db)):
    # 1. Create the service object
    new_service = models.Service(
        name=service.name,
        duration=service.duration,
        price=service.price,
        business_id=business_id
    )
    
    # 2. Save to DB
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    
    return new_service



@app.get("/services/", response_model=list[schemas.ServiceResponse])
def read_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    services = db.query(models.Service).offset(skip).limit(limit).all()
    return services

@app.post("/bookings/", response_model=schemas.BookingResponse)
def create_booking(
    booking: schemas.BookingCreate, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    service = db.query(models.Service).filter(models.Service.id == booking.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    new_end_time = booking.start_time + timedelta(minutes=service.duration)

    collision = db.query(models.Booking).filter(
        models.Booking.service_id == booking.service_id,
        models.Booking.start_time < new_end_time,
        models.Booking.end_time > booking.start_time
    ).first()

    if collision:
        raise HTTPException(status_code=400, detail="Time slot already booked")

    new_booking = models.Booking(
        user_id=current_user.id, 
        service_id=booking.service_id,
        start_time=booking.start_time,
        end_time=new_end_time,
        booking_time=datetime.now()
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return new_booking
# In backend/main.py

@app.get("/my-bookings/", response_model=list[schemas.BookingResponse])
def read_user_bookings(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Query the DB for bookings where user_id matches the Token's ID
    bookings = db.query(models.Booking).filter(models.Booking.user_id == current_user.id).all()
    return bookings

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # DEBUG 1: Check what is coming in from the form
    print("DEBUG: Form Email:", form_data.username)
    print("DEBUG: Form Password:", form_data.password)

    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # DEBUG 2: Check if we found the user
    if not user:
        print("DEBUG: User NOT found in database")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print("DEBUG: User found! ID:", user.id)
    print("DEBUG: Stored Hash:", user.hashed_password)

    # DEBUG 3: Check the password verification
    is_password_correct = verify_password(form_data.password, user.hashed_password)
    print("DEBUG: Password match result:", is_password_correct)

    if not is_password_correct:
        print("DEBUG: Password mismatch")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}