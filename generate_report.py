import os
import time
from datetime import datetime
from pathlib import Path

import requests
from fpdf import FPDF


# La Quiniela no dispone de un endpoint JSON oficial, público y documentado.
# Configura una fuente de terceros que devuelva la próxima jornada:
#   QUINIELA_API_URL=https://.../quiniela
#
# API-Football se utiliza para resolver los equipos y consultar el H2H:
#   API_FOOTBALL_KEY=...
#   API_FOOTBALL_LEAGUE=140       # LaLiga; cambia si tu proveedor usa otro ID
#   API_FOOTBALL_SEASON=2026      # opcional; por defecto el año actual
QUINIELA_API_URL = os.getenv("QUINIELA_API_URL")
FOOTBALL_API_URL = "https://v3.football.api-sports.io"
FOOTBALL_API_KEY = os.getenv("API_FOOTBALL_KEY")
FOOTBALL_LEAGUE = os.getenv("API_FOOTBALL_LEAGUE", "140")
FOOTBALL_SEASON = os.getenv("API_FOOTBALL_SEASON", str(datetime.now().year))

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "caracara/1.0"})


class QuinielaError(RuntimeError):
    pass


class FootballApiError(RuntimeError):
    pass


def obtener_json(url, headers=None, params=None):
    respuesta = SESSION.get(url, headers=headers, params=params, timeout=25)
    respuesta.raise_for_status()
    datos = respuesta.json()
    if isinstance(datos, dict) and datos.get("error"):
        raise RuntimeError(datos["error"])
    return datos


def extraer_partidos_quiniela(datos):
    """Normaliza respuestas habituales de APIs de Quiniela.

    Se aceptan, entre otros, estos formatos:
      {"partidos": [{"numero": 1, "local": "...", "visitante": "..."}]}
      {"matches": [{"home": "...", "away": "..."}]}
      [{"homeTeam": "...", "awayTeam": "..."}]
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

        # Algunas APIs devuelven {team: {name: ...}}.
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


def football_api(endpoint, params):
    if not FOOTBALL_API_KEY:
        raise FootballApiError("Falta la variable API_FOOTBALL_KEY")

    datos = obtener_json(
        f"{FOOTBALL_API_URL}/{endpoint}",
        headers={"x-apisports-key": FOOTBALL_API_KEY},
        params=params,
    )

    if isinstance(datos, dict) and datos.get("errors"):
        raise FootballApiError(str(datos["errors"]))
    return datos.get("response", [])


def buscar_equipo(nombre):
    """Busca el ID de API-Football sin depender de slugs o de scraping HTML."""
    resultados = football_api("teams", {"search": nombre})
    if not resultados:
        raise FootballApiError(f"No se encontró el equipo: {nombre}")

    # La primera coincidencia suele ser correcta; se conserva el nombre devuelto
    # para que el informe muestre cómo lo interpreta el proveedor.
    equipo = resultados[0]["team"]
    return equipo["id"], equipo["name"]


def obtener_h2h(local, visitante, ultimos=10):
    local_id, local_api = buscar_equipo(local)
    visitante_id, visitante_api = buscar_equipo(visitante)

    encuentros = football_api(
        "fixtures/headtohead",
        {"h2h": f"{local_id}-{visitante_id}", "last": ultimos},
    )

    resumen = {
        "local_api": local_api,
        "visitante_api": visitante_api,
        "partidos": [],
        "local_gana": 0,
        "empates": 0,
        "visitante_gana": 0,
    }

    for encuentro in encuentros:
        goles = encuentro.get("goals", {})
        goles_local = goles.get("home")
        goles_visitante = goles.get("away")
        if goles_local is None or goles_visitante is None:
            continue

        equipo_local_id = encuentro["teams"]["home"]["id"]
        ganador = encuentro["teams"].get("winner")
        if goles_local == goles_visitante:
            resumen["empates"] += 1
        elif ganador == (equipo_local_id == local_id):
            # winner=True significa que ganó el equipo que aparece como local.
            if equipo_local_id == local_id:
                resumen["local_gana"] += 1
            else:
                resumen["visitante_gana"] += 1
        elif equipo_local_id == local_id:
            resumen["visitante_gana"] += 1
        else:
            resumen["local_gana"] += 1

        fecha = encuentro.get("fixture", {}).get("date", "")[:10]
        resumen["partidos"].append(
            f"{fecha}: {encuentro['teams']['home']['name']} "
            f"{goles_local}-{goles_visitante} "
            f"{encuentro['teams']['away']['name']}"
        )

    return resumen


def construir_informe(partidos):
    fecha = datetime.now().strftime("%Y-%m-%d")
    lineas = [f"# Informe H2H de La Quiniela - {fecha}", ""]

    for partido in partidos:
        local = partido["local"]
        visitante = partido["visitante"]
        numero = partido["numero"]
        print(f"[{numero}/15] {local} vs {visitante}...")
        lineas.extend([f"## {numero}. {local} - {visitante}", ""])

        try:
            h2h = obtener_h2h(local, visitante)
            lineas.extend([
                f"- Equipos identificados: {h2h['local_api']} - {h2h['visitante_api']}",
                f"- Partidos analizados: {len(h2h['partidos'])}",
                f"- Victorias de {local}: {h2h['local_gana']}",
                f"- Empates: {h2h['empates']}",
                f"- Victorias de {visitante}: {h2h['visitante_gana']}",
                "",
                "### Últimos enfrentamientos",
                "",
            ])
            lineas.extend(f"- {partido}" for partido in h2h["partidos"])
            if not h2h["partidos"]:
                lineas.append("- No hay H2H disponible.")
        except (FootballApiError, requests.RequestException, KeyError) as error:
            lineas.append(f"- Error obteniendo H2H: {error}")

        lineas.append("")
        time.sleep(0.25)

    return "\n".join(lineas)


def guardar_informe(contenido):
    fecha = datetime.now().strftime("%Y-%m-%d")
    carpeta = Path("informes")
    carpeta.mkdir(exist_ok=True)

    ruta_md = carpeta / f"informe_{fecha}.md"
    ruta_md.write_text(contenido, encoding="utf-8")

    # fpdf2 necesita una fuente TTF Unicode para ñ y acentos.
    ruta_fuente = Path("fonts/DejaVuSans.ttf")
    ruta_pdf = carpeta / f"informe_{fecha}.pdf"
    pdf = FPDF()
    pdf.add_page()
    if ruta_fuente.exists():
        pdf.add_font("DejaVu", "", str(ruta_fuente))
        pdf.set_font("DejaVu", size=9)
    else:
        # El Markdown siempre se genera; el PDF requiere la fuente indicada.
        raise RuntimeError(
            "Falta fonts/DejaVuSans.ttf. Descárgala o elimina la generación PDF."
        )
    pdf.multi_cell(0, 5, contenido)
    pdf.output(str(ruta_pdf))
    return ruta_md, ruta_pdf


def generar():
    partidos = obtener_proxima_quiniela()
    informe = construir_informe(partidos)
    rutas = guardar_informe(informe)
    print(f"Informe generado: {rutas[0]} y {rutas[1]}")


if __name__ == "__main__":
    generar()
