from flask import Blueprint,render_template,request,redirect
from ubicaciones_utils import *
from datos_utils import *
from config import *
import pandas as pd

ubicaciones_bp = Blueprint(
    "ver_ubicaciones",
    __name__
)




@ubicaciones_bp.route("/ubicaciones")
def ver_ubicaciones():

    df = pd.read_excel(ARCHIVO_UBICACIONES)

    ubicaciones = df.to_dict(orient="records")

    return render_template(
        "pages/ubicaciones/lista.html",
        ubicaciones=ubicaciones
    )



@ubicaciones_bp.route("/ubicaciones/nueva", methods=["GET", "POST"])
def nueva_ubicacion():

    if request.method == "POST":

        df = pd.read_excel(ARCHIVO_UBICACIONES)

        nueva = {
            "Ubicación": request.form["ubicacion"],
            "Sububicación": request.form["sububicacion"]
        }

        df = pd.concat([df, pd.DataFrame([nueva])], ignore_index=True)

        df.to_excel(ARCHIVO_UBICACIONES, index=False)

        return redirect("/ubicaciones")

    return render_template("pages/ubicaciones/form.html")


@ubicaciones_bp.route("/ubicaciones/editar/<int:index>", methods=["GET", "POST"])
def editar_ubicacion(index):

    df = pd.read_excel(ARCHIVO_UBICACIONES)

    if request.method == "POST":

        df.loc[index, "Ubicación"] = request.form["ubicacion"]
        df.loc[index, "Sububicación"] = request.form["sububicacion"]

        df.to_excel(ARCHIVO_UBICACIONES, index=False)

        return redirect("/ubicaciones")

    ubicacion = df.iloc[index].to_dict()

    return render_template(
        "pages/ubicaciones/form.html",
        ubicacion=ubicacion,
        index=index
    )

@ubicaciones_bp.route("/ubicaciones/eliminar/<int:index>")
def eliminar_ubicacion(index):

    df = pd.read_excel(ARCHIVO_UBICACIONES)

    df = df.drop(index)

    df.to_excel(ARCHIVO_UBICACIONES, index=False)

    return redirect("/ubicaciones")



@ubicaciones_bp.route("/ver_ubicaciones")
def listado_ubicaciones():

    df = pd.read_excel(
        ARCHIVO_UBICACIONES
    )

    html = """
    <h1>Ubicaciones</h1>

    <a href="/admin">
    Volver
    </a>

    <hr>
    """

    for _, fila in df.iterrows():

        ubicacion = fila["Ubicación"]
        sububicacion = fila["Sububicación"]

        html += f"""
        <p>

        <a href="/ver_sububicacion/{ubicacion}/{sububicacion}">

        {ubicacion}
        >
        {sububicacion}

        </a>

        </p>
        """

    return html




@ubicaciones_bp.route(
    "/ver_sububicacion/<ubicacion>/<sububicacion>"
)
def ver_sububicacion(
        ubicacion,
        sububicacion):

    inventario = pd.read_excel(
        ARCHIVO_INVENTARIO
    )

    catalogo = pd.read_excel(
        ARCHIVO_EXCEL
    )

    try:

        contenido_cajas = pd.read_excel(
            ARCHIVO_CONTENIDO_CAJAS
        )

    except:

        contenido_cajas = pd.DataFrame(
            columns=[
                "CajaID",
                "Numero"
            ]
        )

    try:

        cajas = pd.read_excel(
            ARCHIVO_CAJAS
        )

    except:

        cajas = pd.DataFrame()

    try:

        ubicacion_cajas = pd.read_excel(
            ARCHIVO_UBICACION_CAJAS
        )

    except:

        ubicacion_cajas = pd.DataFrame(
            columns=[
                "CajaID",
                "Ubicacion",
                "Sububicacion"
            ]
        )

    html = f"""
    <h1>

    {ubicacion}
    >
    {sububicacion}

    </h1>

    <a href="/ver_ubicaciones">

    Volver

    </a>

    <hr>
    """

    articulos = inventario[
        (
            inventario["Ubicación"]
            == ubicacion
        )
        &
        (
            inventario["Sububicación"]
            == sububicacion
        )
    ]

    numeros_en_caja = set(
        contenido_cajas["Numero"]
    )

    articulos_sueltos = []

    for _, fila in articulos.iterrows():

        numero = fila["Número"]

        if numero in numeros_en_caja:

            continue

        art = catalogo[
            catalogo["Número"]
            == numero
        ]

        if len(art) > 0:

            articulos_sueltos.append(
                art.iloc[0]
            )

    html += f"""
    <h2>

    Artículos sueltos
    ({len(articulos_sueltos)})

    </h2>
    """

    for art in articulos_sueltos:

        html += f"""
        <p>

        <a href="/articulo/{art['Número']}">

        {art['Marca']}
        -
        {art['Referencia']}

        </a>

        </p>
        """

    html += """
    <hr>

    <h2>

    Cajas

    </h2>
    """

    total_articulos_cajas = 0
    total_cajas = 0

    for _, fila in ubicacion_cajas.iterrows():

        if (
            str(fila["Ubicacion"]).strip()
            == str(ubicacion).strip()
            and
            str(fila["Sububicacion"]).strip()
            == str(sububicacion).strip()
        ):

            caja_id = fila["CajaID"]

            caja = cajas[
                cajas["CajaID"]
                == caja_id
            ]

            if len(caja) == 0:

                continue

            caja = caja.iloc[0]

            ocupados = len(
                contenido_cajas[
                    contenido_cajas["CajaID"]
                    == caja_id
                ]
            )

            total_articulos_cajas += ocupados
            total_cajas += 1

            html += f"""
            <p>

            <a href="/caja/{caja_id}">

            📦 {caja['Nombre']}

            </a>

            <br>

            Artículos:
            {ocupados}

            </p>

            <hr>
            """

    total_general = (
        len(articulos_sueltos)
        + total_articulos_cajas
    )

    html += f"""
    <hr>

    <h2>

    Resumen

    </h2>

    <p>

    Cajas:
    {total_cajas}

    </p>

    <p>

    Artículos en cajas:
    {total_articulos_cajas}

    </p>

    <p>

    Artículos sueltos:
    {len(articulos_sueltos)}

    </p>

    <p>

    Total artículos:
    {total_general}

    </p>
    """

    return html
@ubicaciones_bp.route("/ubicacion/<ubicacion>")
def ver_ubicacion(ubicacion):

    inventario = pd.read_excel(ARCHIVO_INVENTARIO)
    catalogo = pd.read_excel(ARCHIVO_EXCEL)

    try:
        contenido_cajas = pd.read_excel(ARCHIVO_CONTENIDO_CAJAS)
    except:
        contenido_cajas = pd.DataFrame(columns=["CajaID", "Numero"])

    try:
        cajas = pd.read_excel(ARCHIVO_CAJAS)
    except:
        cajas = pd.DataFrame()

    df = inventario[inventario["Ubicación"] == ubicacion]

    subgrupos = df["Sububicación"].dropna().unique()

    resumen = []

    total_articulos = len(df)
    total_cajas = 0
    total_sueltos = 0

    for sub in subgrupos:

        df_sub = df[df["Sububicación"] == sub]

        numeros = set(df_sub["Número"])

        en_caja = set(contenido_cajas["Numero"])

        sueltos = numeros - en_caja
        en_cajas_sub = contenido_cajas[
            contenido_cajas["Numero"].isin(numeros)
        ]

        cajas_unicas = en_cajas_sub["CajaID"].nunique()

        total_cajas += cajas_unicas
        total_sueltos += len(sueltos)

        # 🔥 nivel de carga
        if len(numeros) == 0:
            nivel = "verde"
        else:
            ratio = len(sueltos) / len(numeros)

            if ratio > 0.7:
                nivel = "verde"
            elif ratio > 0.3:
                nivel = "amarillo"
            else:
                nivel = "rojo"

        resumen.append({
            "sub": sub,
            "total": len(numeros),
            "sueltos": len(sueltos),
            "cajas": cajas_unicas,
            "nivel": nivel
        })

    return render_template(
        "pages/ubicaciones/detalle.html",
        ubicacion=ubicacion,
        resumen=resumen,
        total_articulos=total_articulos,
        total_cajas=total_cajas,
        total_sueltos=total_sueltos
    )
