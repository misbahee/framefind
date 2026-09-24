from app.database import SessionLocal


def get_db():
    """ Provide a database session for requests. """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()