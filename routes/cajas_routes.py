from flask import (Blueprint,redirect,request,render_template)
from datetime import datetime
from config import *
import pandas as pd
from datos_utils import *
from ubicaciones_utils import *
from cajas_utils import *

cajas_bp = Blueprint(
    "cajas",
    __name__
)

@cajas_bp.route("/cajas")
def cajas():

    cajas_df = pd.read_excel(ARCHIVO_CAJAS)
    contenido = leer_excel_seguro(ARCHIVO_CONTENIDO_CAJAS, ["CajaID", "Numero"])

    cajas_data = []

    for _, fila in cajas_df.iterrows():

        caja_id = fila["CajaID"]

        ocupados = len(contenido[contenido["CajaID"] == caja_id])

        capacidad = int(fila["Capacidad"]) if not pd.isna(fila["Capacidad"]) else 0

        libres = capacidad - ocupados
        porcentaje = round(ocupados * 100 / capacidad) if capacidad else 0

        if porcentaje >= 100:
            aviso = "🔴 LLENA"
        elif porcentaje >= 80:
            aviso = "🟠 CASI LLENA"
        else:
            aviso = "🟢"

        cajas_data.append({
            **fila.to_dict(),
            "ocupados": ocupados,
            "libres": libres,
            "porcentaje": porcentaje,
            "aviso": aviso
        })

    return render_template("pages/cajas/lista.html", cajas=cajas_data)


@cajas_bp.route("/caja/<int:caja_id>")
def ver_caja(caja_id):

    cajas = pd.read_excel(ARCHIVO_CAJAS)
    contenido = leer_excel_seguro(ARCHIVO_CONTENIDO_CAJAS, ["CajaID", "Numero"])
    catalogo = pd.read_excel(ARCHIVO_EXCEL)

    caja_row = cajas[cajas["CajaID"] == caja_id]

    if len(caja_row) == 0:
        return "Caja no encontrada"

    caja = caja_row.iloc[0]

    ubicacion, sububicacion = obtener_ubicacion_caja(caja_id)

    articulos = contenido[contenido["CajaID"] == caja_id]

    ocupados = len(articulos)
    libres = int(caja["Capacidad"]) - ocupados

    articulos_data = []

    for _, fila in articulos.iterrows():
        art = catalogo[catalogo["Número"] == fila["Numero"]]
        if len(art):
            articulos_data.append(art.iloc[0].to_dict())

    return render_template(
        "pages/cajas/detalle.html",
        caja=caja,
        ubicacion=ubicacion,
        sububicacion=sububicacion,
        ocupados=ocupados,
        libres=libres,
        articulos=articulos_data
    )


@cajas_bp.route(
    "/mover_caja/<int:caja_id>",
    methods=["GET", "POST"]
)
def mover_caja(caja_id):

    if request.method == "POST":

        ubicacion = request.form[
            "ubicacion"
        ]

        sububicacion = request.form[
            "sububicacion"
        ]

        guardar_ubicacion_caja(
            caja_id,
            ubicacion,
            sububicacion
        )

        return redirect(
            f"/caja/{caja_id}"
        )

    ubicaciones = pd.read_excel(
        ARCHIVO_UBICACIONES
    )

    opciones = []

    for _, fila in ubicaciones.iterrows():

        opciones.append({
            "valor":
                f"{fila['Ubicación']}|{fila['Sububicación']}",

            "texto":
                f"{fila['Ubicación']} > {fila['Sububicación']}"
        })

    return render_template(
        "pages/cajas/mover.html",
        caja_id=caja_id,
        opciones=opciones
    )

@cajas_bp.route("/asignar_caja/<int:numero>", methods=["GET", "POST"])
def asignar_caja(numero):

    cajas = pd.read_excel(ARCHIVO_CAJAS)

    if request.method == "POST":

        caja_id = int(request.form["caja"])

        try:
            df = pd.read_excel(ARCHIVO_CONTENIDO_CAJAS)
        except:
            df = pd.DataFrame(columns=["CajaID", "Numero"])

        # 🔁 actualizar o insertar relación
        existe = df[df["Numero"] == numero]

        if len(existe) > 0:
            df.loc[df["Numero"] == numero, "CajaID"] = caja_id
        else:
            df = pd.concat([
                df,
                pd.DataFrame([{"CajaID": caja_id, "Numero": numero}])
            ], ignore_index=True)

        df.to_excel(ARCHIVO_CONTENIDO_CAJAS, index=False)

        # 📍 actualizar ubicación del artículo
        ubicacion, sububicacion = obtener_ubicacion_caja(caja_id)

        guardar_ubicacion(numero, ubicacion, sububicacion)

        return redirect(f"/articulo/{numero}")

    cajas_data = cajas.to_dict(orient="records")

    return render_template(
        "pages/cajas/asignar.html",
        numero=numero,
        cajas=cajas_data
    )


@cajas_bp.route(
    "/quitar_caja/<int:numero>"
)
def quitar_caja(numero):

    try:

        df = pd.read_excel(
            ARCHIVO_CONTENIDO_CAJAS
        )

        df = df[
            df["Numero"] != numero
        ]

        df.to_excel(
            ARCHIVO_CONTENIDO_CAJAS,
            index=False
        )

        return redirect(
            f"/articulo/{numero}"
        )

    except Exception as e:

        return f"<pre>{e}</pre>"


@cajas_bp.route("/buscar_caja")
def buscar_caja():

    texto = request.args.get("q", "")

    catalogo = pd.read_excel(ARCHIVO_EXCEL)

    try:
        contenido = pd.read_excel(ARCHIVO_CONTENIDO_CAJAS)
    except:
        contenido = pd.DataFrame(columns=["CajaID", "Numero"])

    try:
        cajas = pd.read_excel(ARCHIVO_CAJAS)
    except:
        cajas = pd.DataFrame(columns=["CajaID", "Nombre"])

    resultados = []

    if texto:

        mascara = (
            catalogo.astype(str)
            .apply(lambda col: col.str.contains(texto, case=False, na=False))
            .any(axis=1)
        )

        resultado = catalogo[mascara]

        for _, fila in resultado.iterrows():

            numero = fila["Número"]

            caja_nombre = "SIN CAJA"

            fila_caja = contenido[contenido["Numero"] == numero]

            if len(fila_caja) > 0:

                caja_id = fila_caja.iloc[0]["CajaID"]

                caja = cajas[cajas["CajaID"] == caja_id]

                if len(caja) > 0:
                    caja_nombre = caja.iloc[0]["Nombre"]

            resultados.append({
                "numero": numero,
                "marca": fila["Marca"],
                "referencia": fila["Referencia"],
                "caja": caja_nombre
            })

    return render_template(
        "pages/cajas/buscar.html",
        texto=texto,
        resultados=resultados
    )


@cajas_bp.route("/crear_caja", methods=["GET", "POST"])
def crear_caja_route():

    if request.method == "POST":

        nombre = request.form["nombre"]
        tipo = request.form["tipo"]
        capacidad = request.form["capacidad"]
        ubicacion = request.form["ubicacion"]
        sububicacion = request.form["sububicacion"]

        crear_caja(
            nombre,
            tipo,
            capacidad,
            ubicacion,
            sububicacion
        )

        return redirect("/cajas")

    return render_template(
            "pages/cajas/crear.html"
            )

@cajas_bp.route(
    "/eliminar_caja/<int:caja_id>"
)
def eliminar_caja(caja_id):

    df_cajas = pd.read_excel(
        ARCHIVO_CAJAS
    )

    df_contenido = pd.read_excel(
        ARCHIVO_CONTENIDO_CAJAS
    )

    articulos = df_contenido[
        df_contenido["CajaID"] == caja_id
    ]

    if len(articulos) > 0:

        return """
        <h1>No se puede eliminar</h1>

        <p>
        La caja contiene artículos.
        </p>

        <a href="/cajas">
        Volver
        </a>
        """

    df_cajas = df_cajas[
        df_cajas["CajaID"] != caja_id
    ]

    df_cajas.to_excel(
        ARCHIVO_CAJAS,
        index=False
    )

    return redirect("/cajas")


@cajas_bp.route("/editar_caja/<int:caja_id>", methods=["GET", "POST"])
def editar_caja(caja_id):

    df = pd.read_excel(ARCHIVO_CAJAS)

    fila = df[df["CajaID"] == caja_id]

    if len(fila) == 0:
        return "Caja no encontrada"

    indice = fila.index[0]
    caja = fila.iloc[0]

    if request.method == "POST":

        df.loc[indice, "Nombre"] = request.form["nombre"]
        df.loc[indice, "Tipo"] = request.form["tipo"]
        df.loc[indice, "Capacidad"] = request.form["capacidad"]
        df.loc[indice, "Ubicación"] = request.form["ubicacion"]
        df.loc[indice, "Sububicación"] = request.form["sububicacion"]

        df.to_excel(ARCHIVO_CAJAS, index=False)

        return redirect(f"/caja/{caja_id}")

    return render_template(
        "pages/cajas/editar.html",
        caja=caja
    )
