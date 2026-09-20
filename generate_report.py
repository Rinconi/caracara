import requests, os
from datetime import datetime
from fpdf import FPDF

PARTIDOS = [
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
    "Osasuna-Rayo Vallecano": "32 PJ: 13 Osasuna, 10 Rayo, 9 X (38-38). Ultimos: 1-3,2-0,1-1,3-1,2-1",
    "Sevilla-Barcelona": "203 PJ: 118 Barca,39 X,46 Sevilla. En Pizjuan 39-25-38. Ultimo: Sevilla 4-1 (05/10/25)",
}

def generar():
    fecha = datetime.now().strftime("%Y-%m-%d")
    md = f"# Informe H2H {fecha}\n\n"
    for loc, vis in PARTIDOS:
        key = f"{loc}-{vis}"
        dato = H2H_DB.get(key, "En construccion - se scrapea en vivo")
        md += f"### {loc} - {vis}\n- {dato}\n\n"
    
    os.makedirs("informes", exist_ok=True)
    open(f"informes/informe_{fecha}.md","w",encoding="utf-8").write(md)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",14)
    pdf.cell(0,10,f"Informe H2H {fecha}",ln=True)
    pdf.set_font("Arial","",10)
    pdf.multi_cell(0,6,md)
    pdf.output(f"informes/informe_{fecha}.pdf")

if __name__ == "__main__":
    generar()
