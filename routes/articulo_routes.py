from flask import (
    Blueprint,
    request,
    redirect,
    render_template
)
from werkzeug.utils import secure_filename
from config import *
import pandas as pd
from datetime import datetime
from datos_utils import *
from cajas_utils import *
from ubicaciones_utils import registrar_movimiento


articulo_bp = Blueprint(
    "articulo",
    __name__
)


@articulo_bp.route("/articulo/<int:numero>")
def articulo(numero):

    df = cargar_datos()

    fila = df[df["Número"] == numero]

    if len(fila) == 0:
        return "Artículo no encontrado"

    fila = fila.iloc[0]

    caja = obtener_caja(numero)
    caja_id = obtener_caja_id(numero)

    ubicacion_caja, sububicacion_caja = obtener_ubicacion_articulo(numero)
    ubicacion, sububicacion = obtener_ubicacion(numero)

    imagen = str(fila["Imagen"])

    return render_template(
        "pages/articulo/detalle.html",
        fila=fila,
        imagen=imagen,
        numero=numero,
        ubicacion=ubicacion,
        sububicacion=sububicacion,
        caja=caja,
        caja_id=caja_id,
        ubicacion_caja=ubicacion_caja,
        sububicacion_caja=sububicacion_caja
    )


@articulo_bp.route("/buscar", methods=["GET"])
def buscar():

    marca = request.args.get(
        "marca",
        ""
    )

    descripcion = request.args.get(
        "descripcion",
        ""
    )

    df = pd.read_excel(
        ARCHIVO_EXCEL
    )

    # ===== LISTA DE MARCAS =====

    marcas = (
        df["Marca"]
        .dropna()
        .astype(str)
        .sort_values()
        .unique()
        .tolist()
    )

    # ===== FILTRO =====

    resultado = df.copy()

    if marca:

        resultado = resultado[
            resultado["Marca"]
            .astype(str)
            .str.contains(
                marca,
                case=False,
                na=False
            )
        ]

    if descripcion:

        resultado = resultado[
            resultado["Descripción"]
            .astype(str)
            .str.contains(
                descripcion,
                case=False,
                na=False
            )
        ]

    # ===== LIMITAR SI NO HAY BÚSQUEDA =====

    if not marca and not descripcion:

        resultado = df.head(100)

    # ===== RESULTADOS =====

    articulos = []

    for _, fila in resultado.iterrows():

        articulos.append({

            "numero": fila["Número"],

            "marca": str(
                fila["Marca"]
            ),

            "referencia": str(
                fila["Referencia"]
            ),

            "descripcion": str(
                fila["Descripción"]
            )
        })

    return render_template(
        "pages/articulo/buscar.html",
        articulos=articulos,
        total=len(resultado),
        marca=marca,
        descripcion=descripcion,
        marcas=marcas
    )

@articulo_bp.route("/historial/<int:numero>")
def historial(numero):

    try:

        df = pd.read_excel(
            ARCHIVO_MOVIMIENTOS
        )

        df = df[
            df["Número"] == numero
        ]

        movimientos = []

        for _, fila in (

            df.sort_values(
                by="Fecha",
                ascending=False
            )

            .iterrows()

        ):

            movimientos.append({

                "fecha": fila["Fecha"],

                "origen": fila["Origen"],

                "destino": fila["Destino"]

            })

        return render_template(
            "pages/articulo/historial.html",
            movimientos=movimientos,
            numero=numero
        )

    except Exception as e:

        return f"<pre>{e}</pre>"
    
@articulo_bp.route(
    "/cambiar_ubicacion/<int:numero>",
    methods=["GET", "POST"]
)
def cambiar_ubicacion(numero):

    if request.method == "POST":

        ubicacion = request.form[
            "ubicacion"
        ]

        sububicacion = request.form[
            "sububicacion"
        ]

        guardar_ubicacion(

            numero,

            ubicacion,

            sububicacion

        )

        return redirect(
            f"/articulo/{numero}"
        )

    df = pd.read_excel(
        ARCHIVO_UBICACIONES
    )

    opciones = []

    for _, fila in df.iterrows():

        ubicacion = fila[
            "Ubicación"
        ]

        sububicacion = fila[
            "Sububicación"
        ]

        opciones.append({

            "valor":
            f"{ubicacion}|{sububicacion}",

            "texto":
            f"{ubicacion} > {sububicacion}"

        })

    return render_template(
        "pages/articulo/cambiar_ubicacion.html",
        numero=numero,
        opciones=opciones
        )


@articulo_bp.route(
    "/subir_imagen/<int:numero>",
    methods=["GET", "POST"]
)
def subir_imagen(numero):

    df = pd.read_excel(
        ARCHIVO_EXCEL
    )

    fila = df[
        df["Número"] == numero
    ]

    if len(fila) == 0:

        return "Artículo no encontrado"

    fila = fila.iloc[0]

    referencia = str(
        fila["Referencia"]
    )

    if request.method == "POST":

        if "imagen" not in request.files:

            return "No se recibió archivo"

        archivo = request.files["imagen"]

        if archivo.filename == "":

            return "No se seleccionó archivo"

        extension = os.path.splitext(
            archivo.filename
        )[1]

        nombre_destino = secure_filename(
            referencia + extension.lower()
        )

        ruta_destino = os.path.join(
            CARPETA_IMAGENES,
            nombre_destino
        )

        archivo.save(
            ruta_destino
        )

        return redirect(
            f"/articulo/{numero}"
        )

    # ESTE RETURN DEBE EXISTIR
    return render_template(
        "pages/articulo/subir_imagen.html",
        referencia=referencia,
        numero=numero
    )



@articulo_bp.route("/imagen/<nombre>")
def imagen(nombre):

    carpeta = "imagenes"

    posibles = [
        f"{nombre}.jpg",
        f"{nombre}.jpeg",
        f"{nombre}.png",
        f"{nombre}.JPG",
        f"{nombre}.PNG",
    ]

    for archivo in posibles:
        ruta = os.path.join(carpeta, archivo)

        if os.path.exists(ruta):
            return send_from_directory(carpeta, archivo)

    return "Imagen no encontrada", 404



