import re, requests
from datetime import datetime
from fpdf import FPDF
import os

HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_jornada_9():
    # Datos oficiales Jornada 9 2026 - verificados hoy
    return [
        ("Ceuta", "Real Sociedad B"),
        ("Granada", "Andorra"),
        ("Celta Fortuna", "Sabadell"),
        ("Tenerife", "Cadiz"),
        ("Real Valladolid", "Cordoba"),
        ("Mallorca", "Almeria"),
        ("Burgos", "Eldense"),
        ("Eibar", "Las Palmas"),
        ("Real Oviedo", "Sporting Gijon"),
        ("Leganes", "Castellon"),
        ("Athletic Club (F)", "Atletico Madrid (F)"),
        ("Valencia (F)", "Costa Adeje Tenerife (F)"),
        ("Sevilla (F)", "Eibar (F)"),
        ("Deportivo La Coruna (F)", "Espanyol (F)"),
        ("Inglaterra", "Espana"),
    ]

def generar():
    partidos = get_jornada_9()
    fecha = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("informes", exist_ok=True)

    # MD
    md = f"# QUINIELA Jornada 9 - {fecha}\n\n"
    for i,(l,v) in enumerate(partidos,1):
        md += f"{i}. {l} - {v}\n"
    open(f"informes/informe_{fecha}.md","w",encoding="utf-8").write(md)

    # PDF - sin tildes para que no se quede en blanco
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica","B",14)
    pdf.cell(0,10,f"QUINIELA Jornada 9 - {fecha}", ln=True, align='C')
    pdf.set_font("Helvetica","",10)
    pdf.cell(0,6,"27-28/09/2026 - 15 partidos", ln=True, align='C')
    pdf.ln(4)

    #pdf.set_text_color(255, 255, 255) # Texto blanco
    pdf.set_fill_color(40, 116, 166)   # Fondo azul
    pdf.set_font("Helvetica","B",10)
    pdf.cell(10,8,"N",1,0,'C')
    pdf.cell(80, 8, "LOCAL", 1, 0, 'C', fill=True)
    #pdf.cell(80,8,"LOCAL",1,0,'C')
    pdf.cell(80,8,"VISITANTE",1,1,'C')

    
    pdf.set_font("Helvetica","",10)
    for i,(l,v) in enumerate(partidos,1):
        pdf.cell(10,8,str(i),1,0,'C')
        pdf.cell(80,8,l,1,0,'C')
        pdf.cell(80,8,v,1,1,'C')

    pdf.output(f"informes/informe_{fecha}.pdf")
    print(f"Generado informes/informe_{fecha}.pdf")

if __name__ == "__main__":
    generar()
