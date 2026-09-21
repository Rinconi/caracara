import os
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from fpdf import FPDF

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124"}

# BASE CURADA H2H - se actualiza cada jornada
H2H_CURADO = {
    "osasuna-rayo vallecano": "32 PJ: 13 Osasuna, 10 Rayo, 9 X (38-38). En El Sadar 8-2-3. Ult: 1-3,2-0,1-1,3-1,2-1 [FootyStats]",
    "athletic club-alaves": "27 PJ desde 2005: 10 Ath, 7 Alaves, 10 X (28-21). Ult: Ath 0-1 Alaves (13/09/25)",
    "sevilla-barcelona": "203 PJ: 118 Barca, 39 X, 46 Sevilla. En Pizjuan 39-25-38. Ult: Sevilla 4-1 Barca (05/10/25)",
    "getafe-malaga": "23 PJ: 11 Getafe, 6 X, 6 Malaga. En Coliseum 7-3-1",
    "deportivo-betis": "42 PJ: 18 Depor, 11 X, 13 Betis. En Riazor 14-5-2",
    "villarreal-levante": "Derbi 28 PJ: 14 Villarreal, 8 X, 6 Levante. En La Ceramica 9-3-2",
    "valencia-real sociedad": "162 PJ: 70 Valencia, 36 X, 56 Real. En Mestalla 53-17-11",
    "andorra fc-sporting gijon": "8 PJ: 3 Andorra, 2 X, 3 Sporting. Desde 2022",
    "castellon-tenerife": "26 PJ: 10 Castellon, 7 X, 9 Tenerife. En Castalia 7-4-2",
    "leganes-granada": "16 PJ: 6 Leganes, 5 X, 5 Granada. Ult: Granada 1-0 Leganes",
    "at.madrid(f)-logrono(f)": "Liga F 12 PJ: 10 Atleti Fem, 1 X, 1 Logroño",
    "eibar(f)-ath club(f)": "Derbi vasco Fem 18 PJ: 8 Athletic, 4 X, 6 Eibar",
    "r.madrid(f)-valencia(f)": "Liga F 22 PJ: 18 Real Madrid Fem, 2 X, 2 Valencia",
    "tenerife(f)-sevilla(f)": "Liga F 14 PJ: 5 Tenerife, 3 X, 6 Sevilla",
    "at.madrid-r.madrid": "Derbi 240 PJ: 61 Atleti, 57 X, 122 Real Madrid. En Metropolitano 2-1-0 ult 3",
}

FALLBACK = [
    ("Osasuna", "Rayo Vallecano"),
    ("Athletic Club", "Alaves"),
    ("Sevilla", "Barcelona"),
    ("Getafe", "Malaga"),
    ("Deportivo", "Betis"),
    ("Villarreal", "Levante"),
    ("Valencia", "Real Sociedad"),
    ("Andorra FC", "Sporting Gijon"),
    ("Castellon", "Tenerife"),
    ("Leganes", "Granada"),
    ("At.Madrid(F)", "Logrono(F)"),
    ("Eibar(F)", "Ath Club(F)"),
    ("R.Madrid(F)", "Valencia(F)"),
    ("Tenerife(F)", "Sevilla(F)"),
    ("At.Madrid", "R.Madrid"),
]

def get_proximos_partidos():
    try:
        # Fuente 1: eduardolosilla.es (no bloquea en Actions)
        url = "https://www.eduardolosilla.es/quiniela"
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")
        text = soup.get_text()
        # Busca lineas tipo "1 OSASUNA - RAYO"
        raw = re.findall(r"\d+\s+([A-ZÁÉÍÓÚÑ\.\s\(\)]+)\s*-\s*([A-ZÁÉÍÓÚÑ\.\s\(\)]+)", text.upper())
        partidos = []
        for a,b in raw:
            a = a.strip().title(); b = b.strip().title()
            if len(a)>2 and len(b)>2 and "Jornada" not in a and len(partidos)<15:
                # Limpia numeros raros
                if not any(x in a for x in ["Bote","Quiniela"]):
                    partidos.append((a,b))
        if len(partidos) >= 14:
            print(f"Partidos desde Losilla: {partidos[:15]}")
            return partidos[:15]
    except Exception as e:
        print(f"Error scraper Losilla: {e}")

    print("Usando FALLBACK")
    return FALLBACK

def get_h2h(local, visi):
    key = f"{local.lower()}-{visi.lower()}"
    key = key.replace(" ", " ").strip()
    return H2H_CURADO.get(key, "H2H en construccion - se actualizara con FootyStats")

def generar():
    partidos = get_proximos_partidos()
    fecha = datetime.now().strftime("%Y-%m-%d")
    md = f"# Informe H2H Caracara - {fecha}\n\n"
    md += f"_Jornada detectada automaticamente ({len(partidos)} partidos)_\n\n"

    for i, (loc, vis) in enumerate(partidos, 1):
        h2h = get_h2h(loc, vis)
        md += f"### {i}. {loc} - {vis}\n"
        md += f"- **Historico:** {h2h}\n\n"

    os.makedirs("informes", exist_ok=True)
    path_md = f"informes/informe_{fecha}.md"
    open(path_md, "w", encoding="utf-8").write(md)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Informe H2H Caracara {fecha}", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 5, md)
    pdf.output(f"informes/informe_{fecha}.pdf")
    print(f"Generado {path_md}")

if __name__ == "__main__":
    generar()
