from app.db import Base, engine, SessionLocal
from app.models import Location, Employee
Base.metadata.create_all(engine)
with SessionLocal() as db:
    if not db.query(Location).first():
        a, b = Location(name="Точка А"), Location(name="Точка Б")
        db.add_all([a, b]); db.flush()
        db.add_all([Employee(telegram_id=829485533, full_name="ivan", location_id=a.id),
                    Employee(telegram_id=812902706, full_name="лиза", location_id=b.id)])
        db.commit()
print("Готово. Замените демонстрационные Telegram ID в seed.py.")
