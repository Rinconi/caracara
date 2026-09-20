import requests, os, time, re
from datetime import datetime
from bs4 import BeautifulSoup
from fpdf import FPDF

HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124"}

PARTIDOS_FALLBACK = [
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

def slugify(team):
    team = team.lower().replace("(f)","").replace("(F)","").strip()
    team = team.replace(" ", "-").replace("ñ","n")
    return re.sub(r'[^a-z0-9-]', '', team)

def fetch_h2h_footystats(local, visitante):
    """Intenta FootyStats: /es/club/local-vs-visitante-h2h"""
    try:
        s1 = slugify(local)
        s2 = slugify(visitante)
        urls = [
            f"https://footystats.org/es/club/{s1}-vs-{s2}-h2h",
            f"https://footystats.org/clubs/{s1}-vs-{s2}-h2h",
        ]
        for url in urls:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200 and "Head to Head" in r.text:
                soup = BeautifulSoup(r.text, "lxml")
                # Busca el bloque de stats
                text = soup.get_text()
                m = re.search(r'(\d+)\s*Matches.*?(\d+)\s*Wins.*?(\d+)\s*Draws', text, re.S)
                if m:
                    return f"{m.group(1)} partidos - H2H {url}"
                # Fallback: devuelve primeros 200 chars del resumen
                resumen = soup.find("div", class_="h2h")
                if resumen:
                    return resumen.get_text(strip=True)[:200]
                return f"Datos H2H encontrados en {url}"
            time.sleep(1)
    except Exception as e:
        print(f"FootyStats fallo {local}-{visitante}: {e}")
    return None

def fetch_h2h_aiscore(local, visitante):
    """Fallback AiScore search"""
    try:
        url = f"https://www.aiscore.com/es/search?q={local} {visitante}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")
            # AiScore lista historial
            h2h = soup.find(string=re.compile("enfrentaron|jugaron"))
            if h2h:
                return h2h.strip()[:300]
    except Exception as e:
        print(f"AiScore fallo {e}")
    return None

def get_h2h_completo(local, visitante):
    # Orden: FootyStats -> AiScore -> fallback curado
    data = fetch_h2h_footystats(local, visitante)
    if data:
        return data + " [FootyStats]"

    data = fetch_h2h_aiscore(local, visitante)
    if data:
        return data + " [AiScore]"

    # Fallback curado que ya tenemos
    curados = {
        "osasuna-rayo-vallecano": "32 PJ: 13 Osasuna, 10 Rayo, 9 X (38-38). Ult: 1-3,2-0,1-1",
        "sevilla-barcelona": "203 PJ: 118 Barca, 39 X, 46 Sevilla. En Pizjuan 39-25-38. Ult: Sevilla 4-1 (05/10/25)",
    }
    key = f"{slugify(local)}-{slugify(visitante)}"
    return curados.get(key, "H2H en construccion - sin bloqueo anti-bot")

def get_partidos():
    # Aqui puedes dejar tu logica de loterias que ya te pase
    # Para simplificar usamos fallback por ahora
    return PARTIDOS_FALLBACK

def generar():
    partidos = get_partidos()
    fecha = datetime.now().strftime("%Y-%m-%d")
    md = f"# Informe H2H Caracara - {fecha}\n\n"

    for i,(loc, vis) in enumerate(partidos,1):
        print(f"[{i}/15] {loc} vs {vis}...")
        h2h = get_h2h_completo(loc, vis)
        md += f"### {i}. {loc} - {vis}\n"
        md += f"- **Historico:** {h2h}\n"
        md += f"- **Ultimos 5:** (ver detalle en web)\n\n"
        time.sleep(1.5) # para no ser baneado

    os.makedirs("informes", exist_ok=True)
    open(f"informes/informe_{fecha}.md","w",encoding="utf-8").write(md)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",12)
    pdf.cell(0,10,f"Informe H2H {fecha}",ln=True)
    pdf.set_font("Arial","",8)
    pdf.multi_cell(0,4,md)
    pdf.output(f"informes/informe_{fecha}.pdf")
    print("Informe generado")

if __name__ == "__main__":
    generar()
