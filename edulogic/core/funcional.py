from functools import reduce
from typing import List, Dict
from models.entidades import Estudiante


# Funciones puras sin efectos secundarios
calcular_promedio = lambda notas: round(
    reduce(lambda acc, x: acc + x, notas, 0.0) / len(notas), 2
) if notas else 0.0

calcular_porcentaje_inasistencia = lambda total, faltas: round(
    (faltas / total) * 100, 1
) if total > 0 else 0.0


def transformar_estudiantes(estudiantes: List[Estudiante]) -> List[Dict]:
    """Usa map() para transformar objetos Estudiante en diccionarios de indicadores."""
    return list(map(lambda est: {
        "codigo": est.codigo,
        "nombre": est.nombre_completo,
        "correo": est.correo,
        "promedio": calcular_promedio([c.nota for c in est.calificaciones]),
        "porcentaje_inasistencia": calcular_porcentaje_inasistencia(
            est.total_sesiones, est.inasistencias
        ),
        "porcentaje_asistencia": round(
            100.0 - calcular_porcentaje_inasistencia(est.total_sesiones, est.inasistencias), 1
        )
    }, estudiantes))


def filtrar_desaprobados(indicadores: List[Dict], nota_minima: float = 11.0) -> List[Dict]:
    """Usa filter() para obtener estudiantes con promedio menor a la nota aprobatoria."""
    return list(filter(lambda item: item["promedio"] < nota_minima, indicadores))


def filtrar_inasistencias_criticas(indicadores: List[Dict], umbral: float = 20.0) -> List[Dict]:
    """Usa filter() para obtener estudiantes que superan el 20% de inasistencia."""
    return list(filter(lambda item: item["porcentaje_inasistencia"] > umbral, indicadores))


def calcular_promedio_general(indicadores: List[Dict]) -> float:
    """Usa reduce() y map() para calcular el promedio global de toda la cohorte."""
    if not indicadores:
        return 0.0
    suma_total = reduce(lambda acc, val: acc + val, map(lambda x: x["promedio"], indicadores), 0.0)
    return round(suma_total / len(indicadores), 2)