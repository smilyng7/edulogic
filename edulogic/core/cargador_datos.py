import os
import pandas as pd
from models.entidades import Estudiante, Curso, Calificacion


class CargadorDatos:
    """Se encarga de leer, validar los CSV e instanciar los objetos POO."""
    def __init__(self, ruta_data: str = "data"):
        self.ruta_data = ruta_data

    def cargar_sistema(self):
        df_est = pd.read_csv(os.path.join(self.ruta_data, "estudiantes.csv"))
        df_cur = pd.read_csv(os.path.join(self.ruta_data, "cursos.csv"))
        df_cal = pd.read_csv(os.path.join(self.ruta_data, "calificaciones.csv"))
        df_asi = pd.read_csv(os.path.join(self.ruta_data, "asistencias.csv"))

        # Limpieza básica de datos nulos
        df_cal["nota"] = df_cal["nota"].fillna(0.0).clip(0, 20)

        cursos = {
            row["codigo"]: Curso(row["codigo"], row["nombre"], row["docente"])
            for _, row in df_cur.iterrows()
        }

        estudiantes_dict = {}
        for _, row in df_est.iterrows():
            est = Estudiante(row["codigo"], row["nombre"], row["apellido"], row["correo"])
            estudiantes_dict[est.codigo] = est

        for _, row in df_cal.iterrows():
            cod_est = row["codigo_estudiante"]
            if cod_est in estudiantes_dict:
                cal = Calificacion(cod_est, row["codigo_curso"], row["nota"], row["fecha"])
                estudiantes_dict[cod_est].agregar_calificacion(cal)

        for _, row in df_asi.iterrows():
            cod_est = row["codigo_estudiante"]
            if cod_est in estudiantes_dict:
                estudiantes_dict[cod_est].registrar_asistencia(
                    int(row["total_sesiones"]), int(row["inasistencias"])
                )

        return list(estudiantes_dict.values()), cursos, df_cal, df_asi