from sqlalchemy import Boolean, CheckConstraint, Column, Integer, String, true

from app.database import Base

TIPOS_ESPACIO = ("laboratorio", "auditorio", "sala_computo")


class Espacio(Base):
    __tablename__ = "espacios"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('laboratorio', 'auditorio', 'sala_computo')",
            name="ck_espacios_tipo",
        ),
        CheckConstraint("capacidad > 0", name="ck_espacios_capacidad_positiva"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    nombre_normalizado = Column(String(120), nullable=False, unique=True, index=True)
    tipo = Column(String(20), nullable=False)
    capacidad = Column(Integer, nullable=False)
    activo = Column(Boolean, nullable=False, default=True, server_default=true())
