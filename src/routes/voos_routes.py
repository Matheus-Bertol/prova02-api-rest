from datetime import datetime, timedelta

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlmodel import select

from src.config.database import get_session
from src.models.voos_model import Voo

voos_router = APIRouter(prefix="/voos")


# POST /voos
@voos_router.post("")
def cria_voo(voo: Voo):
    with get_session() as session:
        LIMITE_HORAS = 2
        hora_atual = datetime.now()
        hora_limite = hora_atual + timedelta(hours=LIMITE_HORAS)
        no_horario_limite = voo.data_saida <= hora_limite
        print("horario_limite", no_horario_limite, hora_limite)

        if no_horario_limite:
            return JSONResponse(
                content={
                    "message": f"Impossível incluir vôos com menos de {LIMITE_HORAS} horas antes da saída"
                },
                status_code=403,
            )

        session.add(voo)
        session.commit()
        session.refresh(voo)
        return voo

# GET /voos/vendas
@voos_router.get("/vendas")
def lista_voos_venda():
    LIMITE_HORAS = 2
    with get_session() as session:
        hora_limite = datetime.now() + timedelta(hours=LIMITE_HORAS)
        statement = select(Voo).where(Voo.data_saida >= hora_limite)
        voo = session.exec(statement).all()
        return voo

@voos_router.get("")
def lista_voos():
    with get_session() as session:
        statement = select(Voo)
        voo = session.exec(statement).all()
        return voo

# TODO - Implementar rota que retorne as poltronas por id do voo 