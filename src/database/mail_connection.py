from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config.config import MAIL_DATABASE_URL

# engine_mail = create_engine(MAIL_DATABASE_URL, pool_size=5, max_overflow=2, pool_timeout=20, pool_recycle=1800, echo=False)
# SessionMail = sessionmaker(autocommit=False, autoflush=False, bind=engine_mail)

# BaseMail = declarative_base()

# def get_mail_db():
#     db = SessionMail()
#     try:
#         yield db
#     finally:
#         db.close()
