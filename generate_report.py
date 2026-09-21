import os
import requests

QUINIELA_API_URL = os.getenv("QUINIELA_API_URL")

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "caracara/1.0"})


class QuinielaError(RuntimeError):
    pass


def obtener_json(url, headers=None, params=None):
    respuesta = SESSION.get(url, headers=headers, params=params, timeout=25)
    respuesta.raise_for_status()
    datos = respuesta.json()

    if isinstance(datos, dict) and datos.get("error"):
        raise RuntimeError(datos["error"])

    return datos


def extraer_partidos_quiniela(datos):
    """
    Normaliza respuestas habituales de APIs de Quiniela.

    Acepta formatos como:
      {"partidos": [{"numero": 1, "local": "X", "visitante": "Y"}]}
      {"matches": [{"home": "X", "away": "Y"}]}
      [{"homeTeam": "X", "awayTeam": "Y"}]
    """
    if isinstance(datos, list):
        candidatos = datos
    elif isinstance(datos, dict):
        candidatos = None
        for clave in ("partidos", "matches", "fixtures", "games", "data"):
            valor = datos.get(clave)
            if isinstance(valor, list):
                candidatos = valor
                break

        if candidatos is None:
            raise QuinielaError("La respuesta no contiene una lista de partidos")
    else:
        raise QuinielaError("Formato JSON de Quiniela no reconocido")

    partidos = []
    for indice, partido in enumerate(candidatos, 1):
        if not isinstance(partido, dict):
            continue

        local = partido.get("local") or partido.get("home") or partido.get("homeTeam")
        visitante = (
            partido.get("visitante")
            or partido.get("away")
            or partido.get("awayTeam")
        )

        # Algunos proveedores devuelven {team: {name: "..."}}
        if isinstance(local, dict):
            local = local.get("name")
        if isinstance(visitante, dict):
            visitante = visitante.get("name")

        if local and visitante:
            numero = partido.get("numero") or partido.get("num") or indice
            partidos.append({
                "numero": numero,
                "local": str(local).strip(),
                "visitante": str(visitante).strip(),
            })

    if len(partidos) != 15:
        raise QuinielaError(
            f"La API devolvió {len(partidos)} partidos válidos; se esperaban 15"
        )

    return partidos


def obtener_proxima_quiniela():
    if not QUINIELA_API_URL:
        raise QuinielaError(
            "Falta QUINIELA_API_URL. Configura una API de terceros que publique "
            "los 15 partidos de la próxima Quiniela."
        )

    datos = obtener_json(QUINIELA_API_URL)
    return extraer_partidos_quiniela(datos)


if __name__ == "__main__":
    try:
        partidos = obtener_proxima_quiniela()

        for partido in partidos:
            print(f"{partido['numero']}. {partido['local']} vs {partido['visitante']}")

    except Exception as e:
        print(f"Error: {e}")
