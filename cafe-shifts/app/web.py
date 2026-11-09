import os
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from .db import Base, engine, get_db
from .service import current_staff, monthly_hours

load_dotenv()
Base.metadata.create_all(engine)
app = FastAPI(title="Cafe Shift Manager")
security = HTTPBasic()
MANAGERS = {
    os.getenv("MANAGER_A_USERNAME", "manager_a"): (os.getenv("MANAGER_A_PASSWORD", "change-this-a"), 1),
    os.getenv("MANAGER_B_USERNAME", "manager_b"): (os.getenv("MANAGER_B_PASSWORD", "change-this-b"), 2),
}

def manager_location(credentials: HTTPBasicCredentials = Depends(security)):
    account = MANAGERS.get(credentials.username)
    if not account or account[0] != credentials.password:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль",
                            headers={"WWW-Authenticate": "Basic"})
    return account[1]

@app.get("/", response_class=__import__("fastapi").responses.HTMLResponse)
def dashboard():
    return (Path(__file__).parent / "dashboard.html").read_text(encoding="utf-8")

@app.get("/api/current")
def api_current(location_id: int = Depends(manager_location), db: Session = Depends(get_db)):
    return [{"name": n, "started_at": t.isoformat()} for n, t in current_staff(db, location_id)]

@app.get("/api/hours")
def api_hours(month: str | None = None, location_id: int = Depends(manager_location), db: Session = Depends(get_db)):
    try:
        year, mon = map(int, (month or datetime.now().strftime("%Y-%m")).split("-"))
        if not 1 <= mon <= 12: raise ValueError()
    except ValueError:
        raise HTTPException(status_code=400, detail="month должен быть YYYY-MM")
    return [{"employee": n, "hours": round(float(h), 2)}
            for _, n, h in monthly_hours(db, location_id, year, mon)]
