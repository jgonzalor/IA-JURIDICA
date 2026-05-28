from datetime import date
from typing import Dict, List


def _value(data: Dict[str, str], key: str, default: str = "________________") -> str:
    val = (data.get(key) or "").strip()
    return val if val else default


def denuncia_template(data: Dict[str, str], temas: List[Dict]) -> str:
    hechos = _value(data, "hechos")
    victima = _value(data, "victima")
    probable = _value(data, "probable")
    lugar = _value(data, "lugar")
    fecha_hecho = _value(data, "fecha_hecho")
    return f"""# Borrador de denuncia / noticia criminal

**Fecha de elaboración:** {date.today().isoformat()}  
**Víctima u ofendido:** {victima}  
**Persona señalada o probable interviniente:** {probable}  
**Lugar:** {lugar}  
**Fecha/hora aproximada del hecho:** {fecha_hecho}

## I. Hechos
{hechos}

## II. Clasificación jurídica preliminar
Con base en la narración inicial, los hechos podrían relacionarse preliminarmente con los temas siguientes, sujetos a verificación por la autoridad competente:

{_temas_markdown(temas)}

## III. Datos de prueba iniciales sugeridos
- Identificación plena de la víctima u ofendido.
- Narrativa cronológica de modo, tiempo y lugar.
- Documentos, fotografías, videos, mensajes, audios, comprobantes o testigos disponibles.
- En caso de evidencia digital: archivo original, fuente de obtención, hash y cadena de custodia.
- En caso de telefonía/CDR: número, operador, periodo, zona horaria y fundamento de solicitud.

## IV. Petición
Se solicita recibir la presente narración de hechos, abrir o integrar la carpeta de investigación correspondiente y ordenar los actos de investigación necesarios para esclarecer los hechos, preservar evidencia y proteger los derechos de la víctima u ofendido.

**Nota:** Este borrador debe ser revisado y adecuado por profesional jurídico antes de presentarse.
"""


def acto_investigacion_template(data: Dict[str, str], temas: List[Dict]) -> str:
    hechos = _value(data, "hechos")
    acto = _value(data, "acto")
    fundamento = _temas_markdown(temas)
    return f"""# Borrador de solicitud de acto de investigación

**Fecha:** {date.today().isoformat()}  
**Carpeta de investigación:** {_value(data, "carpeta")}  
**Acto solicitado:** {acto}

## I. Antecedentes relevantes
{hechos}

## II. Pertinencia, idoneidad y necesidad
El acto solicitado se considera pertinente porque guarda relación directa con los hechos investigados; idóneo porque puede aportar información útil para esclarecerlos; y necesario porque permite confirmar, descartar o fortalecer líneas de investigación.

## III. Fundamento orientativo
{fundamento}

## IV. Petición concreta
Se solicita se ordene y documente el acto de investigación indicado, preservando la cadena de custodia, el registro de intervinientes, fechas, horas, lugares y condiciones de obtención de los indicios o datos resultantes.

## V. Observaciones de control judicial
Cuando el acto implique afectación a derechos constitucionales, comunicaciones privadas, cateo, extracción forense invasiva, geolocalización o datos sensibles, deberá valorarse la necesidad de autorización previa del Juez de control y demás legislación aplicable.
"""


def preservacion_digital_template(data: Dict[str, str], temas: List[Dict]) -> str:
    return f"""# Borrador de oficio de preservación de evidencia digital

**Fecha:** {date.today().isoformat()}  
**Carpeta de investigación:** {_value(data, "carpeta")}  
**Destinatario / proveedor / institución:** {_value(data, "destinatario")}  
**Cuenta, número, usuario, URL, ID o dato a preservar:** {_value(data, "identificador")}

## I. Antecedentes
{_value(data, "hechos")}

## II. Solicitud de preservación
Se solicita preservar de manera inmediata los registros, metadatos, archivos, logs, direcciones IP, identificadores, números, cuentas, fechas, horas, zonas horarias, datos de acceso, movimientos o información técnica asociada al identificador señalado, evitando su eliminación, alteración o pérdida.

## III. Periodo solicitado
Desde: {_value(data, "periodo_inicio")}  
Hasta: {_value(data, "periodo_fin")}

## IV. Alcance
La presente solicitud tiene como finalidad conservar la información para su posterior requerimiento formal por la autoridad competente, conforme a la normatividad aplicable.

## V. Consideraciones de integridad
- Conservar registros originales y bitácoras técnicas.
- Informar zona horaria usada en los timestamps.
- Mantener trazabilidad de extracción, resguardo y entrega.
- Cuando se entreguen archivos, proporcionar hash o medio de verificación de integridad.

**Nota:** La entrega de contenido o datos protegidos puede requerir autorización judicial o formalidad específica según el tipo de información solicitada.
"""


def cadena_custodia_template(data: Dict[str, str], temas: List[Dict]) -> str:
    return f"""# Borrador de registro de cadena de custodia digital

**Fecha:** {date.today().isoformat()}  
**Carpeta / expediente:** {_value(data, "carpeta")}  
**Indicio:** {_value(data, "indicio")}  
**Descripción:** {_value(data, "descripcion_indicio")}

## I. Localización, descubrimiento, aportación o recepción
- Fecha y hora: {_value(data, "fecha_recepcion")}
- Lugar: {_value(data, "lugar")}
- Persona que entrega/localiza: {_value(data, "entrega")}
- Persona que recibe: {_value(data, "recibe")}

## II. Identificación del indicio
- Tipo: {_value(data, "tipo_indicio")}
- Marca/modelo/serie si aplica: {_value(data, "serie")}
- Estado físico/lógico observado: {_value(data, "estado")}
- Embalaje o medio de resguardo: {_value(data, "embalaje")}

## III. Preservación e integridad
- Herramienta o método: {_value(data, "herramienta")}
- Hash MD5: {_value(data, "md5")}
- Hash SHA-1/SHA-256: {_value(data, "sha")}
- Ruta/nombre de imagen o respaldo: {_value(data, "ruta")}

## IV. Transferencias de custodia
| Fecha/hora | Entrega | Recibe | Motivo | Observaciones |
|---|---|---|---|---|
| {_value(data, "fecha_recepcion")} | {_value(data, "entrega")} | {_value(data, "recibe")} | Recepción/análisis | {_value(data, "observaciones")} |

## V. Fundamento orientativo
{_temas_markdown(temas)}

## VI. Advertencia técnica
Toda intervención sobre el indicio debe quedar documentada, evitando alteración innecesaria. Para evidencia digital se recomienda trabajar sobre copia forense o duplicado verificado, manteniendo original bajo resguardo.
"""


def teoria_caso_template(data: Dict[str, str], temas: List[Dict]) -> str:
    return f"""# Matriz preliminar de teoría del caso

**Fecha:** {date.today().isoformat()}  
**Carpeta / asunto:** {_value(data, "carpeta")}

## I. Hipótesis fáctica
{_value(data, "hechos")}

## II. Hipótesis jurídica preliminar
{_temas_markdown(temas)}

## III. Hipótesis probatoria
| Hecho a acreditar | Dato/medio de prueba | Fuente | Riesgo procesal |
|---|---|---|---|
| Conducta principal | {_value(data, "dato_1")} | {_value(data, "fuente_1")} | Verificar licitud y pertinencia |
| Identidad/intervención | {_value(data, "dato_2")} | {_value(data, "fuente_2")} | Corroborar con datos independientes |
| Resultado/perjuicio | {_value(data, "dato_3")} | {_value(data, "fuente_3")} | Cuantificar y documentar |

## IV. Debilidades a revisar
- Falta de tiempo, lugar o modo precisos.
- Datos de prueba no preservados o sin cadena de custodia.
- Evidencia digital sin original, hash o fuente clara.
- Actos que pudieran requerir control judicial.
- Necesidad de diferenciar tipo penal similar.

## V. Próximos actos sugeridos
- Entrevistas clave.
- Aseguramiento o preservación de evidencia.
- Pericial correspondiente.
- Oficios a instituciones/proveedores.
- Análisis de vínculos y corroboración independiente.
"""


def _temas_markdown(temas: List[Dict]) -> str:
    if not temas:
        return "- Sin temas detectados automáticamente. Verificar manualmente legislación aplicable."
    lines = []
    for t in temas[:6]:
        label = t.get("tema") or t.get("delito") or "Tema relacionado"
        law = t.get("ley") or t.get("ley_referencia") or "Referencia"
        art = t.get("articulo") or t.get("articulos") or "Verificar"
        summary = t.get("resumen") or t.get("tipo_base") or ""
        lines.append(f"- **{label}** — {law}, art./ref. {art}. {summary}")
    return "\n".join(lines)


TEMPLATE_BUILDERS = {
    "Denuncia / noticia criminal": denuncia_template,
    "Solicitud de acto de investigación": acto_investigacion_template,
    "Oficio de preservación de evidencia digital": preservacion_digital_template,
    "Registro de cadena de custodia digital": cadena_custodia_template,
    "Matriz de teoría del caso": teoria_caso_template,
}
