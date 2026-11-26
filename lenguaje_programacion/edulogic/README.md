# EduLogic

Sistema web de apoyo a la evaluación y seguimiento académico. Centraliza estudiantes, docentes, cursos, calificaciones y asistencias; calcula indicadores con procesamiento funcional y obtiene conclusiones con reglas PyDatalog. Las alertas orientan el seguimiento docente y no son diagnósticos sobre el estudiante.

## Problema, justificación y objetivos

La información académica suele estar fragmentada en registros independientes, lo que retrasa la detección de dificultades. EduLogic centraliza estos datos para consultar promedios, asistencia, cursos y alertas en un solo panel. Sus objetivos son mantener registros íntegros, resumir el rendimiento y facilitar decisiones oportunas del equipo docente.

## Arquitectura y tecnologías

Aplicación monolítica modular: Flask presenta el frontend y expone JSON REST; SQLAlchemy persiste entidades en SQLite; servicios de dominio y paradigmas contienen los cálculos; Bootstrap y JavaScript Fetch consumen la API, y Chart.js presenta el dashboard. Flask-CORS permite configuración de orígenes para despliegues separados. Pandas prepara reportes tabulares.

- Python 3.10+ recomendado, Flask, Flask-SQLAlchemy, SQLAlchemy, Flask-CORS, PyDatalog, Pandas, python-dotenv y Pytest.
- SQLite; HTML5, CSS3, JavaScript, Bootstrap 5 y Chart.js.

## Estructura

```text
edulogic/
├── backend/app/{models,routes,services,repositories,paradigmas,utils}/
├── backend/tests/
├── backend/run.py
├── frontend/{index.html,js/}
├── database/                 # edulogic.db se crea al inicializar
├── docs/paradigmas.md
├── .env.example
└── README.md
```

## Instalación y ejecución

Desde `edulogic/`, crear un entorno y activar según el sistema operativo:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
Copy-Item .env.example .env
cd backend
python run.py init-db
python run.py seed       # opcional; datos demostrativos una sola vez
python run.py            # http://127.0.0.1:5000
```

En Linux/macOS, activar con `source .venv/bin/activate` y copiar `.env.example` como `.env`. La aplicación sirve `frontend/index.html` desde Flask, por lo que no se necesita servidor frontend independiente. No se carga información de demostración en cada inicio. `seed` no hace nada si ya existen estudiantes.

Variables `.env`: `SECRET_KEY`, `DATABASE_URL`, `CORS_ORIGINS`, `NOTA_MINIMA`, `NOTA_OBSERVACION` e `INASISTENCIA_MAXIMA`. Desde el directorio `backend`, la URL SQLite de ejemplo apunta a `edulogic/database/edulogic.db`.

## Pruebas

Desde `edulogic/backend/`: `python -m pytest -q`. Las pruebas cubren transformaciones funcionales, cinco escenarios lógicos, endpoints, validación, integridad de asistencia y dashboard. La base de pruebas es temporal.

## Paradigmas

- **POO:** los modelos SQLAlchemy (`backend/app/models/`) encapsulan relaciones y comportamiento (`nombre_completo`, `aprobada`, activar/desactivar). `EntidadActiva` comparte comportamiento a través de herencia.
- **Funcional:** `backend/app/paradigmas/funcional/` calcula promedios, filtros y porcentajes sin modificar entradas, usando `map`, `filter`, `reduce` y `lambda`.
- **Lógica:** `backend/app/paradigmas/logica/` afirma hechos de promedio e inasistencia y ejecuta reglas PyDatalog; la documentación está en `docs/paradigmas.md`.

## API

Todas las respuestas exitosas usan `{ "datos": ... }`; errores usan `{ "error": { "code", "message" } }`.

| Método | Ruta | Función |
|---|---|---|
| GET/POST | `/api/estudiantes`, `/api/docentes`, `/api/cursos`, `/api/calificaciones`, `/api/asistencias`, `/api/alertas` | Listar y crear |
| GET/PUT/DELETE | `/api/<recurso>/<id>` | Consultar, editar y eliminar |
| GET | `/api/estudiantes/<id>/perfil` | Perfil con notas y asistencia |
| GET | `/api/cursos/<id>/estadisticas` | Estadísticas del curso |
| GET | `/api/dashboard` | Indicadores y series para gráficos |
| POST | `/api/riesgos/evaluar` | Inferir categorías y sincronizar alertas |
| GET | `/api/reportes/rendimiento` | Reporte JSON |
| GET | `/api/reportes/rendimiento.csv` | Exportación CSV |

Ejemplo de creación:

```bash
curl -X POST http://127.0.0.1:5000/api/estudiantes \
  -H 'Content-Type: application/json' \
  -d '{"codigo":"E001","nombre":"Ana","apellido":"Rojas","correo":"ana@ejemplo.edu"}'
```

Notas permitidas: 0–20; aprobación predeterminada: 11. Asistencia acepta `PRESENTE`, `AUSENTE`, `TARDANZA`, `JUSTIFICADO`; justificados no entran al denominador, tardanzas cuentan como asistencia y solo `AUSENTE` cuenta como inasistencia. Una asistencia por estudiante, curso y fecha.

## Datos demo

El comando `python run.py seed` crea un docente, tres cursos, diez estudiantes, notas y estados de asistencia variados, con ejemplos de las categorías de riesgo. Úsese solo en una base vacía.

## Alcance de seguridad

Se validan campos, correos básicos, rangos, claves únicas y registros relacionados. La aplicación no implementa autenticación ni autorización; para uso institucional se debe desplegar detrás de controles de acceso y configurar claves y CORS. Las operaciones sobre registros inexistentes devuelven 404.
