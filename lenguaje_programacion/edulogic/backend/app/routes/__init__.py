"""API REST y vistas de datos; validación de entrada centralizada."""
from datetime import date
from flask import Blueprint, jsonify, request, current_app, Response
from sqlalchemy import func
import pandas as pd
from ..extensions import db
from ..models import Estudiante, Docente, Curso, Calificacion, Asistencia, AlertaAcademica
from ..paradigmas.funcional import promedio, porcentaje_asistencia, porcentaje_inasistencia
from ..paradigmas.logica import inferir

api = Blueprint("api", __name__, url_prefix="/api")
MODELOS = {"estudiantes": Estudiante, "docentes": Docente, "cursos": Curso, "calificaciones": Calificacion, "asistencias": Asistencia, "alertas": AlertaAcademica}

def serializar(obj):
    if isinstance(obj, Estudiante): 
        return {"id":obj.id,"codigo":obj.codigo,"nombre":obj.nombre,"apellido":obj.apellido,"nombre_completo":obj.nombre_completo,"correo":obj.correo,"estado":obj.estado,"fecha_registro":obj.fecha_registro.isoformat()}
    if isinstance(obj, Docente): 
        return {"id":obj.id,"codigo":obj.codigo,"nombre":obj.nombre,"apellido":obj.apellido,"nombre_completo":obj.nombre_completo,"correo":obj.correo,"estado":obj.estado}
    if isinstance(obj, Curso): 
        return {"id":obj.id,"codigo":obj.codigo,"nombre":obj.nombre,"descripcion":obj.descripcion,"docente_id":obj.docente_id,"docente":obj.docente.nombre_completo if obj.docente else None,"estado":obj.estado}
    if isinstance(obj, Calificacion): 
        return {"id":obj.id,"estudiante_id":obj.estudiante_id,"curso_id":obj.curso_id,"nota":obj.nota,"fecha_registro":obj.fecha_registro.isoformat(),"observacion":obj.observacion,"estudiante":obj.estudiante.nombre_completo,"curso":obj.curso.nombre}
    if isinstance(obj, Asistencia): 
        return {"id":obj.id,"estudiante_id":obj.estudiante_id,"curso_id":obj.curso_id,"fecha":obj.fecha.isoformat(),"estado":obj.estado,"estudiante":obj.estudiante.nombre_completo,"curso":obj.curso.nombre}
    return {"id":obj.id,"estudiante_id":obj.estudiante_id,"nivel":obj.nivel,"motivo":obj.motivo,"fecha":obj.fecha.isoformat(),"estado":obj.estado,"estudiante":obj.estudiante.nombre_completo}

def error(mensaje, codigo=400):
    return jsonify(error={"code":"validation_error","message":mensaje}), codigo

def parse_date(value, default=None):
    if not value: return default or date.today()
    try: return date.fromisoformat(value)
    except (TypeError, ValueError): raise ValueError("La fecha debe usar el formato AAAA-MM-DD.")

@api.get("/<string:recurso>")
def listar(recurso):
    model = MODELOS.get(recurso)
    if not model: return error("Módulo desconocido.",404)
    query = model.query
    termino = request.args.get("q", "").strip()
    if termino and model in (Estudiante, Docente): query = query.filter(db.or_(model.nombre.ilike(f"%{termino}%"), model.apellido.ilike(f"%{termino}%"), model.codigo.ilike(f"%{termino}%")))
    pagina=max(1, request.args.get("pagina",1,type=int)); por_pagina=min(100,max(1,request.args.get("limite",100,type=int)))
    pag=query.order_by(model.id.desc()).paginate(page=pagina,per_page=por_pagina,error_out=False)
    return jsonify(datos=[serializar(x) for x in pag.items],pagina=pag.page,paginas=pag.pages,total=pag.total)

@api.post("/<string:recurso>")
def crear(recurso):
    model=MODELOS.get(recurso); data=request.get_json(silent=True) or {}
    if not model: return error("Módulo desconocido.",404)
    try:
        if model in (Estudiante,Docente):
            for campo in ("codigo","nombre","apellido","correo"):
                if not str(data.get(campo,"")).strip(): return error(f"El campo {campo} es obligatorio.")
            correo=data["correo"].strip()
            if "@" not in correo or "." not in correo.split("@")[-1]: return error("Correo electrónico inválido.")
            obj=model(codigo=data["codigo"].strip(),nombre=data["nombre"].strip(),apellido=data["apellido"].strip(),correo=correo)
        elif model is Curso:
            if not all(data.get(k) for k in ("codigo","nombre","docente_id")): return error("Código, nombre y docente son obligatorios.")
            obj=Curso(codigo=data["codigo"].strip(),nombre=data["nombre"].strip(),descripcion=data.get("descripcion",""),docente_id=int(data["docente_id"]))
        elif model is Calificacion:
            nota=float(data["nota"])
            if not 0 <= nota <= 20: return error("La nota debe estar entre 0 y 20.")
            obj=Calificacion(estudiante_id=int(data["estudiante_id"]),curso_id=int(data["curso_id"]),nota=nota,fecha_registro=parse_date(data.get("fecha_registro")),observacion=data.get("observacion",""))
        elif model is Asistencia:
            estado=str(data.get("estado","")).upper()
            if estado not in ("PRESENTE","AUSENTE","TARDANZA","JUSTIFICADO"): return error("Estado de asistencia inválido.")
            obj=Asistencia(estudiante_id=int(data["estudiante_id"]),curso_id=int(data["curso_id"]),fecha=parse_date(data.get("fecha")),estado=estado)
        elif model is AlertaAcademica:
            obj=AlertaAcademica(estudiante_id=int(data["estudiante_id"]),nivel=data["nivel"],motivo=data["motivo"],estado=data.get("estado","PENDIENTE"))
        db.session.add(obj); db.session.commit(); return jsonify(datos=serializar(obj)),201
    except (KeyError,TypeError,ValueError) as exc:
        db.session.rollback(); return error(str(exc) or "Faltan campos obligatorios.")

@api.route("/<string:recurso>/<int:ident>",methods=["GET","PUT","DELETE"])
def detalle(recurso,ident):
    model=MODELOS.get(recurso); obj=model.query.get(ident) if model else None
    if not model: 
        return error("Módulo desconocido.",404)
    if obj is None: 
        return error("Registro no encontrado.",404)
    if request.method=="GET": 
        return jsonify(datos=serializar(obj))
    if request.method=="DELETE":
        db.session.delete(obj); db.session.commit(); 
        return jsonify(mensaje="Registro eliminado.")
    data=request.get_json(silent=True) or {}
    try:
        for key in ("codigo","nombre","apellido","correo","descripcion","estado","observacion","nivel","motivo"):
            if key in data: setattr(obj,key,data[key])
        if isinstance(obj,Curso) and "docente_id" in data: obj.docente_id=int(data["docente_id"])
        if isinstance(obj,Calificacion):
            if "nota" in data and not 0 <= float(data["nota"]) <= 20: 
                return error("La nota debe estar entre 0 y 20.")
            if "nota" in data: obj.nota=float(data["nota"])
            if "estudiante_id" in data: obj.estudiante_id=int(data["estudiante_id"])
            if "curso_id" in data: obj.curso_id=int(data["curso_id"])
        if isinstance(obj,Asistencia):
            if "estado" in data and data["estado"].upper() not in ("PRESENTE","AUSENTE","TARDANZA","JUSTIFICADO"): 
                return error("Estado inválido.")
            for k in ("estado","curso_id","estudiante_id"):
                if k in data: setattr(obj,k,int(data[k]) if k.endswith("_id") else data[k].upper())
            if "fecha" in data: obj.fecha=parse_date(data["fecha"])
        db.session.commit(); return jsonify(datos=serializar(obj))
    except (TypeError,ValueError) as exc: db.session.rollback(); return error(str(exc))

def perfil_estudiante(estudiante):
    notas=[x.nota for x in estudiante.calificaciones]
    asist=[x.estado for x in estudiante.asistencias]
    return {**serializar(estudiante),"promedio":round(promedio(notas),2),"asistencia":round(porcentaje_asistencia(asist),2),"inasistencia":round(porcentaje_inasistencia(asist),2),"calificaciones":[serializar(x) for x in estudiante.calificaciones],"asistencias":[serializar(x) for x in estudiante.asistencias],"alertas":[serializar(x) for x in estudiante.alertas]}

@api.get("/estudiantes/<int:ident>/perfil")
def perfil(ident):
    e=Estudiante.query.get_or_404(ident); return jsonify(datos=perfil_estudiante(e))

@api.get("/dashboard")
def dashboard():
    estudiantes=Estudiante.query.all(); cursos=Curso.query.all()
    perfiles=[perfil_estudiante(e) for e in estudiantes]
    inferencias=inferir(perfiles,current_app.config["NOTA_MINIMA"],current_app.config["NOTA_OBSERVACION"],current_app.config["INASISTENCIA_MAXIMA"])
    niveles={"RIESGO ALTO":0,"EN OBSERVACIÓN":0,"RIESGO ACADÉMICO":0,"SIN ALERTAS":0,"ALERTA DE ASISTENCIA":0}
    for p in perfiles:
        conclusiones=inferencias.get(str(p["id"]),[])
        if "RIESGO ALTO" in conclusiones: niveles["RIESGO ALTO"]+=1
        elif "BAJO RENDIMIENTO" in conclusiones: niveles["RIESGO ACADÉMICO"]+=1
        elif "EN OBSERVACIÓN" in conclusiones: niveles["EN OBSERVACIÓN"]+=1
        elif "SIN ALERTAS" in conclusiones: niveles["SIN ALERTAS"]+=1
        if "ALERTA DE ASISTENCIA" in conclusiones: niveles["ALERTA DE ASISTENCIA"]+=1
    total_asist=[a.estado for a in Asistencia.query.all()]
    return jsonify(datos={"totales":{"estudiantes":len(estudiantes),"docentes":Docente.query.count(),"cursos":len(cursos)},"niveles":niveles,"promedio_general":round(promedio([p["promedio"] for p in perfiles if p["calificaciones"]]),2),"asistencia_general":round(porcentaje_asistencia(total_asist),2),"promedios_curso":[{"curso":c.nombre,"promedio":round(promedio([x.nota for x in c.calificaciones]),2)} for c in cursos],"asistencia":{"presente":sum(a.estado=="PRESENTE" for a in Asistencia.query.all()),"ausente":sum(a.estado=="AUSENTE" for a in Asistencia.query.all()),"tardanza":sum(a.estado=="TARDANZA" for a in Asistencia.query.all()),"justificado":sum(a.estado=="JUSTIFICADO" for a in Asistencia.query.all())},"evolucion":[{"fecha":x.fecha_registro.isoformat(),"promedio":x.nota} for x in Calificacion.query.order_by(Calificacion.fecha_registro).all()]})

@api.post("/riesgos/evaluar")
def evaluar_riesgos():
    perfiles=[perfil_estudiante(e) for e in Estudiante.query.all()]
    conf=current_app.config
    hechos=[{"id":p["id"],"promedio":p["promedio"],"inasistencia":p["inasistencia"]} for p in perfiles]
    resultados=inferir(hechos,conf["NOTA_MINIMA"],conf["NOTA_OBSERVACION"],conf["INASISTENCIA_MAXIMA"])
    niveles=[]
    for p in perfiles:
        conclusiones=resultados.get(str(p["id"]),[])
        nivel=("RIESGO ALTO" if "RIESGO ALTO" in conclusiones else "RIESGO ACADÉMICO" if "BAJO RENDIMIENTO" in conclusiones else "EN OBSERVACIÓN" if "EN OBSERVACIÓN" in conclusiones else "ALERTA DE ASISTENCIA" if "ALERTA DE ASISTENCIA" in conclusiones else "SIN ALERTAS")
        razones=[]
        if "BAJO RENDIMIENTO" in conclusiones: razones.append(f"Promedio {p['promedio']:.2f} menor que {conf['NOTA_MINIMA']}.")
        if "EN OBSERVACIÓN" in conclusiones: razones.append(f"Promedio {p['promedio']:.2f} en rango de observación.")
        if "ALERTA DE ASISTENCIA" in conclusiones: razones.append(f"Inasistencia {p['inasistencia']:.2f}% superior a {conf['INASISTENCIA_MAXIMA']}%.")
        if not razones: razones.append("No se activaron reglas de alerta.")
        niveles.append({"estudiante_id":p["id"],"estudiante":p["nombre_completo"],"promedio":p["promedio"],"inasistencia":p["inasistencia"],"nivel":nivel,"motivos":razones,"seguimiento_prioritario":"SEGUIMIENTO PRIORITARIO" in conclusiones})
        abierta=AlertaAcademica.query.filter_by(estudiante_id=p["id"],estado="PENDIENTE").first()
        if nivel!="SIN ALERTAS":
            if abierta: abierta.nivel=nivel; abierta.motivo=" ".join(razones); abierta.fecha=db.func.current_timestamp()
            else: db.session.add(AlertaAcademica(estudiante_id=p["id"],nivel=nivel,motivo=" ".join(razones)))
        elif abierta: abierta.estado="DESCARTADA"
    db.session.commit(); return jsonify(datos=niveles)

@api.get("/cursos/<int:ident>/estadisticas")
def estadisticas_curso(ident):
    curso=Curso.query.get_or_404(ident)
    notas=[c.nota for c in curso.calificaciones]
    estados=[a.estado for a in curso.asistencias]
    return jsonify(datos={"curso":curso.nombre,"cantidad_calificaciones":len(notas),"promedio":round(promedio(notas),2),"aprobados":sum(n>=current_app.config["NOTA_MINIMA"] for n in notas),"desaprobados":sum(n<current_app.config["NOTA_MINIMA"] for n in notas),"asistencia":round(porcentaje_asistencia(estados),2),"inasistencia":round(porcentaje_inasistencia(estados),2)})

@api.get("/reportes/rendimiento")
def reporte_rendimiento():
    filas=[]
    for e in Estudiante.query.order_by(Estudiante.apellido,Estudiante.nombre):
        p=perfil_estudiante(e)
        filas.append({"codigo":e.codigo,"estudiante":e.nombre_completo,"promedio":p["promedio"],"asistencia_pct":p["asistencia"],"inasistencia_pct":p["inasistencia"]})
    # Pandas compone la tabla del reporte y entrega registros ordenados por desempeño.
    tabla=pd.DataFrame(filas,columns=["codigo","estudiante","promedio","asistencia_pct","inasistencia_pct"])
    return jsonify(datos=tabla.to_dict(orient="records"))

@api.get("/reportes/rendimiento.csv")
def reporte_rendimiento_csv():
    filas=[{"codigo":e.codigo,"estudiante":e.nombre_completo,"promedio":perfil_estudiante(e)["promedio"],"asistencia_pct":perfil_estudiante(e)["asistencia"],"inasistencia_pct":perfil_estudiante(e)["inasistencia"]} for e in Estudiante.query]
    csv=pd.DataFrame(filas).to_csv(index=False) if filas else "codigo,estudiante,promedio,asistencia_pct,inasistencia_pct\n"
    return Response(csv,mimetype="text/csv",headers={"Content-Disposition":"attachment; filename=reporte_rendimiento.csv"})
