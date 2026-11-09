import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db import Base
from app.models import Location, Employee

@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    a, b = Location(name="Точка А"), Location(name="Точка Б")
    session.add_all([a, b]); session.flush()
    session.add_all([Employee(telegram_id=111, full_name="Анна", location_id=a.id),
                     Employee(telegram_id=222, full_name="Борис", location_id=b.id)])
    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
