import pandas as pd
from datetime import datetime
import os
from ubicaciones_utils import registrar_movimiento
from config import ARCHIVO_EXCEL,ARCHIVO_INVENTARIO

def leer_excel_seguro(ruta, columnas=None):

    try:
        return pd.read_excel(ruta)

    except:

        if columnas:
            return pd.DataFrame(columns=columnas)

        return pd.DataFrame()

def cargar_datos():
    return pd.read_excel(ARCHIVO_EXCEL)


def obtener_ubicacion(numero):

    try:

        df = pd.read_excel(ARCHIVO_INVENTARIO)

        fila = df[df["Número"] == numero]

        if len(fila) == 0:

            return (
                "SIN UBICACION",
                ""
            )

        fila = fila.iloc[0]

        return (
            str(fila["Ubicación"]),
            str(fila["Sububicación"])
        )

    except:

        return (
            "SIN UBICACION",
            ""
        )
def guardar_ubicacion(numero, ubicacion, sububicacion):
    ARCHIVO_MOVIMIENTOS = os.path.join(
        "datos",
        "movimientos.xlsx"
    )
    try:

        df = pd.read_excel(ARCHIVO_INVENTARIO)

    except:

        df = pd.DataFrame(
            columns=[
                "Número",
                "Ubicación",
                "Sububicación"
            ]
        )

    existe = df["Número"] == numero

    if existe.any():
        origen = (
            str(
                df.loc[
                    existe,
                    "Ubicación"
                ].iloc[0]
            )
            + " > "
            +
            str(
                df.loc[
                    existe,
                    "Sububicación"
                ].iloc[0]
            )
        )

        destino = (
            ubicacion
            + " > "
            + sububicacion
        )

        if origen != destino:
        
            registrar_movimiento(
                numero,
                origen,
                destino
            )

        df.loc[
            existe,
            "Ubicación"
        ] = ubicacion

        df.loc[
            existe,
            "Sububicación"
        ] = sububicacion

    else:

        nueva_fila = pd.DataFrame(
            [{
                "Número": numero,
                "Ubicación": ubicacion,
                "Sububicación": sububicacion
            }]
        )

        df = pd.concat(
            [df, nueva_fila],
            ignore_index=True
        )

    df.to_excel(
        ARCHIVO_INVENTARIO,
        index=False
    )

