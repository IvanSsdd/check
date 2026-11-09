from datetime import datetime, timedelta
from sqlalchemy import select, func, case, and_, or_
from sqlalchemy.orm import Session
from .models import Employee, Shift

def arrive(db: Session, telegram_id: int, now: datetime | None = None):
    emp = db.scalar(select(Employee).where(Employee.telegram_id == telegram_id))
    if emp is None:
        return False, "Ваш аккаунт не привязан к точке. Обратитесь к менеджеру."
    opened = db.scalar(select(Shift).where(Shift.employee_id == emp.id, Shift.ended_at.is_(None)))
    if opened:
        return False, "Вы уже отметились — смена открыта."
    db.add(Shift(employee_id=emp.id, started_at=now or datetime.now()))
    db.commit()
    return True, "Приход отмечен. Хорошей смены!"

def leave(db: Session, telegram_id: int, now: datetime | None = None):
    emp = db.scalar(select(Employee).where(Employee.telegram_id == telegram_id))
    if emp is None:
        return False, "Ваш аккаунт не привязан к точке. Обратитесь к менеджеру."
    opened = db.scalar(select(Shift).where(Shift.employee_id == emp.id, Shift.ended_at.is_(None)))
    if opened is None:
        return False, "У вас нет открытой смены."
    ended = now or datetime.now()
    if ended < opened.started_at:
        ended += timedelta(days=1)
    opened.ended_at = ended
    db.commit()
    return True, "Уход отмечен. Смена закрыта."

def current_staff(db: Session, location_id: int):
    return db.execute(
        select(Employee.full_name, Shift.started_at)
        .join(Shift, Shift.employee_id == Employee.id)
        .where(Employee.location_id == location_id, Shift.ended_at.is_(None))
        .order_by(Employee.full_name)
    ).all()

def monthly_hours(db: Session, location_id: int, year: int, month: int):
    start = datetime(year, month, 1)
    end = datetime(year + (month == 12), 1 if month == 12 else month + 1, 1)
    effective_end = case((Shift.ended_at.is_(None), func.datetime("now")), else_=Shift.ended_at)
    clipped_start = case((Shift.started_at < start, start), else_=Shift.started_at)
    clipped_end = case((effective_end > end, end), else_=effective_end)
    total = func.sum((func.julianday(clipped_end) - func.julianday(clipped_start)) * 24.0)
    stmt = (select(Employee.id, Employee.full_name, func.coalesce(total, 0.0).label("hours"))
            .outerjoin(Shift, and_(Shift.employee_id == Employee.id, Shift.started_at < end,
                                   or_(Shift.ended_at.is_(None), Shift.ended_at > start)))
            .where(Employee.location_id == location_id)
            .group_by(Employee.id, Employee.full_name).order_by(Employee.full_name))
    return db.execute(stmt).all()
