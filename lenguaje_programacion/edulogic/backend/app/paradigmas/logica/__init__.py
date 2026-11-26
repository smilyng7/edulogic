"""Motor PyDatalog: hechos numéricos y reglas declarativas de clasificación."""
from threading import RLock
from pyDatalog import pyDatalog

_lock = RLock()

def inferir(registros, nota_minima=11, nota_observacion=13, inasistencia_maxima=20):
    """Carga un conjunto aislado de hechos, consulta las reglas y devuelve conclusiones."""
    with _lock:
        pyDatalog.clear()
        pyDatalog.create_terms("rendimiento, asistencia, bajo_rendimiento, observacion, alerta_asistencia, riesgo_alto, prioritario, sin_alertas, X, P, I")
        # Umbrales interpolados como números configurables, no lógica imperativa.
        pyDatalog.load(f"""
            bajo_rendimiento(X) <= rendimiento(X, P) & (P < {float(nota_minima)})
            observacion(X) <= rendimiento(X, P) & ({float(nota_minima)} <= P) & (P <= {float(nota_observacion)})
            alerta_asistencia(X) <= asistencia(X, I) & (I > {float(inasistencia_maxima)})
            riesgo_alto(X) <= bajo_rendimiento(X) & alerta_asistencia(X)
            prioritario(X) <= riesgo_alto(X)
            sin_alertas(X) <= rendimiento(X, P) & asistencia(X, I) & (P >= {float(nota_minima)}) & (I <= {float(inasistencia_maxima)})
        """)
        for item in registros:
            pyDatalog.assert_fact("rendimiento", str(item["id"]), float(item.get("promedio", 0)))
            pyDatalog.assert_fact("asistencia", str(item["id"]), float(item.get("inasistencia", 0)))
        conclusion = {}
        queries = {"BAJO RENDIMIENTO": "bajo_rendimiento(X)", "EN OBSERVACIÓN": "observacion(X)",
                   "ALERTA DE ASISTENCIA": "alerta_asistencia(X)", "RIESGO ALTO": "riesgo_alto(X)",
                   "SEGUIMIENTO PRIORITARIO": "prioritario(X)", "SIN ALERTAS": "sin_alertas(X)"}
        for nivel, consulta in queries.items():
            respuesta = pyDatalog.ask(consulta)
            for fila in (respuesta.answers if respuesta else []):
                ident = fila[0]
                conclusion.setdefault(ident, []).append(nivel)
        return conclusion
