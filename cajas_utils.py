import pandas as pd
from datos_utils import *

from config import (
    ARCHIVO_CAJAS,
    ARCHIVO_CONTENIDO_CAJAS,
    ARCHIVO_UBICACION_CAJAS
)


def obtener_caja(numero):

    try:

        contenido = pd.read_excel(
            ARCHIVO_CONTENIDO_CAJAS
        )

        cajas = pd.read_excel(
            ARCHIVO_CAJAS
        )

        fila = contenido[
            contenido["Numero"] == numero
        ]

        if len(fila) == 0:

            return "SIN CAJA"

        caja_id = fila.iloc[0]["CajaID"]

        caja = cajas[
            cajas["CajaID"] == caja_id
        ]

        if len(caja) == 0:

            return "SIN CAJA"

        return caja.iloc[0]["Nombre"]

    except:

        return "SIN CAJA"


def obtener_caja_id(numero):

    try:

        contenido = pd.read_excel(
            ARCHIVO_CONTENIDO_CAJAS
        )

        fila = contenido[
            contenido["Numero"] == numero
        ]

        if len(fila) == 0:

            return None

        return int(
            fila.iloc[0]["CajaID"]
        )

    except:

        return None



def obtener_ubicacion_caja(caja_id):

    try:

        df = pd.read_excel(
            ARCHIVO_UBICACION_CAJAS
        )

        fila = df[
            df["CajaID"] == caja_id
        ]

        if len(fila) == 0:

            return (
                "SIN UBICACION",
                ""
            )

        fila = fila.iloc[0]

        return (
            str(fila["Ubicacion"]),
            str(fila["Sububicacion"])
        )

    except:

        return (
            "SIN UBICACION",
            ""
        )


def guardar_ubicacion_caja(
        caja_id,
        ubicacion,
        sububicacion):

    try:

        df = pd.read_excel(
            ARCHIVO_UBICACION_CAJAS
        )

    except:

        df = pd.DataFrame(
            columns=[
                "CajaID",
                "Ubicacion",
                "Sububicacion"
            ]
        )

    existe = (
        df["CajaID"]
        == caja_id
    )

    if existe.any():

        df.loc[
            existe,
            "Ubicacion"
        ] = ubicacion

        df.loc[
            existe,
            "Sububicacion"
        ] = sububicacion

    else:

        nueva = pd.DataFrame(
            [{
                "CajaID": caja_id,
                "Ubicacion": ubicacion,
                "Sububicacion": sububicacion
            }]
        )

        df = pd.concat(
            [df, nueva],
            ignore_index=True
        )

    df.to_excel(
        ARCHIVO_UBICACION_CAJAS,
        index=False
    )

def obtener_ubicacion_articulo(numero):

    caja_id = obtener_caja_id(
        numero
    )

    if caja_id is None:

        return (
            "SIN CAJA",
            ""
        )

    return obtener_ubicacion_caja(
        caja_id
    )

def crear_caja(
    nombre,
    tipo,
    capacidad,
    ubicacion,
    sububicacion
):

    df = pd.read_excel(
        ARCHIVO_CAJAS
    )

    nuevo_id = (
        df["CajaID"].max() + 1
    )

    nueva_fila = pd.DataFrame([
        {
            "CajaID": nuevo_id,
            "Nombre": nombre,
            "Tipo": tipo,
            "Capacidad": capacidad,
            "Ubicación": ubicacion,
            "Sububicación": sububicacion
        }
    ])

    df = pd.concat(
        [df, nueva_fila],
        ignore_index=True
    )

    df.to_excel(
        ARCHIVO_CAJAS,
        index=False
    )

def eliminar_caja(caja_id):

    df = leer_excel_seguro(
        ARCHIVO_CAJAS,
        ["CajaID", "Caja"]
    )

    df = df[
        df["CajaID"] != caja_id
    ]

    df.to_excel(
        ARCHIVO_CAJAS,
        index=False
    )

    contenido = leer_excel_seguro(
        ARCHIVO_CONTENIDO_CAJAS,
        ["Número", "CajaID"]
    )

    contenido = contenido[
        contenido["CajaID"] != caja_id
    ]

    contenido.to_excel(
        ARCHIVO_CONTENIDO_CAJAS,
        index=False
    )

    ubicaciones = leer_excel_seguro(
        ARCHIVO_UBICACION_CAJAS,
        ["CajaID", "Ubicación", "Sububicación"]
    )

    ubicaciones = ubicaciones[
        ubicaciones["CajaID"] != caja_id
    ]

    ubicaciones.to_excel(
        ARCHIVO_UBICACION_CAJAS,
        index=False
    )
