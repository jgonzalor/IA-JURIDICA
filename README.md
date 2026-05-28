# Sentinel Penal IA

MVP en Streamlit para consulta interna de derecho penal mexicano, CNPP, evidencia digital, cadena de custodia y generación de borradores.

## Módulos

- Inicio / dashboard
- Consulta inteligente por hechos
- CNPP por etapas
- Fichas penales
- Generador de borradores
- Fuentes oficiales y actualización

## Instalación local

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Subir a Streamlit Cloud

1. Crea un repositorio en GitHub.
2. Sube estos archivos.
3. En Streamlit Cloud selecciona el repositorio.
4. Main file path: `app.py`.
5. Deploy.

## Fuentes base usadas para este MVP

- CNPP, Cámara de Diputados: https://www.diputados.gob.mx/LeyesBiblio/pdf/CNPP.pdf
- Código Penal Federal, Cámara de Diputados: https://www.diputados.gob.mx/LeyesBiblio/pdf/CPF.pdf
- Semanario Judicial de la Federación: https://sjf2.scjn.gob.mx/busqueda-principal-tesis
- Ley General en materia de Extorsión, Cámara de Diputados: https://www.diputados.gob.mx/LeyesBiblio/ref/lgpisdme.htm

## Aviso

Esta herramienta es informativa y de apoyo. No sustituye asesoría jurídica, revisión profesional, consulta directa de fuentes oficiales, legislación estatal, leyes especiales ni criterios judiciales vigentes.

## Próximas mejoras sugeridas

- Cargar PDFs oficiales y crear búsqueda por texto completo.
- Base vectorial con Supabase/pgvector.
- Módulo de jurisprudencia.
- Exportar borradores a Word/PDF.
- Roles de usuario y bitácora de consultas.

## Animaciones agregadas

Esta versión incluye la carpeta `assets/` con tres recursos visuales:

- `sentinel_head_turn.gif`: animación de carga con la cabeza girando.
- `sentinel_click_sticker.png`: sticker emergente para acciones de análisis y generación.
- `sentinel_head_sheet.png`: hoja base de stickers por si se quiere generar otra animación.

La animación aparece al abrir la app y al navegar entre módulos. El sticker aparece al usar botones como `Analizar` y `Generar borrador`.

Para hacer que el sticker salga solo algunas veces, abre `app.py` y cambia:

```python
SHOW_ACTION_STICKER_EVERY_CLICK = True
```

por:

```python
SHOW_ACTION_STICKER_EVERY_CLICK = False
```
