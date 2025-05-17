from sqlalchemy.orm import Session
from app.models.actividades import ActividadesModel as Actividad
from app.database.db import SessionLocal

db: Session = SessionLocal()

actividades = db.query(Actividad).all()
for act in actividades:
    responsable = act.persona_responsable

    # Si es un dict plano con 'nombre' y no está ya en formato r0, r1...
    if isinstance(responsable, dict) and "nombre" in responsable and "r0" not in responsable:
        nuevo_formato = {
            "r0": {
                "nombre": responsable.get("nombre") or "",
                "puesto": responsable.get("puesto") or ""
            }
        }
        print(f"Convirtiendo actividad ID {act.id}: {responsable} → {nuevo_formato}")
        act.persona_responsable = nuevo_formato

db.commit()
db.close()