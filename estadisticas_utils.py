import pandas as pd
from config import ARCHIVO_EXCEL
from imagenes_utils import existe_imagen


def obtener_estadisticas():

    df = pd.read_excel(
        ARCHIVO_EXCEL
    )

    total = len(df)

    con_imagen = 0

    for _, fila in df.iterrows():

        referencia = str(
            fila["Referencia"]
        )

        if existe_imagen(
            referencia
        ):

            con_imagen += 1

    return {
        "total": total,
        "con_imagen": con_imagen,
        "sin_imagen": total - con_imagen
    }

