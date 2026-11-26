"""Transformaciones académicas puras: no alteran las colecciones recibidas."""
from functools import reduce
from collections import defaultdict

def promedio(notas):
    valores = tuple(map(float, notas))
    return reduce(lambda suma, n: suma + n, valores, 0.0) / len(valores) if valores else 0.0

def promedios_por_estudiante(registros):
    grupos = defaultdict(list)
    for item in registros: grupos[item["estudiante_id"]].append(item["nota"])
    return {ident: promedio(notas) for ident, notas in grupos.items()}

def filtrar_desaprobados(resultados, minima=11):
     return list(filter(lambda x: x.get("promedio", x.get("nota", 0)) < minima, resultados))


def filtrar_inasistencia_elevada(resultados, umbral=20): 
    return list(filter(lambda x: x.get("inasistencia", 0) > umbral, resultados))

def porcentaje_asistencia(estados):
    considerados = [e for e in estados if e in ("PRESENTE", "AUSENTE", "TARDANZA")]
    return 100 * sum(1 for e in considerados if e in ("PRESENTE", "TARDANZA")) / len(considerados) if considerados else 0.0

def porcentaje_inasistencia(estados):
    considerados = [e for e in estados if e in ("PRESENTE", "AUSENTE", "TARDANZA")]
    return 100 * sum(1 for e in considerados if e == "AUSENTE") / len(considerados) if considerados else 0.0

def agrupar_por_nivel(resultados):
    salida = defaultdict(list)
    for estudiante in resultados: salida[estudiante.get("nivel", "SIN ALERTAS")].append(estudiante)
    return dict(salida)

def estadisticas_curso(cursos):
    return [{**c, "promedio": promedio(c.get("notas", [])), "asistencia": porcentaje_asistencia(c.get("asistencias", []))} for c in cursos]
