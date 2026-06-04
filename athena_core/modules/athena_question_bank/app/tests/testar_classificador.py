from app.classificadores.classificador_competencias import classificar

casos = [
    "Paciente apresenta sepse grave com hipotensao persistente.",
    "Discussao sobre bioetica em cuidados paliativos.",
    "Estudo de incidencia e prevalencia da dengue.",
    "Gestante com hipertensao arterial.",
]

for caso in casos:
    print("-" * 80)
    print(caso)
    print(classificar(caso))
