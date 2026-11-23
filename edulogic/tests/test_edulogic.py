from core.funcional import calcular_promedio, calcular_porcentaje_inasistencia
from core.logico import MotorLogicoEduLogic


def test_calculo_promedio_funcional():
    assert calcular_promedio([12.0, 14.0, 16.0]) == 14.0
    assert calcular_promedio([]) == 0.0


def test_reglas_logicas():
    motor = MotorLogicoEduLogic()
    motor.cargar_hechos([
        {"codigo": "U01", "nombre": "Test 1", "promedio": 9.5, "porcentaje_inasistencia": 25.0},
        {"codigo": "U02", "nombre": "Test 2", "promedio": 10.0, "porcentaje_inasistencia": 10.0},
        {"codigo": "U03", "nombre": "Test 3", "promedio": 12.0, "porcentaje_inasistencia": 5.0},
        {"codigo": "U04", "nombre": "Test 4", "promedio": 15.0, "porcentaje_inasistencia": 30.0},
        {"codigo": "U05", "nombre": "Test 5", "promedio": 17.0, "porcentaje_inasistencia": 0.0},
    ])
    alertas = motor.inferir_alertas()
    assert alertas[0].nivel_riesgo == "Prioridad de seguimiento"
    assert alertas[1].nivel_riesgo == "Riesgo académico alto"
    assert alertas[2].nivel_riesgo == "Rendimiento en observación"
    assert alertas[3].nivel_riesgo == "Alerta de asistencia"
    assert alertas[4].nivel_riesgo == "Sin riesgo"