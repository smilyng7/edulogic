# Integración de los paradigmas en EduLogic

## Flujo

1. SQLAlchemy recupera las entidades persistidas.
2. Las funciones puras en `backend/app/paradigmas/funcional/` agregan calificaciones y asistencias.
3. `backend/app/paradigmas/logica/` carga un conjunto de hechos mediante `assert_fact` y ejecuta las reglas declarativas de PyDatalog.
4. El servicio de evaluación presenta motivos y sincroniza alertas pendientes sin crear duplicados.

## Hechos y reglas

Cada evaluación construye los hechos `rendimiento(id, promedio)` y `asistencia(id, porcentaje_inasistencia)`. PyDatalog deriva:

- `bajo_rendimiento(X)` si `rendimiento(X,P)` y `P < NOTA_MINIMA`.
- `observacion(X)` si `NOTA_MINIMA <= P <= NOTA_OBSERVACION`.
- `alerta_asistencia(X)` si `I > INASISTENCIA_MAXIMA`.
- `riesgo_alto(X)` si `bajo_rendimiento(X)` y `alerta_asistencia(X)`.
- `prioritario(X)` si `riesgo_alto(X)`.
- `sin_alertas(X)` si el promedio aprueba y la inasistencia no supera el umbral.

Los umbrales vienen de la configuración central y pueden reemplazarse por variables de entorno. La inferencia se protege con un bloqueo porque PyDatalog usa un espacio de conocimiento compartido; cada consulta limpia y vuelve a cargar sus hechos.

## Categorías en la API

La API prioriza la presentación: riesgo alto; bajo rendimiento como riesgo académico; promedio de observación; alerta de asistencia; y sin alertas. El motor conserva todas las conclusiones compatibles, por lo que un estudiante con promedio alto y demasiadas faltas mantiene una alerta de asistencia.

## Convenciones de asistencia

Justificado se excluye del cálculo de asistencia e inasistencia. Tardanza forma parte del denominador y se considera presente. Ausente es el único estado que suma inasistencia. Sin sesiones consideradas, el porcentaje se define como 0 para no producir división por cero.
