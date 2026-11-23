class Persona:
    """Clase base que aplica herencia y encapsulamiento."""
    def __init__(self, codigo: str, nombre: str, apellido: str, correo: str):
        self._codigo = codigo
        self._nombre = nombre
        self._apellido = apellido
        self._correo = correo

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def nombre_completo(self) -> str:
        return f"{self._nombre} {self._apellido}"

    @property
    def correo(self) -> str:
        return self._correo


class Estudiante(Persona):
    """Entidad principal del sistema académico."""
    def __init__(self, codigo: str, nombre: str, apellido: str, correo: str):
        super().__init__(codigo, nombre, apellido, correo)
        self.calificaciones = []
        self.total_sesiones = 0
        self.inasistencias = 0

    def agregar_calificacion(self, calificacion: 'Calificacion'):
        self.calificaciones.append(calificacion)

    def registrar_asistencia(self, total_sesiones: int, inasistencias: int):
        self.total_sesiones = total_sesiones
        self.inasistencias = inasistencias

    def to_dict(self) -> dict:
        return {
            "codigo": self.codigo,
            "nombre_completo": self.nombre_completo,
            "correo": self.correo,
            "notas": [c.nota for c in self.calificaciones],
            "total_sesiones": self.total_sesiones,
            "inasistencias": self.inasistencias
        }


class Curso:
    """Representa una asignatura académica."""
    def __init__(self, codigo: str, nombre: str, docente: str):
        self.codigo = codigo
        self.nombre = nombre
        self.docente = docente


class Calificacion:
    """Representa la nota obtenida por un estudiante en un curso."""
    def __init__(self, codigo_estudiante: str, codigo_curso: str, nota: float, fecha: str):
        self.codigo_estudiante = codigo_estudiante
        self.codigo_curso = codigo_curso
        self.nota = float(nota)
        self.fecha = fecha


class AlertaAcademica:
    """Representa el resultado inferido por el motor lógico."""
    def __init__(self, codigo_estudiante: str, nombre_estudiante: str, promedio: float,
                 porcentaje_inasistencia: float, nivel_riesgo: str, motivo: str, color_badge: str):
        self.codigo_estudiante = codigo_estudiante
        self.nombre_estudiante = nombre_estudiante
        self.promedio = promedio
        self.porcentaje_inasistencia = porcentaje_inasistencia
        self.nivel_riesgo = nivel_riesgo
        self.motivo = motivo
        self.color_badge = color_badge