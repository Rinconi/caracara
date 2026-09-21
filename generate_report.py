  import os, re, requests
from datetime import datetime
from fpdf import FPDF
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

H2H_CURADO = {
    "ceuta-r.sociedad b": "2 PJ: 1 Ceuta, 1 X, 0 R.Sociedad B (3-1 goles). Ult: 0-0 (10/04/26), 1-1 (21/12/25) [AiScore]",
    "ceuta-real sociedad b": "2 PJ: 1 Ceuta, 1 X, 0 R.Sociedad B (3-1 goles). Ult: 0-0 (10/04/26), 1-1 (21/12/25) [AiScore]",
    "granada-andorra fc": "5 PJ: 2 Granada, 2 X, 1 Andorra. Ult: 2-0 Granada (24/25)",
    "granada-andorra": "5 PJ: 2 Granada, 2 X, 1 Andorra",
    "osasuna-rayo vallecano": "32 PJ: 13 Osasuna, 10 Rayo, 9 X (38-38)",
    "sevilla-barcelona": "203 PJ: 118 Barca, 39 X, 46 Sevilla",
}

FALLBACK = [("Ceuta","R.Sociedad B"),("Granada","Andorra FC"),("Celta B","Sabadell"),
            ("Tenerife","Cadiz"),("Leganes","Granada"),("Osasuna","Rayo Vallecano"),
            ("Athletic Club","Alaves"),("Sevilla","Barcelona"),("Getafe","Malaga"),
            ("Deportivo","Betis"),("Villarreal","Levante"),("Valencia","Real Sociedad"),
            ("Andorra FC","Sporting Gijon"),("Castellon","Tenerife"),("At.Madrid","R.Madrid")]

def get_proximos_partidos():
    try:
        url = "https://www.eduardolosilla.es/quiniela"
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")
        text = soup.get_text(" ", strip=True)
        # Nuevo regex que IGNORA Null
        raw = re.findall(r"\b([A-ZÁÉÍÓÚÑa-z\.\s]{3,25})\s*-\s*([A-ZÁÉÍÓÚÑa-z\.\s]{3,25})", text)
        partidos = []
        for a,b in raw:
            a=a.strip(); b=b.strip()
            if a.lower()=="null" or b.lower()=="null": continue
            if len(a)<3 or len(b)<3: continue
            if any(x in a for x in ["Quiniela","Bote","Jornada"]): continue
            if len(partidos)<15:
                partidos.append((a.title(), b.title()))
        # Quita duplicados y deja 15
        uniq = []
        for p in partidos:
            if p not in uniq: uniq.append(p)
        if len(uniq) >= 10:
            print(f"Jornada detectada: {uniq[:15]}")
            return uniq[:15]
    except Exception as e:
        print(e)
    return FALLBACK

def get_h2h(loc, vis):
    key = f"{loc.lower()}-{vis.lower()}"
    for k,v in H2H_CURADO.items():
        if k in key or key in k:
            return v
    return "Historial corto / primera vez en esta categoria - consultar forma actual"

def generar():
    partidos = get_proximos_partidos()
    fecha = datetime.now().strftime("%Y-%m-%d")
    md = f"# Informe H2H Caracara - {fecha}\n\n_Jornada detectada automaticamente ({len(partidos)} partidos)_\n\n"
    for i,(loc,vis) in enumerate(partidos,1):
        md+=f"### {i}. {loc} - {vis}\n- **Historico:** {get_h2h(loc,vis)}\n\n"
    os.makedirs("informes", exist_ok=True)
    open(f"informes/informe_{fecha}.md","w",encoding="utf-8").write(md)
    pdf=FPDF(); pdf.add_page(); pdf.set_font("Arial","B",12)
    pdf.cell(0,10,f"Informe H2H Caracara {fecha}",ln=True)
    pdf.set_font("Arial","",9); pdf.multi_cell(0,5,md)
    pdf.output(f"informes/informe_{fecha}.pdf")
    print("OK")

if __name__=="__main__":
    generar()
