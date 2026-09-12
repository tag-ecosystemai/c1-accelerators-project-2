from .database import Base, engine
from .models.job import Job


Base.metadata.create_all(bind=engine)