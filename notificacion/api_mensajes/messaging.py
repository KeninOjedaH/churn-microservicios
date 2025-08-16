import os
from twilio.rest import Client
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
TWILIO_SMS_NUMBER = os.getenv("TWILIO_SMS_NUMBER")

async def send_whatsapp_message(phone_number: str, message_content: str):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            body=message_content,
            to=f"whatsapp:{phone_number}"
        )
        return message.sid
    except Exception as e:
        print(f"Error al enviar el mensaje de WhatsApp: {e}")
        raise

async def get_message_from_excel(offer_id: str):
    try:
        df = pd.read_excel("ofertas.xlsx")
        df.columns = df.columns.str.lower()
        message = df.iloc[df.index[df['offerid'] == offer_id][0], 2]
        return message.replace("“", "").replace("”", "")
    except Exception as e:
        print(f"Error al leer el archivo Excel: {e}")
        raise
