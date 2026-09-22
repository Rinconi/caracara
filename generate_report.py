import os
from datetime import datetime
from fpdf import FPDF

def get_jornada_9():
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

H2H = {
    "Ceuta - Real Sociedad B": [
        {"fecha": "10/04/2026", "comp": "LaLiga2", "local": "R. Sociedad B", "visitante": "Ceuta", "res": "0-0"},
        {"fecha": "21/12/2025", "comp": "LaLiga2", "local": "Ceuta", "visitante": "R. Sociedad B", "res": "2-1"},
    ],
    "Granada - Andorra": [
        {"fecha": "17/10/2025", "comp": "LaLiga2", "local": "Andorra", "visitante": "Granada", "res": "0-0"},
        {"fecha": "28/01/2023", "comp": "LaLiga2", "local": "Granada", "visitante": "Andorra", "res": "2-0"},
        {"fecha": "04/09/2022", "comp": "LaLiga2", "local": "Andorra", "visitante": "Granada", "res": "1-0"},
    ],
    "Celta Fortuna - Sabadell": [
        {"fecha": "21/01/2024", "comp": "1a RFEF", "local": "Sabadell", "visitante": "Celta Fortuna", "res": "2-1"},
        {"fecha": "28/10/2023", "comp": "1a RFEF", "local": "Celta Fortuna", "visitante": "Sabadell", "res": "4-2"},
    ],
    "Tenerife - Cadiz": [
        {"fecha": "23/03/2025", "comp": "LaLiga2", "local": "Tenerife", "visitante": "Cadiz", "res": "2-1"},
        {"fecha": "31/08/2024", "comp": "LaLiga2", "local": "Cadiz", "visitante": "Tenerife", "res": "2-2"},
    ],
    "Real Valladolid - Cordoba": [
        {"fecha": "31/01/2026", "comp": "LaLiga2", "local": "Cordoba", "visitante": "Valladolid", "res": "3-1"},
        {"fecha": "30/08/2025", "comp": "LaLiga2", "local": "Valladolid", "visitante": "Cordoba", "res": "0-0"},
    ],
    "Mallorca - Almeria": [
        {"fecha": "17/08/2025", "comp": "LaLiga", "local": "Mallorca", "visitante": "Almeria", "res": "1-1"},
    ],
    "Burgos - Eldense": [
        {"fecha": "29/03/2025", "comp": "LaLiga2", "local": "Eldense", "visitante": "Burgos", "res": "0-0"},
        {"fecha": "08/12/2024", "comp": "LaLiga2", "local": "Burgos", "visitante": "Eldense", "res": "0-0"},
        {"fecha": "10/05/2024", "comp": "LaLiga2", "local": "Burgos", "visitante": "Eldense", "res": "1-2"},
    ],
    "Eibar - Las Palmas": [
        {"fecha": "29/03/2026", "comp": "LaLiga2", "local": "Eibar", "visitante": "Las Palmas", "res": "3-1"},
        {"fecha": "19/10/2025", "comp": "LaLiga2", "local": "Las Palmas", "visitante": "Eibar", "res": "3-1"},
    ],
    "Real Oviedo - Sporting Gijon": [
        {"fecha": "09/03/2025", "comp": "LaLiga2", "local": "Sporting", "visitante": "Oviedo", "res": "1-1"},
        {"fecha": "12/10/2024", "comp": "LaLiga2", "local": "Oviedo", "visitante": "Sporting", "res": "1-0"},
    ],
    "Leganes - Castellon": [
        {"fecha": "01/12/2024", "comp": "LaLiga2", "local": "Castellon", "visitante": "Leganes", "res": "0-2"},
    ],
    "Athletic Club (F) - Atletico Madrid (F)": [
        {"fecha": "11/05/2025", "comp": "Liga F", "local": "Athletic (F)", "visitante": "Atleti (F)", "res": "1-2"},
    ],
    "Valencia (F) - Costa Adeje Tenerife (F)": [
        {"fecha": "02/02/2025", "comp": "Liga F", "local": "Tenerife (F)", "visitante": "Valencia (F)", "res": "1-1"},
    ],
    "Sevilla (F) - Eibar (F)": [
        {"fecha": "23/03/2025", "comp": "Liga F", "local": "Eibar (F)", "visitante": "Sevilla (F)", "res": "0-2"},
    ],
    "Deportivo La Coruna (F) - Espanyol (F)": [
        {"fecha": "02/02/2025", "comp": "Liga F", "local": "Espanyol (F)", "visitante": "Depor (F)", "res": "2-0"},
    ],
     "Inglaterra - Espana": [
        {"fecha": "14/07/2024", "comp": "Euro", "local": "Espana", "visitante": "Inglaterra", "res": "2-1"},
        {"fecha": "15/10/2018", "comp": "Nations", "local": "Espana", "visitante": "Inglaterra", "res": "2-3"},
        {"fecha": "08/09/2018", "comp": "Nations", "local": "Inglaterra", "visitante": "Espana", "res": "1-2"},
        {"fecha": "12/11/2011", "comp": "Amistoso", "local": "Inglaterra", "visitante": "Espana", "res": "1-0"},
        {"fecha": "02/07/1996", "comp": "Euro", "local": "Inglaterra", "visitante": "Espana", "res": "0-0 (4-2 p)"},
    ],

}

def generar():
    partidos = get_jornada_9()
    fecha = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("informes", exist_ok=True)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    #titulo de quiniela
    pdf.add_page()
    pdf.set_font("Helvetica","B",14)
    pdf.cell(0,10,f"QUINIELA Jornada 9 - {fecha}", ln=True, align='C')
    pdf.ln(2)
    
    #cabecera de la tabla quiniela
    pdf.set_font("Helvetica","B",16)
    pdf.set_fill_color(0,0,0) #fondo negro
    pdf.set_text_color(255,255,255) #texto blanco
    pdf.cell(10,8,"N",1,0,'C', True)
    pdf.cell(80,8,"LOCAL",1,0,'C', True)
    pdf.cell(80,8,"VISITANTE",1,1,'C', True)
    #resto de la lista
    pdf.set_text_color(0,0,0)#volvemos a texto negro para el resto
    pdf.set_font("Helvetica","",14)
    for i,(l,v) in enumerate(partidos,1):
        pdf.cell(10,8,str(i),1,0,'C')
        pdf.cell(80,8,l,1,0,'C')
        pdf.cell(80,8,v,1,1,'C')
    #pagina 2 Historiales cara a cara
    pdf.add_page()
    pdf.set_font("Helvetica","B",14)
    pdf.cell(0,10,"HISTORIALES H2H - Jornada 9", ln=True, align='C')
    pdf.ln(3)

    for titulo, datos in H2H.items():
        if pdf.get_y() > 235:
            pdf.add_page()
        pdf.set_font("Helvetica","B",16)
        pdf.set_fill_color(200,200,200)
        pdf.cell(0,8,f" {titulo} ({len(datos)} PJ)",1,1,'C',True)
        pdf.set_font("Helvetica","B",12)
        pdf.set_fill_color(30,30,30)#fondo negro
        pdf.set_text_color(255,255,255)#texto blanco
        pdf.cell(22,7,"FECHA",1,0,'C',True)
        pdf.cell(28,7,"COMP",1,0,'C',True)
        pdf.cell(52,7,"LOCAL",1,0,'C',True)
        pdf.cell(52,7,"VISITANTE",1,0,'C',True)
        pdf.cell(24,7,"RES",1,1,'C',True)
        pdf.set_text_color(0,0,0)
        pdf.set_font("Helvetica","",10)
        for p in datos:
            pdf.cell(22,7,p["fecha"],1,0,'C')
            pdf.cell(24,7,p["comp"],1,0,'C')
            pdf.cell(52,7,p["local"],1,0,'C')
            pdf.cell(52,7,p["visitante"],1,0,'C')
            pdf.cell(24,7,p["res"],1,1,'C')
        pdf.ln(4)

    out = f"informes/informe_{fecha}.pdf"
    pdf.output(out)
    print(f"PDF generado: {out}")

# IMPORTANTE: esto hace que se genere al ejecutar
if __name__ == "__main__":
    generar()

# Para Jupyter - descomenta si estas en Colab/Jupyter
# generar()
