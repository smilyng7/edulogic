"""Entidades persistentes del dominio (POO mediante modelos SQLAlchemy)."""
from datetime import date, datetime
from sqlalchemy import CheckConstraint, UniqueConstraint, Index
from ..extensions import db


class EntidadActiva:
    """Comportamiento común polimórfico para entidades que pueden desactivarse."""
    def activar(self): 
        self.estado = "ACTIVO"
    def desactivar(self): 
        self.estado = "INACTIVO"


class Estudiante(EntidadActiva, db.Model):
    __tablename__ = "estudiantes"
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False, index=True)
    fecha_registro = db.Column(db.Date, nullable=False, default=date.today)
    estado = db.Column(db.String(12), nullable=False, default="ACTIVO")
    calificaciones = db.relationship("Calificacion", back_populates="estudiante", cascade="all, delete-orphan")
    asistencias = db.relationship("Asistencia", back_populates="estudiante", cascade="all, delete-orphan")
    alertas = db.relationship("AlertaAcademica", back_populates="estudiante", cascade="all, delete-orphan")
    
    @property
    def nombre_completo(self): 
        return f"{self.nombre} {self.apellido}"


class Docente(EntidadActiva, db.Model):
    __tablename__ = "docentes"
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False, index=True)
    estado = db.Column(db.String(12), nullable=False, default="ACTIVO")
    cursos = db.relationship("Curso", back_populates="docente")
    @property
    def nombre_completo(self): 
        return f"{self.nombre} {self.apellido}"


class Curso(EntidadActiva, db.Model):
    __tablename__ = "cursos"
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, default="")
    docente_id = db.Column(db.Integer, db.ForeignKey("docentes.id", ondelete="RESTRICT"), nullable=False)
    estado = db.Column(db.String(12), nullable=False, default="ACTIVO")
    docente = db.relationship("Docente", back_populates="cursos")
    calificaciones = db.relationship("Calificacion", back_populates="curso", cascade="all, delete-orphan")
    asistencias = db.relationship("Asistencia", back_populates="curso", cascade="all, delete-orphan")


class Calificacion(db.Model):
    __tablename__ = "calificaciones"
    __table_args__ = (CheckConstraint("nota >= 0 AND nota <= 20", name="ck_nota_rango"), Index("ix_calif_est_curso", "estudiante_id", "curso_id"))
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False)
    nota = db.Column(db.Float, nullable=False)
    fecha_registro = db.Column(db.Date, nullable=False, default=date.today)
    observacion = db.Column(db.String(250), default="")
    estudiante = db.relationship("Estudiante", back_populates="calificaciones")
    curso = db.relationship("Curso", back_populates="calificaciones")
    
    def aprobada(self, minima=11):
        return self.nota >= minima


class Asistencia(db.Model):
    __tablename__ = "asistencias"
    __table_args__ = (UniqueConstraint("estudiante_id", "curso_id", "fecha", name="uq_asistencia_dia"),)
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=date.today)
    estado = db.Column(db.String(12), nullable=False)
    estudiante = db.relationship("Estudiante", back_populates="asistencias")
    curso = db.relationship("Curso", back_populates="asistencias")


class AlertaAcademica(db.Model):
    __tablename__ = "alertas"
    __table_args__ = (UniqueConstraint("estudiante_id", "nivel", "estado", name="uq_alerta_abierta"),)
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False)
    nivel = db.Column(db.String(30), nullable=False)
    motivo = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    estado = db.Column(db.String(12), nullable=False, default="PENDIENTE")
    estudiante = db.relationship("Estudiante", back_populates="alertas")
