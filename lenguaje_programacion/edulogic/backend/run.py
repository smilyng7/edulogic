"""Comandos de desarrollo: python run.py [serve|init-db|seed]."""
import sys
from app import create_app
from app.extensions import db

app=create_app()

def cargar_demo():
    from app.models import Estudiante,Docente,Curso,Calificacion,Asistencia
    if Estudiante.query.first(): print("La base ya contiene datos; se omite la demostración."); return
    d=Docente(codigo="DOC001",nombre="María",apellido="Quispe",correo="mquispe@edulogic.edu")
    db.session.add(d); db.session.flush()
    cursos=[Curso(codigo=f"CUR00{i}",nombre=n,descripcion="Curso de demostración",docente_id=d.id) for i,n in enumerate(("Programación","Matemática","Comunicación"),1)]
    db.session.add_all(cursos); db.session.flush()
    perfiles=[("Ana","Rojas",18,5),("Luis","Pérez",12,10),("Camila","Díaz",9,5),("Diego","Luna",9,25),("Sofía","Vega",15,25),("Mateo","Ruiz",10,28),("Lucía","Mora",16,0),("Pablo","León",13,15),("Elena","Cruz",8,30),("Jorge","Soto",17,8)]
    for i,(nombre,apellido,nota,falta) in enumerate(perfiles,1):
        e=Estudiante(codigo=f"EST{i:03}",nombre=nombre,apellido=apellido,correo=f"est{i}@edulogic.edu"); db.session.add(e); db.session.flush()
        for j,c in enumerate(cursos): db.session.add(Calificacion(estudiante_id=e.id,curso_id=c.id,nota=max(0,min(20,nota+(j-1))),observacion="Evaluación de demostración"))
        for dia in range(1,21):
            estado="AUSENTE" if dia <= round(falta/5) else "PRESENTE"
            if dia==20 and i%3==0: estado="JUSTIFICADO"
            elif dia==19 and i%4==0: estado="TARDANZA"
            db.session.add(Asistencia(estudiante_id=e.id,curso_id=cursos[0].id,fecha=__import__("datetime").date(2026,10,dia),estado=estado))
    db.session.commit(); print("Datos de demostración cargados.")

if __name__=="__main__":
    with app.app_context():
        db.create_all()
        if len(sys.argv)>1 and sys.argv[1]=="seed": cargar_demo()
        elif len(sys.argv)>1 and sys.argv[1]=="init-db": print("Base de datos inicializada.")
        else: app.run(debug=True,port=5000)
