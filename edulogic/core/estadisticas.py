import numpy as np
import pandas as pd
from typing import List, Dict
from models.entidades import AlertaAcademica, Curso


def generar_estadisticas_numpy_pandas(
    df_cal: pd.DataFrame,
    cursos: Dict[str, Curso],
    alertas: List[AlertaAcademica]
) -> Dict:
    """Realiza el análisis estadístico avanzado con NumPy y pandas."""
    notas_array = df_cal["nota"].to_numpy(dtype=float)

    metricas_globales = {
        "media_numpy": round(float(np.mean(notas_array)), 2),
        "mediana_numpy": round(float(np.median(notas_array)), 2),
        "desviacion_std": round(float(np.std(notas_array)), 2),
        "nota_maxima": round(float(np.max(notas_array)), 2),
        "nota_minima": round(float(np.min(notas_array)), 2),
    }

    # Agrupación por curso usando pandas
    resumen_cursos_df = df_cal.groupby("codigo_curso")["nota"].agg(
        promedio="mean",
        maxima="max",
        minima="min",
        total_evaluados="count"
    ).reset_index()

    estadisticas_cursos = []
    for _, row in resumen_cursos_df.iterrows():
        cod = row["codigo_curso"]
        nombre_curso = cursos[cod].nombre if cod in cursos else cod
        estadisticas_cursos.append({
            "codigo": cod,
            "nombre": nombre_curso,
            "promedio": round(float(row["promedio"]), 2),
            "maxima": round(float(row["maxima"]), 2),
            "minima": round(float(row["minima"]), 2)
        })

    # Conteo por nivel de riesgo usando pandas
    df_alertas = pd.DataFrame([vars(a) for a in alertas])
    conteo_riesgos = df_alertas["nivel_riesgo"].value_counts().to_dict()

    categorias_ordenadas = [
        "Prioridad de seguimiento",
        "Riesgo académico alto",
        "Rendimiento en observación",
        "Alerta de asistencia",
        "Sin riesgo"
    ]
    distribucion_riesgo = {
        cat: int(conteo_riesgos.get(cat, 0)) for cat in categorias_ordenadas
    }

    return {
        "metricas_globales": metricas_globales,
        "estadisticas_cursos": estadisticas_cursos,
        "distribucion_riesgo": distribucion_riesgo
    }