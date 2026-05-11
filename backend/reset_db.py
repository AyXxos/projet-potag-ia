from database import Base, SessionLocal, engine
import main


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        main.seed_database(db)
    finally:
        db.close()


if __name__ == "__main__":
    reset_database()
