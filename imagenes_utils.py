import os


def existe_imagen(referencia):

    extensiones = [
        ".jpg",
        ".jpeg",
        ".png",
        ".JPG",
        ".JPEG",
        ".PNG"
    ]

    for ext in extensiones:

        ruta = os.path.join(
            "imagenes",
            f"{referencia}{ext}"
        )

        if os.path.exists(ruta):

            return True

    return False
