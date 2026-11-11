from contextlib import contextmanager

from sqlalchemy.orm import Session


@contextmanager
def transaction(db: Session):
    """
    Database Transaction Context Manager

    Automatically:
    - Commit if successful
    - Rollback if any exception occurs
    """

    try:
        yield

        db.commit()

    except Exception:
        db.rollback()
        raise