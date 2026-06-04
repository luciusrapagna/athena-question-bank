from app.services.competencias_service import carregar_competencias, filtrar_por_area, buscar_por_codigo


def main():
    competencias = carregar_competencias()
    print(f"Competências carregadas: {len(competencias)}")

    clinica = filtrar_por_area("Clínica Médica")
    print(f"Competências de Clínica Médica: {len(clinica)}")

    exemplo = buscar_por_codigo("CM001")
    print("Exemplo CM001:")
    print(exemplo)


if __name__ == "__main__":
    main()
