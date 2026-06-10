
from flask import (Blueprint,render_template)
import pandas as pd
import os
import shutil
from datetime import datetime

from estadisticas_utils import *
from ubicaciones_utils import *
from imagenes_utils import *
from config import *

inicio_bp = Blueprint(
    "inicio",
    __name__
)

@inicio_bp.route("/")
def inicio():

    stats = obtener_estadisticas()

    ubicaciones = resumen_ubicaciones()

    movimientos = ultimos_movimientos()


    return render_template(
        "inicio.html",
        stats=stats,
        ubicaciones=ubicaciones,
        movimientos=movimientos
    )

@inicio_bp.route("/backup")
def backup():

    fecha = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    carpeta = os.path.join(
        "backups",
        fecha
    )

    os.makedirs(
        carpeta,
        exist_ok=True
    )

    archivos = [
        ARCHIVO_EXCEL,
        ARCHIVO_INVENTARIO,
        ARCHIVO_MOVIMIENTOS,
        ARCHIVO_CAJAS,
        ARCHIVO_CONTENIDO_CAJAS,
        ARCHIVO_UBICACION_CAJAS,
        ARCHIVO_UBICACIONES
    ]

    for archivo in archivos:

        if os.path.exists(archivo):

            shutil.copy2(
                archivo,
                os.path.join(
                    carpeta,
                    os.path.basename(archivo)
                )
            )

    return f"""
    <h1>Backup realizado</h1>

    <p>

    {fecha}

    </p>

    <a href="/admin">
    Volver
    </a>
    """


@inicio_bp.route("/estadisticas")
def estadisticas():

    df = pd.read_excel(ARCHIVO_EXCEL)

    total = len(df)

    con_imagen = 0

    for _, fila in df.iterrows():

        referencia = str(fila["Referencia"])

        if existe_imagen(referencia):

            con_imagen += 1

    sin_imagen = total - con_imagen

    return f"""
    <h1>Estadísticas</h1>

    <p>Total artículos: {total}</p>

    <p>Con imagen: {con_imagen}</p>

    <p>Sin imagen: {sin_imagen}</p>

    <a href='/'>
    Volver
    </a>
    """
