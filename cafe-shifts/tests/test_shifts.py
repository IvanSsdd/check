from datetime import datetime
from app.service import arrive, leave, monthly_hours, current_staff
from app.models import Shift

def test_duplicate_arrival_does_not_create_second_shift(db):
    now = datetime(2026, 5, 10, 9)
    assert arrive(db, 111, now)[0] is True
    assert arrive(db, 111, now)[0] is False
    assert db.query(Shift).filter(Shift.employee_id == 1).count() == 1

def test_overnight_shift_is_four_hours(db):
    arrive(db, 111, datetime(2026, 5, 10, 22))
    leave(db, 111, datetime(2026, 5, 11, 2))
    assert monthly_hours(db, 1, 2026, 5)[0].hours == 4.0

def test_manager_location_scope_isolation(db):
    arrive(db, 111, datetime(2026, 5, 10, 9))
    arrive(db, 222, datetime(2026, 5, 10, 10))
    assert [r[0] for r in current_staff(db, 1)] == ["Анна"]
    assert [r[0] for r in current_staff(db, 2)] == ["Борис"]
    assert [r[1] for r in monthly_hours(db, 1, 2026, 5)] == ["Анна"]
