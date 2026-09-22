import os, re, requests
from datetime import datetime
from fpdf import FPDF
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_proxima_jornada():
    """Saca la proxima quiniela de la web oficial y de respaldo"""
    partidos = []
    try:
        # Fuente 1: Loterias oficial - mas fiable
        r = requests.get("https://www.loteriasyapuestas.es/es/la-quiniela", headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, "lxml")
        # Los partidos estan en <li> o <div> con guion
        for li in soup.find_all(string=re.compile(r"-")):
            txt = li.strip()
            if " - " in txt and len(txt) < 50 and "Quiniela" not in txt:
                if "null" in txt.lower(): continue
                partes = txt.split(" - ")
                if len(partes)==2 and len(partes[0])>2:
                    partidos.append((partes[0].strip().title(), partes[1].strip().title()))
            if len(partidos)>=15: break

        # Fuente 2: Eduardo Losilla si falla la 1
        if len(partidos) < 10:
            r2 = requests.get("https://www.eduardolosilla.es/quiniela", headers=HEADERS, timeout=20)
            txt2 = r2.text
            # Patrón: 1 OSASUNA - RAYO
            encontrados = re.findall(r"\d+\s+([A-ZÁÉÍÓÚÑ\s\(\)\.]{4,})\s*-\s*([A-ZÁÉÍÓÚÑ\s\(\)\.]{4,})", txt2)
            partidos = []
            for a,b in encontrados:
                a=a.strip().title(); b=b.strip().title()
                if a.lower()=="null" or b.lower()=="null": continue
                if len(a)<3 or len(b)<3: continue
                if "Bote" in a or "Quiniela" in a: continue
                if (a,b) not in partidos:
                    partidos.append((a,b))
                if len(partidos)>=15: break

    except Exception as e:
        print(f"Error: {e}")

    return partidos[:15]

def generar_informe(partidos):
    fecha = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("informes", exist_ok=True)

    # 1. MD
    md = f"# Quiniela - Jornada del {fecha}\n\n"
    md += f"Total partidos: {len(partidos)}\n\n"
    for i,(l,v) in enumerate(partidos,1):
        pleno = " (PLENO 15)" if i==15 else ""
        md += f"**{i}.** {l} - {v}{pleno}\n"
    with open(f"informes/informe_{fecha}.md","w",encoding="utf-8") as f:
        f.write(md)

    # 2. PDF simple y limpio (sin caracteres raros)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",16)
    pdf.cell(0,12,f"QUINIELA - {fecha}",0,1,'C')
    pdf.set_font("Arial","",11)
    pdf.cell(0,8,f"Jornada detectada automaticamente - {len(partidos)} partidos",0,1,'C')
    pdf.ln(8)

    pdf.set_font("Arial","B",11)
    pdf.set_fill_color(230,230,230)
    pdf.cell(15,10,"N",1,0,'C',True)
    pdf.cell(80,10,"LOCAL",1,0,'C',True)
    pdf.cell(80,10,"VISITANTE",1,1,'C',True)

    pdf.set_font("Arial","",11)
    for i,(loc,vis) in enumerate(partidos,1):
        # Limpia tildes raras para FPDF
        loc_c = loc.encode('latin-1','ignore').decode('latin-1')
        vis_c = vis.encode('latin-1','ignore').decode('latin-1')
        pdf.cell(15,9,str(i),1,0,'C')
        pdf.cell(80,9,loc_c,1,0,'C')
        pdf.cell(80,9,vis_c,1,1,'C')

    out = f"informes/informe_{fecha}.pdf"
    pdf.output(out)
    print(f"OK -> {out}")
    print(partidos)

if __name__ == "__main__":
    partidos = get_proxima_jornada()
    generar_informe(partidos)
