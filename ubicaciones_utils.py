import pandas as pd
from datetime import datetime
from config import (
    ARCHIVO_INVENTARIO,
    ARCHIVO_MOVIMIENTOS
)
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


def registrar_movimiento(
        numero,
        origen,
        destino):

    try:

        df = pd.read_excel(
            ARCHIVO_MOVIMIENTOS
        )

    except:

        df = pd.DataFrame(
            columns=[
                "Número",
                "Fecha",
                "Origen",
                "Destino"
            ]
        )

    nueva_fila = pd.DataFrame([
        {
            "Número": numero,
            "Fecha":
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                ),
            "Origen": origen,
            "Destino": destino
        }
    ])

    df = pd.concat(
        [df, nueva_fila],
        ignore_index=True
    )

    df.to_excel(
        ARCHIVO_MOVIMIENTOS,
        index=False
    )

def resumen_ubicaciones():

    try:

        df = pd.read_excel(
            ARCHIVO_INVENTARIO
        )

        return (
            df["Ubicación"]
            .value_counts()
            .to_dict()
        )

    except:

        return {}

def ultimos_movimientos():

    try:

        df = pd.read_excel(
            ARCHIVO_MOVIMIENTOS
        )

        df = df.tail(10)

        return (
            df.iloc[::-1]
            .to_dict("records")
        )

    except:

        return []


    

    
