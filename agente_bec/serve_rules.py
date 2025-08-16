
"""
serve_rules.py — Microservicio BRMS simplificado (v2)

Cambios solicitados:
1. El endpoint /decision ahora requiere un campo extra *msisdn* (string).
2. Una vez encuentra la regla, hace POST a http://localhost:8000/send_message
   con el paquete {offerId, msisdn, channel, discountPct, validezHoras}.
3. Todos los eventos se registran en consola mediante logging.INFO.
"""

import os, re, logging, requests
import pandas as pd
from fastapi import FastAPI, HTTPException
import uvicorn
from dotenv import load_dotenv


load_dotenv()

RULES_PATH = os.getenv("RULES_PATH", "decisionTable/decision_table.xlsx")
MSG_API    = os.getenv("MSG_API", "https://ts1vmrfv-8000.brs.devtunnels.ms/send_message")

# ────── Logging ─────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("brms")

# ────── Cargar tabla Excel ──────────────────────────────────────────────
def load_rules(path):
    df = pd.read_excel(path, header=None, engine="openpyxl")
    hdr = df[df.iloc[:,0].astype(str).str.contains("CONDITION", na=False)].index[0]
    headers = df.iloc[hdr].tolist()
    rules = df.iloc[hdr+1:].reset_index(drop=True)
    rules.columns = headers
    rules = rules[rules["ACTION offerId"].notna()]
    log.info("Reglas cargadas: %d", len(rules))
    return rules

RULES = load_rules(RULES_PATH)
COND_COLS = [c for c in RULES.columns if c.startswith("CONDITION")]
ACT_COLS  = [c for c in RULES.columns if c.startswith("ACTION")]

_cmp = re.compile(r'^(>=|<=|>|<)?\s*([0-9]+(?:\.[0-9]+)?)$')
_rng = re.compile(r'^([0-9]+(?:\.[0-9]+)?)\.\.([0-9]+(?:\.[0-9]+)?)$')

def match_val(v, cond):
    if pd.isna(cond) or cond in ("*", ""):
        return True
    cond = str(cond).strip()
    # numeric?
    is_num = False
    try:
        float(v)
        is_num = True
    except Exception:
        pass
    if is_num:
        m = _rng.match(cond)
        if m:
            return float(m.group(1)) <= float(v) <= float(m.group(2))
        m = _cmp.match(cond)
        if m:
            op, num = m.group(1) or "==", float(m.group(2))
            v = float(v)
            return {"==": v == num, ">=": v >= num, "<=": v <= num, ">": v > num, "<": v < num}[op]
    return str(v) == cond

def evaluate(payload):
    for _, rule in RULES.iterrows():
        if all(match_val(payload.get(c.split()[1]), rule[c]) for c in COND_COLS):
            return {a.split()[1]: rule[a] for a in ACT_COLS}
    return None

# ────── FastAPI ─────────────────────────────────────────────────────────
app = FastAPI(title="Mini BRMS con envío de mensaje")

@app.post("/decision")
def decision(req: dict):
    required = ["segment", "riskChurn", "tickets30d", "arpuActual", "bytesDown30m", "msisdn"]
    miss = [k for k in required if k not in req]
    if miss:
        raise HTTPException(400, f"Faltan campos: {miss}")
    log.info("Nueva petición: %s", req)

    result = evaluate(req)
    if not result:
        log.info("Sin regla aplicable.")
        raise HTTPException(404, "No se encontró regla coincidente")

    # Añadir msisdn al payload de salida y enviar mensaje
    send_payload = {
        "offerId":     result["offerId"],
        "msisdn":      str(req["msisdn"]),
        "channel":     "whatsapp",
        "discountPct": str(result["discountPct"]),
        "validezHoras": str(result["validezHoras"])
    }
    try:
        log.info(send_payload)
        resp = requests.post(MSG_API, json=send_payload, timeout=5)
        log.info("Mensaje enviado ➜ %s | status=%s", MSG_API, resp.status_code)
    except Exception as e:
        log.error("Error enviando mensaje: %s", e)

    # Devuelve acciones + estado de envío
    result_out = result.copy()
    result_out.update({"msisdn": req["msisdn"]})
    return result_out

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
