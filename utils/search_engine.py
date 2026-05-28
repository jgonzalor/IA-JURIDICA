import re
import unicodedata
from typing import Dict, Iterable, List, Tuple


def normalize(text: str) -> str:
    text = text or ""
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.lower()


def tokenize(text: str) -> List[str]:
    text = normalize(text)
    return [t for t in re.findall(r"[a-z0-9ñ]+", text) if len(t) > 2]


def score_text(query: str, haystack: str) -> float:
    q_tokens = tokenize(query)
    h = normalize(haystack)
    if not q_tokens:
        return 0.0
    score = 0.0
    for token in q_tokens:
        if token in h:
            score += 1.0
        if re.search(rf"\b{re.escape(token)}\b", h):
            score += 0.5
    unique = len(set(q_tokens)) or 1
    return score / unique


def search_records(query: str, records: Iterable[Dict], fields: Tuple[str, ...], limit: int = 8) -> List[Dict]:
    ranked = []
    for rec in records:
        haystack = " ".join(str(rec.get(field, "")) for field in fields)
        s = score_text(query, haystack)
        if s > 0:
            rec2 = dict(rec)
            rec2["_score"] = round(s, 3)
            ranked.append(rec2)
    ranked.sort(key=lambda x: x["_score"], reverse=True)
    return ranked[:limit]


def detect_suggestions(text: str, rules: Iterable[Dict]) -> List[str]:
    ntext = normalize(text)
    results = []
    seen = set()
    for rule in rules:
        terms = [normalize(t) for t in rule.get("terms", [])]
        if any(term in ntext for term in terms):
            for suggestion in rule.get("suggestions", []):
                if suggestion not in seen:
                    results.append(suggestion)
                    seen.add(suggestion)
    return results


def build_missing_data_checklist(text: str) -> List[str]:
    ntext = normalize(text)
    base = [
        "Fecha y hora aproximada del hecho.",
        "Lugar del hecho o medio utilizado.",
        "Identificación de víctima/ofendido.",
        "Conducta concreta atribuida y forma de participación.",
        "Datos de prueba disponibles y su origen.",
        "Relación causal entre conducta, resultado y perjuicio.",
    ]
    if any(term in ntext for term in ["telefono", "llamada", "mensaje", "whatsapp", "cdr", "imei", "imsi"]):
        base.extend([
            "Número telefónico, IMEI/IMSI, operador, fechas y zona horaria.",
            "Origen lícito de capturas, audios, CDR o datos conservados.",
            "Necesidad de oficio de preservación o autorización judicial, según alcance.",
        ])
    if any(term in ntext for term in ["video", "foto", "usb", "archivo", "metadato", "exif"]):
        base.extend([
            "Archivo original, nombre, ruta, hash y herramienta de extracción/análisis.",
            "Cadena de custodia desde recepción hasta análisis.",
            "Diferencia entre fecha del sistema de archivos y metadatos internos.",
        ])
    if any(term in ntext for term in ["transferencia", "deposito", "banco", "cuenta"]):
        base.extend([
            "Comprobantes de pago, cuenta origen/destino, beneficiario y banco.",
            "Relación entre el pago y el engaño, amenaza o conducta investigada.",
        ])
    return base
