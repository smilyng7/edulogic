import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from core.cargador_datos import CargadorDatos
from core.funcional import (
    transformar_estudiantes,
    filtrar_desaprobados,
    filtrar_inasistencias_criticas,
    calcular_promedio_general
)
from core.logico import MotorLogicoEduLogic
from core.estadisticas import generar_estadisticas_numpy_pandas

app = Flask(__name__)
app.secret_key = "edulogic_utp_2026"
DATA_FOLDER = "data"
DB_PATH = "edulogic.db"


def guardar_en_sqlite(alertas):
    """Persiste los resultados inferidos en una base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas_academicas (
            codigo TEXT PRIMARY KEY,
            nombre TEXT,
            promedio REAL,
            porcentaje_inasistencia REAL,
            nivel_riesgo TEXT,
            motivo TEXT
        )
    """)
    cursor.execute("DELETE FROM alertas_academicas")
    for a in alertas:
        cursor.execute("""
            INSERT INTO alertas_academicas VALUES (?, ?, ?, ?, ?, ?)
        """, (a.codigo_estudiante, a.nombre_estudiante, a.promedio,
              a.porcentaje_inasistencia, a.nivel_riesgo, a.motivo))
    conn.commit()
    conn.close()


@app.route("/", methods=["GET"])
def dashboard():
    # 1. POO + Lectura CSV
    cargador = CargadorDatos(DATA_FOLDER)
    estudiantes, cursos, df_cal, _ = cargador.cargar_sistema()

    # 2. Paradigma Funcional
    indicadores = transformar_estudiantes(estudiantes)
    desaprobados = filtrar_desaprobados(indicadores)
    inasistentes = filtrar_inasistencias_criticas(indicadores)
    promedio_cohorte = calcular_promedio_general(indicadores)

    # 3. Paradigma Lógico
    motor = MotorLogicoEduLogic()
    motor.cargar_hechos(indicadores)
    alertas = motor.inferir_alertas()
    guardar_en_sqlite(alertas)

    # 4. Análisis NumPy y pandas
    analisis = generar_estadisticas_numpy_pandas(df_cal, cursos, alertas)

    kpis = {
        "total_estudiantes": len(estudiantes),
        "promedio_cohorte": promedio_cohorte,
        "total_desaprobados": len(desaprobados),
        "total_inasistentes": len(inasistentes),
        "en_riesgo_critico": sum(
            1 for a in alertas if a.nivel_riesgo in ["Prioridad de seguimiento", "Riesgo académico alto"]
        )
    }

    return render_template(
        "dashboard.html",
        kpis=kpis,
        alertas=alertas,
        analisis=analisis
    )


@app.route("/subir-csv", methods=["POST"])
def subir_csv():
    """Permite cargar nuevos archivos CSV desde la interfaz web."""
    archivos_esperados = ["estudiantes", "calificaciones", "asistencias"]
    actualizados = 0
    for nombre in archivos_esperados:
        archivo = request.files.get(nombre)
        if archivo and archivo.filename.endswith(".csv"):
            archivo.save(os.path.join(DATA_FOLDER, f"{nombre}.csv"))
            actualizados += 1

    if actualizados > 0:
        flash(f"Se actualizaron {actualizados} archivo(s) CSV correctamente.", "success")
    else:
        flash("No se seleccionó ningún archivo CSV válido.", "warning")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)