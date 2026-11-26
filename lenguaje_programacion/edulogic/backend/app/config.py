"""Configuración central de EduLogic."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-en-produccion")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'database' / 'edulogic.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    NOTA_MINIMA = float(os.getenv("NOTA_MINIMA", "11"))
    NOTA_OBSERVACION = float(os.getenv("NOTA_OBSERVACION", "13"))
    INASISTENCIA_MAXIMA = float(os.getenv("INASISTENCIA_MAXIMA", "20"))
