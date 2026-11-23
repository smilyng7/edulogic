from typing import List, Dict
from models.entidades import AlertaAcademica


class MotorLogicoEduLogic:
    """
    Motor de inferencia basado en hechos y reglas lógicas definidas en EduLogic:
    - Regla 1: promedio < 11 Y inasistencia > 20% -> Prioridad de seguimiento
    - Regla 2: promedio < 11 -> Riesgo académico alto
    - Regla 3: 11 <= promedio <= 13 -> Rendimiento en observación
    - Regla 4: inasistencia > 20% -> Alerta de asistencia
    - Regla 5: Caso contrario -> Sin riesgo (Regular)
    """
    def __init__(self):
        self.base_hechos = []

    def cargar_hechos(self, indicadores: List[Dict]):
        """Registra los indicadores académicos como hechos lógicos."""
        self.base_hechos = [
            ("rendimiento", item["codigo"], item["nombre"], item["promedio"], item["porcentaje_inasistencia"])
            for item in indicadores
        ]

    @staticmethod
    def _regla_prioridad_seguimiento(prom: float, inasist: float) -> bool:
        return prom < 11.0 and inasist > 20.0

    @staticmethod
    def _regla_riesgo_alto(prom: float) -> bool:
        return prom < 11.0

    @staticmethod
    def _regla_observacion(prom: float) -> bool:
        return 11.0 <= prom <= 13.0

    @staticmethod
    def _regla_alerta_asistencia(inasist: float) -> bool:
        return inasist > 20.0

    def inferir_alertas(self) -> List[AlertaAcademica]:
        """Evalúa las reglas sobre la base de hechos y deduce la clasificación."""
        alertas = []
        for predicado, codigo, nombre, prom, inasist in self.base_hechos:
            if predicado != "rendimiento":
                continue

            if self._regla_prioridad_seguimiento(prom, inasist):
                nivel = "Prioridad de seguimiento"
                motivo = f"Promedio desaprobatorio ({prom}) e inasistencias críticas ({inasist}%)."
                badge = "danger"
            elif self._regla_riesgo_alto(prom):
                nivel = "Riesgo académico alto"
                motivo = f"Promedio menor a 11 ({prom}). Requiere refuerzo académico."
                badge = "warning"
            elif self._regla_observacion(prom):
                nivel = "Rendimiento en observación"
                motivo = f"Promedio en rango límite ({prom} entre 11 y 13)."
                badge = "info"
            elif self._regla_alerta_asistencia(inasist):
                nivel = "Alerta de asistencia"
                motivo = f"Inasistencias superiores al 20% ({inasist}%), aunque aprueba en notas."
                badge = "secondary"
            else:
                nivel = "Sin riesgo"
                motivo = "Desempeño académico y asistencia dentro de los parámetros esperados."
                badge = "success"

            alertas.append(AlertaAcademica(
                codigo_estudiante=codigo,
                nombre_estudiante=nombre,
                promedio=prom,
                porcentaje_inasistencia=inasist,
                nivel_riesgo=nivel,
                motivo=motivo,
                color_badge=badge
            ))
        return alertas