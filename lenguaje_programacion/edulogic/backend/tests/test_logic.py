from app.paradigmas.logica import inferir

def test_five_risk_scenarios():
    rows=[{'id':i,'promedio':p,'inasistencia':a} for i,(p,a) in enumerate([(18,5),(12,10),(9,5),(9,25),(15,25)],1)]
    got=inferir(rows)
    assert got['1']==['SIN ALERTAS']
    assert 'EN OBSERVACIÓN' in got['2']
    assert 'BAJO RENDIMIENTO' in got['3'] and 'RIESGO ALTO' not in got['3']
    assert 'RIESGO ALTO' in got['4'] and 'SEGUIMIENTO PRIORITARIO' in got['4']
    assert 'ALERTA DE ASISTENCIA' in got['5']
