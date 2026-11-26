from app.paradigmas.funcional import promedio, porcentaje_asistencia, porcentaje_inasistencia, filtrar_desaprobados

def test_promedio_and_empty():
    assert promedio([10, 20, 15]) == 15
    assert promedio([]) == 0

def test_attendance_excludes_justified_and_counts_late_present():
    estados=['PRESENTE','AUSENTE','TARDANZA','JUSTIFICADO']
    assert porcentaje_asistencia(estados) == 66.66666666666667
    assert porcentaje_inasistencia(estados) == 33.333333333333336

def test_filter_does_not_change_input():
    datos=[{'promedio':9},{'promedio':13}]
    assert len(filtrar_desaprobados(datos)) == 1
    assert len(datos)==2
