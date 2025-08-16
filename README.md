# Sistema de recomendación y fidelización mediante agente basado en conocimiento y agente bayesiano para clientes del sector de telecomunicaciones en el Perú

Este proyecto implementa una arquitectura de microservicios para predecir la deserción de clientes (churn) y notificarles ofertas personalizadas, integrando modelos de machine learning, reglas de negocio y mensajería multicanal.

---

## Componentes y Servicios

- **Agente Bayesiano (`agente_bay`)**  
  Microservicio FastAPI que recibe datos de clientes, predice el riesgo de churn usando un modelo Naive Bayes y envía los features relevantes al agente basado en conocimiento.

- **Agente Basado en Conocimiento (`agente_bec`)**  
  Microservicio FastAPI que aplica reglas de negocio (tabla de decisión en Excel) para determinar la mejor oferta y canal, y solicita el envío de notificaciones.

- **Servicio de Notificación (`notificacion`)**  
  API FastAPI que gestiona el envío de mensajes (WhatsApp/SMS) usando Twilio y registra las transacciones en SQLITE.

- **Base de Datos (`SQLITE`)**  
  Almacena logs y transacciones de notificación en la carpeta notificacion/api_mensajes/database.db

- **Grafana**  
  Visualización de métricas y logs de la base de datos.

---

## Instalación y Uso

### 1. Requisitos previos

- Python 3.8+ para los microservicios
- Python y pip instalados.
- Tener instalado los requirements.txt `pip install -r requirements.txt`

### 2. Configuración de notificación a WhatsApp (opcional)

Para recibir notificaciones a su numero de WhatsApp, siga estos pasos:

1.  **Modifique el archivo `simulador/clientes.xlsx`:**  Abra el archivo con Excel o un programa similar y cambie el valor de la columna `MSISDN` con su número de celular en formato `51XXXXXXXXX`.
2.  **Envíe un mensaje a Twilio:**  Envíe el mensaje "join bee-require" al número `+14155238886` a través de WhatsApp.  Este paso es necesario para habilitar el envío de mensajes a su número.

### 3. Arranque del simulador

Desde la raíz del proyecto, ejecute el archivo `main.bat`:

```batch
main.bat
```

Este archivo batch iniciará los servicios de PostgreSQL y Grafana con Docker Compose, y luego iniciará los microservicios y el simulador de predicciones de churn. El archivo `main.bat` contiene los siguientes pasos:

1.  Crea la tabla de notificaciones e enicia el API de notificaciones de WhatsApp.
2.  Espera 10 segundos.
3.  Inicia el microservicio BRMS simplificado.
4.  Espera 10 segundos.
5.  Inicia el microservicio de Churn Risk Prediction.
6.  Espera 20 segundos.
7.  Inicia el simulador de predicciones de churn.

---

## Endpoints principales y ejemplos de uso

### 1. Predicción de churn

**POST** `/predecir_churn/`  
_Ejemplo de payload:_

```json
{
  "distrito": 1,
  "msisdn": 51999999999,
  "tipo_plan": 2,
  "plan_asignado": 3,
  "cargo_plan": 49.9,
  "minutos_mensuales": 200,
  "gb_mensuales": 10,
  "reclamos_mensual": 0,
  "llamadas_soporte": 1,
  "flag_disminucion_consumo": 0,
  "monto_recarga_mensual": 0,
  "facturas_atrasadas": 0,
  "facturacion_mensual": 49.9,
  "flag_oferta_recibida": 0,
  "flag_oferta_aceptada": 0,
  "segmento": "PREMIUM",
  "ticket_30_dias": 0,
  "arpu_actual": 49.9,
  "descarga_ult_30min": 100
}
```

### 2. Evaluación de reglas de negocio

**POST** `/decision`  
_Payload generado automáticamente por el agente bayesiano._

### 3. Envío de notificación

**POST** `/send_message`  
_Ejemplo de payload:_

```json
{
  "offerId": "RET_PREMIUM_20",
  "msisdn": "51999999999",
  "channel": "whatsapp",
  "discountPct": "10",
  "validezHoras": "24"
}
```

_Respuesta esperada:_

```json
{
  "status": "exito",
  "transaction_id": 14,
  "whatsapp_status": "SMf65d711c9e31a1e581185548dc1c8760"
}
```

---


---

## Estructura de la base de datos

La tabla principal es `message_transactions`:

- id (SERIAL, PK)
- phone_number (VARCHAR)
- message_type (VARCHAR)
- message_content (TEXT)
- status (VARCHAR)
- transaction_id (VARCHAR)
- created_at (TIMESTAMP)
- error_message (TEXT)

---

## Notas adicionales

- El entrenamiento del modelo bayesiano se realiza en `agente_bay/training/entrenar_agente_bayesiano_churn.py` usando datos históricos.
- Las reglas de negocio se definen en archivos Excel dentro de `agente_bec/decisionTable/`.
