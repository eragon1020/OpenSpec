from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TipoEspacio(str, Enum):
    laboratorio = "laboratorio"
    auditorio = "auditorio"
    sala_computo = "sala_computo"


class EspacioBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    tipo: TipoEspacio
    capacidad: int = Field(gt=0, strict=True)

    @field_validator("nombre")
    @classmethod
    def normalizar_nombre(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío")
        if len(value) > 120:
            raise ValueError("El nombre no puede superar los 120 caracteres")
        return value


class EspacioCreate(EspacioBase):
    pass


class EspacioUpdate(EspacioBase):
    pass


class EspacioRead(EspacioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activo: bool
