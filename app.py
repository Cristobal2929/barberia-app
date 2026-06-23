# -*- coding: utf-8 -*-
import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import Column, Integer, String, Date, Time, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# -------------------------
# Database configuration
# -------------------------
DATABASE_URL = "sqlite:///appointments.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)


# Create tables if they do not exist
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# Routes
# -------------------------
@app.get("/", response_class=HTMLResponse)
def read_root():
    # Services list (hard‑coded)
    services = [
        ("Haircut", "$15"),
        ("Shave", "$10"),
        ("Haircut + Shave", "$20"),
        ("Beard Trim", "$12"),
    ]

    # Retrieve appointments
    db = next(get_db())
    appointments = (
        db.query(Appointment)
        .order_by(Appointment.date, Appointment.time)
        .all()
    )

    # Build HTML page
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Barberia</title>
        <style>
            body {font-family:Arial, sans-serif; margin:0; padding:0; background:#f4f4f4;}
            .container {max-width:800px; margin:auto; padding:20px; background:#fff; box-shadow:0 0 10px rgba(0,0,0,0.1);}
            h1, h2 {text-align:center;}
            table {width:100%; border-collapse:collapse; margin-top:20px;}
            th, td {border:1px solid #ddd; padding:8px; text-align:left;}
            th {background:#f2f2f2;}
            form {display:flex; flex-direction:column; gap:10px; margin-top:20px;}
            input, select {padding:8px; font-size:1rem; width:100%;}
            button {padding:10px; background:#28a745; color:#fff; border:none; cursor:pointer;}
            button:hover {background:#218838;}
            @media (max-width:600px) {
                .container {padding:10px;}
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Barberia</h1>

            <h2>Servicios y precios</h2>
            <table>
                <tr><th>Servicio</th><th>Precio</th></tr>
    """
    for service, price in services:
        html += f"<tr><td>{service}</td><td>{price}</td></tr>"
    html += """
            </table>

            <h2>Solicitar cita</h2>
            <form method="post" action="/appointments">
                <input type="text" name="name" placeholder="Nombre" required>
                <input type="tel" name="phone" placeholder="Telefono" required>
                <input type="date" name="date" required>
                <input type="time" name="time" required>
                <button type="submit">Reservar</button>
            </form>

            <h2>Citas programadas</h2>
            <table>
                <tr><th>Nombre</th><th>Telefono</th><th>Fecha</th><th>Hora</th></tr>
    """
    for appt in appointments:
        html += f"<tr><td>{appt.name}</td><td>{appt.phone}</td><td>{appt.date}</td><td>{appt.time}</td></tr>"
    html += """
            </table>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.post("/appointments")
def create_appointment(
    name: str = Form(...),
    phone: str = Form(...),
    date: str = Form(...),
    time: str = Form(...),
):
    db = next(get_db())
    new_appt = Appointment(name=name, phone=phone, date=date, time=time)
    db.add(new_appt)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    import os, uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))