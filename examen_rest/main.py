from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine, get_db
from models import Laptop


class LaptopCreate(BaseModel):
    marca: str
    modelo: str
    ram_gb: int


class LaptopResponse(LaptopCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    disponible: bool


def cargar_laptops_iniciales() -> None:
    with SessionLocal() as db:
        if db.scalar(select(Laptop.id).limit(1)) is not None:
            return

        db.add_all(
            [
                Laptop(marca="Dell", modelo="Latitude 5440", ram_gb=16, disponible=True),
                Laptop(marca="Lenovo", modelo="ThinkPad E14", ram_gb=8, disponible=False),
                Laptop(marca="HP", modelo="ProBook 450", ram_gb=16, disponible=True),
            ]
        )
        db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    cargar_laptops_iniciales()
    yield


app = FastAPI(lifespan=lifespan)
DatabaseSession = Annotated[Session, Depends(get_db)]


@app.get("/")
def inicio() -> dict[str, str]:
    return {"mensaje": "API del laboratorio de cómputo"}


@app.get("/laptops", response_model=list[LaptopResponse])
def listar_laptops(db: DatabaseSession) -> list[Laptop]:
    return list(db.scalars(select(Laptop).order_by(Laptop.id)))


@app.get("/laptops/disponibles", response_model=list[LaptopResponse])
def listar_laptops_disponibles(db: DatabaseSession) -> list[Laptop]:
    consulta = select(Laptop).where(Laptop.disponible.is_(True)).order_by(Laptop.id)
    return list(db.scalars(consulta))


@app.get("/laptops/{laptop_id}", response_model=LaptopResponse)
def obtener_laptop(laptop_id: int, db: DatabaseSession) -> Laptop:
    laptop = db.get(Laptop, laptop_id)
    if laptop is None:
        raise HTTPException(status_code=404, detail="Laptop no encontrada")
    return laptop


@app.post("/laptops", response_model=LaptopResponse)
def crear_laptop(datos: LaptopCreate, db: DatabaseSession) -> Laptop:
    laptop = Laptop(**datos.model_dump(), disponible=True)
    db.add(laptop)
    db.commit()
    db.refresh(laptop)
    return laptop
