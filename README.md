# Lumen Sports AI

## Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en Streamlit Community Cloud
1. Crea un repositorio en GitHub.
2. Sube `app.py` y `requirements.txt`.
3. En Streamlit Community Cloud selecciona el repositorio.
4. Main file: `app.py`.
5. Pulsa Deploy.

## Importante
La versión inicial obtiene eventos de ESPN cuando están disponibles y calcula una estimación configurable. No es un modelo validado para apuestas. Para mejorar precisión se necesitan datos históricos, variables por deporte, calibración y evaluación retrospectiva.
