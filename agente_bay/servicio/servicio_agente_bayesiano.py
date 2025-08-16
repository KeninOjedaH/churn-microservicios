import os, re, logging, requests
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from dotenv import load_dotenv
import uvicorn

load_dotenv()
MSG_API    = os.getenv("MSG_API", "http://localhost:9000/decision")
JOB_LIB    = os.getenv("JOB_LIB", "joblib/agente_bayesiano_churn.joblib")

# Cargar modelo bayesiano entrenado
modelo = joblib.load(JOB_LIB)

# Crear instancia de FastAPI
app = FastAPI(title="Churn Risk Prediction Service")

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("agente-bayesiano")

# Modelo de entrada usando Pydantic
class ClienteInput(BaseModel):
    distrito: int
    msisdn: int
    tipo_plan: int
    plan_asignado: int
    cargo_plan: float
    minutos_mensuales: float
    gb_mensuales: float
    reclamos_mensual: int
    llamadas_soporte: int
    flag_disminucion_consumo: int
    monto_recarga_mensual: float
    facturas_atrasadas: int
    facturacion_mensual: float
    flag_oferta_recibida: int
    flag_oferta_aceptada: int
    segmento: str   # Ya no es opcional
    ticket_30_dias: int
    arpu_actual: float
    descarga_ult_30min: int

# Endpoint de predicción
@app.post("/predecir_churn/")
def predecir_churn(cliente: ClienteInput):
    # Convertir input a DataFrame
    entrada_df = pd.DataFrame([cliente.dict()])

    # Extraer datos necesarios para el modelo
    msisdn = entrada_df["msisdn"].iloc[0]
    segmento = entrada_df["segmento"].iloc[0]
    tickets30d = entrada_df["ticket_30_dias"].iloc[0]
    arpu_actual = entrada_df["arpu_actual"].iloc[0]
    descarga_ult_30min = entrada_df["descarga_ult_30min"].iloc[0]

    # Quitar msisdn antes de pasar al modelo
    entrada_modelo = entrada_df.drop(columns=["msisdn"])

    # Obtener probabilidad de churn (clase 1)
    prob_churn = modelo.predict_proba(entrada_modelo)[0][1]
    
    log.info("Probabilidad cruda de churn: %s", prob_churn)

    # Preparar respuesta
    resultado = {
        "segment": segmento,
        "riskChurn": round(float(prob_churn), 4),
        "tickets30d": int(tickets30d),
        "arpuActual": float(arpu_actual),
        "bytesDown30m": int(descarga_ult_30min),
        "msisdn": int(msisdn)
    }
    log.info("Payload a enviar a agente basado en conocimiento:",resultado)
    try:
        
        resp = requests.post(MSG_API, json=resultado, timeout=5)
        log.info("Mensaje enviado ➜ %s | status=%s", MSG_API, resp.status_code)
    except Exception as e:
        log.error("Error enviando mensaje: %s", e)
    return resultado

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6000)
