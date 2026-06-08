from contextlib import contextmanager

from sqlmodel import Session, create_engine

from app.core.settings import get_settings

settings = get_settings()


def get_session():
    engine = create_engine(settings.POSTGRES_DSN.encoded_string())
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_context():
    return get_session()
