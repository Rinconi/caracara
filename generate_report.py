import os
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from fpdf import FPDF

LOSILLA_URL = os.getenv(
    "LOSILLA_URL",
    "https://www.eduardolosilla.es/quiniela/boletos/",
)
OUTPUT_DIR = Path(os.getenv("INFORMES_DIR", "informes"))

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (compatible; caracara/1.0; +https://github.com/Rinconi/caracara)"
        ),
        "Accept-Language": "es-ES,es;q=0.9",
    }
)


class QuinielaError(RuntimeError):
    pass


def limpiar_texto(valor):
    return re.sub(r"\s+", " ", str(valor or "")).strip(" -–—")


def _partido_desde_texto(texto, numero_predeterminado=None):
    """Extrae número, local y visitante de una línea de Losilla."""
    texto = limpiar_texto(texto)
    if not texto:
        return None

    # El número puede aparecer como "1.", "1 -" o simplemente "1".
    patron = re.match(r"^(?P<num>\d{1,2})\s*[.)\-:]?\s+(?P<resto>.+)$", texto)
    if patron:
        numero = int(patron.group("num"))
        resto = patron.group("resto")
    else:
        numero = numero_predeterminado
        resto = texto

    # La web suele separar los equipos con "-", "–" o "—". No se usa
    # split('-') porque algunos nombres pueden contener guiones.
    equipos = re.split(r"\s+[–—-]\s+|\s{2,}", resto, maxsplit=1)
    if len(equipos) != 2:
        return None

    local = limpiar_texto(equipos[0])
    visitante = limpiar_texto(re.sub(r"\s+(?:SAB|DOM|VIE|LUN)\b.*$", "", equipos[1], flags=re.I))
    if not local or not visitante or not re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", local + visitante):
        return None

    return {"numero": numero, "local": local, "visitante": visitante}


def extraer_partidos_quiniela_html(html):
    """Extrae los 15 partidos del boleto visible en la web de Eduardo Losilla."""
    soup = BeautifulSoup(html, "html.parser")
    candidatos = []

    # Primero probamos los contenedores habituales; después las filas de tabla.
    selectores = (
        ".boleto-jornada .boleto-partido",
        ".boleto-partido",
        "table.boleto tbody tr",
        "table.boletos tbody tr",
        "table tbody tr",
    )
    for selector in selectores:
        elementos = soup.select(selector)
        if not elementos:
            continue
        candidatos = [elemento.get_text(" ", strip=True) for elemento in elementos]
        partidos = [
            partido
            for indice, texto in enumerate(candidatos, 1)
            if (partido := _partido_desde_texto(texto, indice)) is not None
        ]
        if len(partidos) >= 15:
            return _normalizar_partidos(partidos[:15])

    # Fallback para cambios menores de HTML: examina líneas del contenido.
    texto = soup.get_text("\n", strip=True)
    partidos = []
    for linea in texto.splitlines():
        partido = _partido_desde_texto(linea)
        if partido and 1 <= (partido["numero"] or 0) <= 15:
            partidos.append(partido)

    partidos = _normalizar_partidos(partidos)
    if len(partidos) != 15:
        raise QuinielaError(
            f"No se encontraron 15 partidos en {LOSILLA_URL} (encontrados: {len(partidos)})"
        )
    return partidos


def _normalizar_partidos(partidos):
    resultado = []
    vistos = set()
    for indice, partido in enumerate(partidos, 1):
        clave = (partido["local"].casefold(), partido["visitante"].casefold())
        if clave in vistos:
            continue
        vistos.add(clave)
        partido = dict(partido)
        partido["numero"] = partido["numero"] or indice
        resultado.append(partido)
    return resultado


def obtener_proxima_quiniela():
    respuesta = SESSION.get(LOSILLA_URL, timeout=25)
    respuesta.raise_for_status()
    return extraer_partidos_quiniela_html(respuesta.text)


def _fuente_font():
    """Devuelve una fuente con soporte para tildes en GitHub Actions/Linux."""
    for ruta in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ):
        if Path(ruta).exists():
            return ruta
    return None


def generar_pdf(partidos, destino):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    fuente = _fuente_font()
    if fuente:
        pdf.add_font("Informe", "", fuente)
        pdf.set_font("Informe", size=16)
    else:
        pdf.set_font("Helvetica", size=16)

    pdf.cell(0, 10, "Informe de la próxima Quiniela", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Informe" if fuente else "Helvetica", size=9)
    pdf.cell(
        0,
        7,
        f"Generado: {datetime.now():%d/%m/%Y %H:%M} | Fuente: Eduardo Losilla",
        new_x="LMARGIN",
        new_y="NEXT",
        align="C",
    )
    pdf.ln(5)

    pdf.set_fill_color(35, 75, 120)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Informe" if fuente else "Helvetica", size=10)
    pdf.cell(18, 9, "Nº", border=1, fill=True, align="C")
    pdf.cell(78, 9, "Local", border=1, fill=True)
    pdf.cell(78, 9, "Visitante", border=1, fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    for indice, partido in enumerate(partidos, 1):
        if indice % 2 == 0:
            pdf.set_fill_color(235, 242, 248)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.cell(18, 9, str(partido["numero"]), border=1, fill=True, align="C")
        pdf.cell(78, 9, partido["local"], border=1, fill=True)
        pdf.cell(78, 9, partido["visitante"], border=1, fill=True)
        pdf.ln()

    pdf.ln(6)
    pdf.set_font("Informe" if fuente else "Helvetica", size=8)
    pdf.multi_cell(0, 5, f"Fuente consultada: {LOSILLA_URL}")
    pdf.output(str(destino))


def main():
    partidos = obtener_proxima_quiniela()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destino = OUTPUT_DIR / f"quiniela_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    generar_pdf(partidos, destino)
    print(f"Informe PDF generado: {destino}")
    for partido in partidos:
        print(f"{partido['numero']}. {partido['local']} vs {partido['visitante']}")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as error:
        print(f"Error al consultar Eduardo Losilla: {error}")
    except Exception as error:
        print(f"Error: {error}")
