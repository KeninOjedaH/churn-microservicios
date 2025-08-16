from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional
import database
import messaging
import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI()
class MessageRequest(BaseModel):
    offerId: str
    msisdn: str
    channel: Literal["whatsapp"]
    discountPct: str
    validezHoras: str

@app.post("/send_message")
async def send_message(request: MessageRequest):
    try:
        # Obtener el mensaje del archivo Excel
        message_content = await messaging.get_message_from_excel(request.offerId)

        # Modificar el mensaje
        message_content += f" Tiene un descuento de S/. {request.discountPct} y la oferta es valida por {request.validezHoras} horas"

        # Registrar la transacción en la base de datos
        transaction_id = await database.create_transaction(
            phone_number=request.msisdn,
            message_type=request.channel,
            message_content=message_content
        )

        # Enviar el mensaje
        if request.channel == "whatsapp":
            whatsapp_status = await messaging.send_whatsapp_message(
                phone_number=request.msisdn,
                message_content=message_content
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid channel. Must be 'whatsapp'")

        # Actualizar el estado de la transacción en la base de datos
        await database.update_transaction_status(
            transaction_id=transaction_id,
            status="exito"
        )

        return {"status": "exito", "transaction_id": transaction_id, "whatsapp_status": whatsapp_status}

    except Exception as e:
        # Actualizar el estado de la transacción en la base de datos
        await database.update_transaction_status(
            transaction_id=transaction_id,
            status="error",
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
