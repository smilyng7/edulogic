def seed_docente(client):
    return client.post('/api/docentes',json={'codigo':'D1','nombre':'Ada','apellido':'Lovelace','correo':'ada@example.edu'})

def test_create_and_validate_student(client):
    r=client.post('/api/estudiantes',json={'codigo':'E1','nombre':'Ana','apellido':'Rojas','correo':'ana@example.edu'})
    assert r.status_code==201
    assert client.post('/api/estudiantes',json={'codigo':'E2','nombre':'A','apellido':'B','correo':'bad'}).status_code==400

def test_course_grade_and_attendance(client):
    seed_docente(client)
    student=client.post('/api/estudiantes',json={'codigo':'E1','nombre':'Ana','apellido':'Rojas','correo':'ana@example.edu'}).json['datos']
    course=client.post('/api/cursos',json={'codigo':'C1','nombre':'Lógica','docente_id':1}).json['datos']
    assert client.post('/api/calificaciones',json={'estudiante_id':student['id'],'curso_id':course['id'],'nota':21}).status_code==400
    assert client.post('/api/calificaciones',json={'estudiante_id':student['id'],'curso_id':course['id'],'nota':18}).status_code==201
    payload={'estudiante_id':student['id'],'curso_id':course['id'],'fecha':'2026-10-01','estado':'PRESENTE'}
    assert client.post('/api/asistencias',json=payload).status_code==201
    assert client.post('/api/asistencias',json=payload).status_code==409

def test_missing_resource_and_dashboard(client):
    assert client.get('/api/estudiantes/999').status_code==404
    assert client.get('/api/dashboard').status_code==200
