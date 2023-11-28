import random

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlmodel import select

from src.config.database import get_session
from src.models.reservas_model import Reserva
from src.models.voos_model import Voo

reservas_router = APIRouter(prefix="/reservas")


@reservas_router.get("/{id_voo}")
def lista_reservas_voo(id_voo: int):
    with get_session() as session:
        statement = select(Reserva).where(Reserva.voo_id == id_voo)
        reservas = session.exec(statement).all()
        return reservas


@reservas_router.post("")
def cria_reserva(reserva: Reserva):
    with get_session() as session:
        voo = session.exec(select(Voo).where(Voo.id == reserva.voo_id)).first()
        
        ## TODO - Validar se existe uma reserva para o mesmo documento
        
        # Verifica se já existe uma reserva para o mesmo documento
        existing_reserva = session.exec(
            select(Reserva).where(
                (Reserva.voo_id == reserva.voo_id) & (Reserva.documento == reserva.documento)
            )
        ).first()

        if existing_reserva:
            return JSONResponse(
                content={"message": f"Já existe uma reserva para o documento {reserva.documento} no voo {reserva.voo_id}."},
                status_code=400,
            )
        #######

        if not voo:
            return JSONResponse(
                content={"message": f"Voo com id {reserva.voo_id} não encontrado."},
                status_code=404,
            )

        codigo_reserva = "".join(
            [str(random.randint(0, 999)).zfill(3) for _ in range(2)]
        )

        reserva.codigo_reserva = codigo_reserva
        session.add(reserva)
        session.commit()
        session.refresh(reserva)
        return reserva


@reservas_router.post("/{codigo_reserva}/checkin/{num_poltrona}")
def faz_checkin(codigo_reserva: str, num_poltrona: int):
    with get_session() as session:
        
        # Buscar a reserva pelo código da reserva
        reserva = session.exec(
            select(Reserva).where(Reserva.codigo_reserva == codigo_reserva)
        ).first()

        if not reserva:
            raise HTTPException(
                status_code=404,
                detail="Reserva não encontrada",
            )

        # Buscar o voo pelo id do voo da reserva
        voo = session.get(Voo, reserva.voo_id)

        if not voo:
            raise HTTPException(
                status_code=404,
                detail=f"Voo com id {reserva.voo_id} não encontrado.",
            )

        # Verificar se a poltrona está livre
        nome_poltrona = f"poltrona_{num_poltrona}"
        if getattr(voo, nome_poltrona) is not None:
            raise HTTPException(
                status_code=400,
                detail=f"Poltrona {num_poltrona} já está ocupada.",
            )

        # Atualizar o campo da poltrona com o código da reserva
        setattr(voo, nome_poltrona, codigo_reserva)

        # Commit e retornar a reserva atualizada
        session.commit()
        return reserva
    
@reservas_router.patch("/{codigo_reserva}/checkin/{num_poltrona}")
def faz_checkin_patch(codigo_reserva: str, num_poltrona: int):
    with get_session() as session:
        # Buscar a reserva pelo código da reserva
        reserva = session.exec(
            select(Reserva).where(Reserva.codigo_reserva == codigo_reserva)
        ).first()

        if not reserva:
            raise HTTPException(
                status_code=404,
                detail="Reserva não encontrada",
            )

        # Buscar o voo pelo id do voo da reserva
        voo = session.get(Voo, reserva.voo_id)

        if not voo:
            raise HTTPException(
                status_code=404,
                detail=f"Voo com id {reserva.voo_id} não encontrado.",
            )

        # Verificar se a poltrona está livre
        nome_poltrona = f"poltrona_{num_poltrona}"
        if getattr(voo, nome_poltrona) is not None:
            raise HTTPException(
                status_code=403,
                detail=f"Poltrona {num_poltrona} já está ocupada.",
            )

        # Atualizar o campo da poltrona com o código da reserva
        setattr(voo, nome_poltrona, codigo_reserva)

        # Commit e retornar a reserva atualizada
        session.commit()
        return reserva