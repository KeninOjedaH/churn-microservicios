import pandas as pd
import requests
import time
import logging

# ───── Configuración de logging ─────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# Ruta al archivo Excel con los datos
ARCHIVO_EXCEL = "clientes.xlsx"
URL_API = "http://localhost:6000/predecir_churn/"

# Leer el archivo Excel
df = pd.read_excel(ARCHIVO_EXCEL, engine="openpyxl")

# Lista para almacenar resultados
resultados = []

# Enviar cada fila como una petición al servicio
for idx, row in df.iterrows():
    payload = row.to_dict()
    msisdn = payload.get("msisdn", f"fila_{idx}")

    logging.info(f"📤 Enviando datos para cliente {msisdn}")
    logging.info(f"JSON de entrada: {payload}")

    try:
        response = requests.post(URL_API, json=payload)
        if response.status_code == 200:
            data = response.json()
            logging.info(f"✅ Respuesta recibida para {msisdn}: {data}")
            resultados.append(data)
        else:
            logging.warning(f"❌ Error HTTP {response.status_code} para {msisdn}")
            logging.warning(f"🔁 Respuesta completa: {response.text}")
    except Exception as e:
        logging.error(f"⚠️ Error al enviar datos del cliente {msisdn}: {e}")

    time.sleep(0.1)  # Pausa opcional

# Guardar resultados en CSV
if resultados:
    pd.DataFrame(resultados).to_csv("resultados_churn.csv", index=False)
    logging.info("📁 Resultados guardados en 'resultados_churn.csv'")
