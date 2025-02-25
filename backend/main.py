from fastapi import FastAPI, HTTPException, Request, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List,Dict
import uuid
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text
import jwt
from passlib.context import CryptContext
from email_validator import validate_email, EmailNotValidError
from starlette.middleware.base import BaseHTTPMiddleware
import re

# Configuration de la sécurité
SECRET_KEY = "your-secret-key-here"  # À changer en production !
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuration du hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuration de la base de données SQLite avec paramètres de sécurité
SQLALCHEMY_DATABASE_URL = "sqlite:///./twitter_clone.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={
        "check_same_thread": False,
        "timeout": 30,  # Timeout en secondes
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèles SQLAlchemy sécurisés
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    avatar = Column(String(200))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class TweetDB(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    content = Column(String(280), nullable=False)  # Limite Twitter standard
    likes = Column(Integer, default=0)
    retweets = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# Création des tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Middleware pour intercepter les erreurs 404
class Catch404Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Si la requête est déjà sur la page d'erreur, ne pas rediriger
        if request.url.path.startswith("/error"):
            response = await call_next(request)
        else:
            response = await call_next(request)
            if response.status_code == 404:
                response = RedirectResponse(url="/error/404")
        return response

# CORS middleware avec restrictions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restreindre aux origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ajouter le middleware Catch404
app.add_middleware(Catch404Middleware)


class UserLogin(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=8, max_length=50)

class UserTweet(BaseModel):
    id: int
    username: str
    full_name: str
    avatar: str

class UpdatePwd(BaseModel):
    password : str 

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    avatar: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=8, max_length=50)
    email: EmailStr
    full_name: constr(min_length=2, max_length=100)

class Tweet(BaseModel):
    id: int
    userId: int
    content: constr(min_length=1, max_length=280)
    likes: int
    retweets: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TweetResponse(BaseModel):
    user: UserTweet
    tweet: Tweet

"""


----------------  FONCTIONS DE SECURITE -------------------------------------



"""
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def sanitize_input(input_string: str, max_length: int = 255) -> str:
    # Remove potentially dangerous characters
    sanitized = re.sub(r"[;\"'\\()=]", "", input_string)

    # Truncate the input to the maximum allowed length
    sanitized = sanitized[:max_length]

    return sanitized

# Dépendance pour la base de données avec protection contre les injections SQL
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dépendance pour obtenir l'utilisateur actuel
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserDB:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user is None:
        raise credentials_exception
    return user




"""


----------------  API USERS -------------------------------------


"""

@app.post("/api/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Log des données reçues
    print(f"Données reçues: {user.dict()}")
    
    # Validation de l'email
    try:
        valid = validate_email(user.email)
        user.email = valid.email
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Validation des champs obligatoires avec messages détaillés
    if len(user.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters long")
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if len(user.full_name) < 2:
        raise HTTPException(status_code=400, detail="Full name must be at least 2 characters long")
    
    user.username = sanitize_input(user.username)
    user.full_name = sanitize_input(user.full_name)
    
    # Vérification de l'existence de l'utilisateur
    db_user = db.query(UserDB).filter(
        func.lower(UserDB.username) == func.lower(user.username)
    ).first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    try:
        # Création de l'utilisateur
        new_user = UserDB(
            username=user.username,
            password_hash=get_password_hash(user.password),
            email=user.email,
            full_name=user.full_name,
            avatar=f"https://i.pravatar.cc/150?img={uuid.uuid4().int % 70}"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"message": "User created", "user_id": new_user.id}
        
    except Exception as e:
        db.rollback()
        print(f"Erreur de base de données: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")


@app.post("/api/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
         
        user.username = sanitize_input(user.username)
        # Recherche de l'utilisateur de manière sécurisée
        user_db = db.query(UserDB).filter(UserDB.username == user.username).first()
        
        # Vérification de l'utilisateur et du mot de passe
        if not user_db:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )
            
        if not verify_password(user.password, user_db.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )
        
        # Création du token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_db.username},
            expires_delta=access_token_expires
        )
        
        # Retour de la réponse
        return {
            "authToken": access_token,
            "token_type": "bearer",
            "user_id": user_db.id
        }
        
    except Exception as e:
        print(f"Login error: {str(e)}")  # Pour le debugging
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/users/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    current_user: UserDB = Depends(get_current_user),  # Ajout de la vérification
    db: Session = Depends(get_db)
):
    user.username = sanitize_input(user.username)
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user




@app.patch("/api/users/{user_id}/password")
def change_pwd(user_id: int,password : UpdatePwd,current_user: UserDB = Depends(get_current_user),  # Ajout de la vérification
    db: Session = Depends(get_db)):
    new_pwd = password.password
    hashed_password = get_password_hash(new_pwd)

    user_db = db.query(UserDB).filter(UserDB.id == user_id).first()
    
    if user_db:
        user_db.password_hash = hashed_password
        db.commit()
        db.refresh(user_db) 
        return {"message": "password updated"}
    raise HTTPException(status_code=404, detail="user not found")



"""


----------------  API TWEETS -------------------------------------


"""
@app.get("/api/tweets/{user_id}", response_model=List[TweetResponse])
async def get_tweet_user(user_id: int,current_user: UserDB = Depends(get_current_user),  # Ajout de la vérification
   db: Session = Depends(get_db)):
    tweets = (
        db.query(TweetDB, UserDB)
        .join(UserDB, TweetDB.userId == UserDB.id)
        .filter(TweetDB.userId == user_id)  
        .order_by(TweetDB.created_at.desc())  # Trier par date décroissante
        .limit(10)
        .all()
    )

    result = []
    for tweet, user in tweets:
        tweet_obj = Tweet(
            id=tweet.id,
            userId=tweet.userId,
            content=tweet.content,
            likes=tweet.likes,
            retweets=tweet.retweets,
            created_at=tweet.created_at,
            updated_at=tweet.updated_at
        )
        user_obj = UserTweet(
            id=user.id,
            full_name=user.full_name,
            username=user.username,
            avatar=user.avatar
        )
        result.append(TweetResponse(user=user_obj, tweet=tweet_obj))

    return result



@app.get("/api/tweets", response_model=List[TweetResponse])
async def get_all_tweets( 
   db: Session = Depends(get_db)):
    # Effectuer la jointure entre Tweet et User, récupérer les 10 tweets les plus récents
    tweets = db.query(TweetDB, UserDB).join(UserDB, TweetDB.userId == UserDB.id).order_by(TweetDB.created_at.desc()).limit(10).all()

    result = []
    for tweet, user in tweets:
        tweet_obj = Tweet(
            id=tweet.id,
            userId=tweet.userId,
            content=tweet.content,
            likes=tweet.likes,
            retweets=tweet.retweets,
            created_at=tweet.created_at,
            updated_at=tweet.updated_at
        )
        user_obj = UserTweet(
            id=user.id,
            full_name=user.full_name,
            username=user.username,
            avatar=user.avatar
        )
        result.append(TweetResponse(user=user_obj, tweet=tweet_obj))

    return result

@app.patch("/api/tweets/{tweet_id}/like")
async def like_tweet(tweet_id: int,current_user: UserDB = Depends(get_current_user),  # Ajout de la vérification
    db: Session = Depends(get_db)):
    tweet = db.query(TweetDB).filter(TweetDB.id == tweet_id).first()
    if tweet:
        tweet.likes += 1
        db.commit()
        return {"message": "Tweet liked"}
    raise HTTPException(status_code=404, detail="Tweet not found")

@app.patch("/api/tweets/{tweet_id}/retweet")
async def retweet(tweet_id: int,current_user: UserDB = Depends(get_current_user),  # Ajout de la vérification
    db: Session = Depends(get_db)):
    tweet = db.query(TweetDB).filter(TweetDB.id == tweet_id).first()
    if tweet:
        tweet.retweets += 1
        db.commit()
        return {"message": "Tweet retweeted"}
    raise HTTPException(status_code=404, detail="Tweet not found")



@app.post("/api/tweets", response_model=Tweet)
async def create_tweet(
    content: str,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),  # Ajout de la vérification
   
):
    if not content or len(content) > 280:
        raise HTTPException(status_code=400, detail="Invalid tweet content")

    tweet = TweetDB(
        userId=user_id,
        content=content,
        likes=0,
        retweets=0
    )
    
    db.add(tweet)
    try:
        db.commit()
        db.refresh(tweet)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database error")
    
    return tweet



"""


----------------  gestion des erreurs  -------------------------------------


"""

# Handler pour TOUTES les erreurs HTTP (y compris 403, 500, etc.)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return RedirectResponse(url=f"/error/{exc.status_code}")

# Handler pour les erreurs générales
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return RedirectResponse(url="/error/777") 


# Route unique pour afficher la page d'erreur
@app.get("/error/{error_code}")
async def error_page(error_code: int):
    html_content = f"""
        <html>
        <head><title>Erreur {error_code}</title></head>
        <body>
            <h1>Erreur {error_code}</h1>
            <p>tu n'est pas sur la bonne piste .</p>
           <a href="/">Retour à l'accueil</a>
       </body>
        <!-- A tu essayé de te creer un compte ?  -->
    </html>
    """
    return HTMLResponse(content=html_content, status_code=777)

# Route unique pour afficher la page d'erreur
@app.post("/error/{error_code}")
async def error_page(error_code: int):
    html_content = f"""
        <html>
        <head><title>Erreur {error_code}</title></head>
        <body>
            <h1>Erreur {error_code}</h1>
            <p>tu n'est pas sur la bonne piste .</p>
           <a href="/">Retour à l'accueil</a>
       </body>
        <!-- A tu essayé de te creer un compte ?  -->
    </html>
    """
    return HTMLResponse(content=html_content, status_code=777)



"""


----------------  ENDPOINTS HTML -------------------------------------


"""

# Routes HTML
@app.get("/")
async def serve_index():
    try:
        with open("../frontend/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend file not found")


@app.get("/profile", response_class=HTMLResponse)
async def profile_page():
    try:
        with open("../frontend/profile.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend file not found")

# Configuration des fichiers statiques avec sécurité
app.mount("/static", StaticFiles(directory="/var/www/html/frontend/static", html=True), name="frontend")

# Lancement du serveur
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
