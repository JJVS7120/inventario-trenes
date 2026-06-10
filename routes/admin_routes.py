from flask import (Blueprint,request,render_template)
from imagenes_utils import *
from datos_utils import *
from estadisticas_utils import *
import pandas as pd
from config import *


admin_bp = Blueprint(
    "admin",
    __name__
)


@admin_bp.route("/admin")
def admin():

    return render_template(
        "pages/admin/dashboard.html"
    )


@admin_bp.route("/sin_imagen")
def sin_imagen():

    df = pd.read_excel(
        ARCHIVO_EXCEL
    )

    articulos = []

    for _, fila in df.iterrows():

        numero = fila["Número"]

        referencia = str(
            fila["Referencia"]
        )

        marca = str(
            fila["Marca"]
        )

        if not existe_imagen(
            referencia
        ):

            articulos.append({

                "numero": numero,

                "marca": marca,

                "referencia": referencia

            })

    return render_template(
        "pages/admin/sin_imagen.html",
        articulos=articulos,
        total=len(articulos)
    )

@admin_bp.route("/sin_ubicacion")
def sin_ubicacion():

    inventario = pd.read_excel(
        ARCHIVO_INVENTARIO
    )

    ubicados = set(
        inventario["Número"]
    )

    catalogo = pd.read_excel(
        ARCHIVO_EXCEL
    )

    articulos = []

    for _, fila in catalogo.iterrows():

        numero = fila["Número"]

        if numero not in ubicados:

            articulos.append({

                "numero": int(fila["Número"]),

                "marca": str(fila["Marca"]),

                "referencia": str(fila["Referencia"])

            })

    return render_template(
        "pages/admin/sin_ubicacion.html",
        articulos=articulos,
        total=len(articulos)
    )


@admin_bp.route("/seleccion_masiva")
def seleccion_masiva():

    df = pd.read_excel(ARCHIVO_EXCEL)

    articulos = []

    for _, fila in df.iterrows():

        articulos.append({
            "numero": fila["Número"],
            "marca": fila["Marca"],
            "referencia": fila["Referencia"]
        })

    return render_template(
        "pages/admin/seleccion_masiva.html",
        articulos=articulos
    )



@admin_bp.route("/mover_masivo", methods=["POST"])
def mover_masivo():

    seleccionados = request.form.getlist("articulos")

    if not seleccionados:

        return "No hay artículos seleccionados"

    df_ubic = pd.read_excel(ARCHIVO_UBICACIONES)

    opciones = []

    for _, fila in df_ubic.iterrows():

        opciones.append({
            "valor": f"{fila['Ubicación']}|{fila['Sububicación']}",
            "texto": f"{fila['Ubicación']} > {fila['Sububicación']}"
        })

    return render_template(
        "pages/admin/mover_masivo.html",
        seleccionados=seleccionados,
        opciones=opciones
    )

@admin_bp.route("/guardar_movimiento_masivo", methods=["POST"])
def guardar_movimiento_masivo():

    articulos = request.form.getlist("articulos")

    destino = request.form["destino"]

    ubicacion, sububicacion = destino.split("|")

    for numero in articulos:

        guardar_ubicacion(
            int(numero),
            ubicacion,
            sububicacion
        )

    return f"""
    <h1>Movimiento completado</h1>
    <p>{len(articulos)} artículos movidos</p>
    <a href='/'>Volver</a>
    """

@admin_bp.route("/historial_general")
def historial_general():

    try:
        df = pd.read_excel(ARCHIVO_MOVIMIENTOS)
    except:
        return "No hay movimientos"

    df = df.sort_values(
        by="Fecha",
        ascending=False
    ).head(50)

    movimientos = []

    for _, fila in df.iterrows():

        movimientos.append({
            "fecha": str(fila["Fecha"]),
            "origen": str(fila.get("Origen", "")),
            "destino": str(fila.get("Destino", "")),
            "numero": fila.get("Número", "")
        })

    return render_template(
        "pages/admin/historial_general.html",
        movimientos=movimientos
    )




