import requests, os, re
from datetime import datetime
from bs4 import BeautifulSoup
from fpdf import FPDF

# Fallback por si la API falla
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

H2H_DB = {
    "Osasuna-Rayo Vallecano": "32 PJ: 13 Osasuna, 10 Rayo, 9 X (38-38). En Sadar 8-2-3",
    "Sevilla-Barcelona": "203 PJ: 118 Barca, 39 X, 46 Sevilla. En Pizjuan 39-25-38",
}

def get_partidos_lae():
    """Intenta sacar la jornada actual de loteriasyapuestas.es"""
    try:
        # API pública que usa la web de Loterías
        url = "https://www.loteriasyapuestas.es/es/la-quiniela"
        r = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")
        # Busca textos tipo "Osasuna - Rayo"
        texto = soup.get_text()
        # Esto es heurístico, si no encuentra nada devuelve fallback
        partidos = re.findall(r"([A-Za-z\.\s\(\)]+)\s*-\s*([A-Za-z\.\s\(\)]+)", texto)
        limpios = []
        for a,b in partidos:
            a=a.strip(); b=b.strip()
            if len(a)>3 and len(b)>3 and len(limpios)<15:
                if "Quiniela" not in a and "Jornada" not in a:
                    limpios.append((a,b))
        if len(limpios) >= 14:
            print(f"Partidos detectados web: {limpios[:15]}")
            return limpios[:15]
    except Exception as e:
        print(f"Fallo scraping LAE: {e}")

    print("Usando PARTIDOS_FALLBACK")
    return PARTIDOS_FALLBACK

def generar():
    partidos = get_partidos_lae()
    fecha = datetime.now().strftime("%Y-%m-%d")
    md = f"# Informe H2H Quiniela {fecha}\n\n_Generado lunes/viernes auto_\n\n"
    
    for loc, vis in partidos:
        key = f"{loc}-{vis}"
        dato = H2H_DB.get(key, "H2H en construccion - se ampliara con scraper FootyStats")
        md += f"### {loc} - {vis}\n- **Historico:** {dato}\n\n"
    
    os.makedirs("informes", exist_ok=True)
    path_md = f"informes/informe_{fecha}.md"
    open(path_md,"w",encoding="utf-8").write(md)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",14)
    pdf.cell(0,10,f"Informe H2H {fecha}",ln=True)
    pdf.set_font("Arial","",9)
    pdf.multi_cell(0,5,md)
    pdf.output(f"informes/informe_{fecha}.pdf")
    print(f"Generado {path_md}")

if __name__ == "__main__":
    generar()
