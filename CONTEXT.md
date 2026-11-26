# Paradigmas de programación en EduLogic

## 1. Alcance

Análisis del código fuente del repositorio edulogic-main. Las rutas son
relativas a la raíz del repositorio.

## 2. Versión básica: edulogic/

### Orientación a objetos

Archivo: `edulogic/models/entidades.py`. - `Persona`: clase base,
atributos protegidos por convención y propiedades. -
`Estudiante(Persona)`: herencia, `super().__init__`, métodos
`agregar_calificacion` y `registrar_asistencia`. - `Curso`,
`Calificacion`, `AlertaAcademica`: objetos del dominio académico.

### Funcional

Archivo: `edulogic/core/funcional.py`. - `calcular_promedio`: lambda y
reduce. - `transformar_estudiantes`: map y lambda. -
`filtrar_desaprobados` y `filtrar_inasistencias_criticas`: filter. -
`calcular_promedio_general`: reduce y map. Estas operaciones transforman
colecciones; no implican que todo el programa sea puramente funcional.

### Lógico

Archivo: `edulogic/core/logico.py`. - `MotorLogicoEduLogic`: almacena
hechos en `base_hechos`. - `cargar_hechos`: construye tuplas de
rendimiento. - `_regla_prioridad_seguimiento`, `_regla_riesgo_alto`,
`_regla_observacion` y `_regla_alerta_asistencia`: predicados
booleanos. - `inferir_alertas`: aplica reglas ordenadas mediante if/elif
y genera objetos AlertaAcademica. Es un motor de reglas implementado
imperativamente, no un motor Datalog.

### Imperativo y procedimental

-   `edulogic/app.py`: configuración Flask, funciones de rutas y
    persistencia SQLite.
-   `edulogic/core/cargador_datos.py`: carga y recorrido de datos.
-   `edulogic/core/estadisticas.py`: cálculos NumPy/pandas, agrupación y
    construcción de resultados.

## 3. Versión desarrollada: lenguaje_programacion/edulogic/

### Orientación a objetos

Archivo: `backend/app/models/__init__.py` bajo la carpeta anterior. -
`EntidadActiva`: comportamiento reutilizable activar/desactivar. -
`Estudiante`, `Docente`, `Curso`, `Calificacion`, `Asistencia`,
`AlertaAcademica`: modelos SQLAlchemy. - `Calificacion.aprobada`:
comportamiento de dominio. - Relaciones y restricciones de integridad
mediante SQLAlchemy. Los archivos individuales de models reexportan
clases definidas en **init**.py.

### Funcional

Archivo: `backend/app/paradigmas/funcional/__init__.py`. - `promedio`:
map y reduce. - `filtrar_desaprobados`, `filtrar_inasistencia_elevada`:
filter. - `promedios_por_estudiante`, `agrupar_por_nivel`: agrupación. -
`estadisticas_curso`: transformación de colecciones. Se combina
programación funcional con ciclos y estructuras mutables locales.

### Lógico declarativo

Archivo: `backend/app/paradigmas/logica/__init__.py`. - `inferir`: carga
hechos rendimiento y asistencia mediante PyDatalog. - Reglas
bajo_rendimiento, observacion, alerta_asistencia, riesgo_alto,
prioritario y sin_alertas. - `pyDatalog.ask` consulta conclusiones. A
diferencia de la versión básica, las reglas se expresan
declarativamente.

### Imperativo y procedimental

-   `backend/run.py`: comandos de ejecución, inicialización y datos de
    demostración.
-   `backend/app/routes/__init__.py`: API Flask, validación y
    operaciones sobre modelos.
-   `frontend/js/app.js`: comportamiento del cliente; no confundir
    JavaScript con los paradigmas implementados en el backend.

## 4. Flujo multiparadigma

1.  Las rutas reciben solicitudes.
2.  Los modelos representan y persisten entidades.
3.  Las funciones calculan indicadores.
4.  Las reglas clasifican el riesgo.
5.  El backend devuelve resultados a la interfaz.

## 5. Conclusión

La versión básica demuestra integración de paradigmas mediante clases,
funciones y reglas condicionales. La versión desarrollada separa
responsabilidades y emplea un motor lógico declarativo. Los paradigmas
se complementan: no son carpetas mutuamente excluyentes.
