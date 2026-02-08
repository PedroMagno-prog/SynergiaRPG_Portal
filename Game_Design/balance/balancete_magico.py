import math
import csv
import time

def validar_todas_as_builds():
    """
    Testa todas as combinações de Dano, Alcance e Área
    para encontrar builds válidas dentro do orçamento de PC.
    """
    print("Iniciando validação de todas as builds...")
    start_time = time.time()

    # --- Constantes do Sistema ---
    MAX_PC_BUDGET = 60
    MAX_ALCANCE = 20
    MAX_AREA = 36

    # Máximo de dados 'X' a testar.
    # Se (X*4)/2 = 60 (dano de d4), X = 30.
    # Usaremos 30 como um teto seguro.
    MAX_DADOS_X = 30

    TIPOS_DADO_Y = [4, 6, 8, 10, 12]  # d4, d6, d8, d10, d12
    # -----------------------------

    valid_builds = []
    iteracoes_totais = 0

    # 4 loops aninhados para testar todas as combinações
    for y_dado in TIPOS_DADO_Y:
        for x_dados in range(1, MAX_DADOS_X + 1):
            for al_alcance in range(0, MAX_ALCANCE + 1):
                for ar_area in range(0, MAX_AREA + 1):

                    iteracoes_totais += 1

                    # --- Cálculo de Custo (Suas Fórmulas) ---
                    custo_dano = (x_dados * y_dado) / 2
                    custo_alcance = math.ceil(al_alcance / 2)
                    custo_area = ar_area

                    custo_total_pc = custo_dano + custo_alcance + custo_area

                    # --- Validação ---
                    if custo_total_pc <= MAX_PC_BUDGET:
                        # Calcula a média de dano para análise
                        # Média de 1 dado Y = (Y + 1) / 2
                        dano_medio_calculado = x_dados * ((y_dado + 1) / 2)

                        build_info = {
                            "Descricao_Dano": f"{x_dados}d{y_dado}",
                            "Alcance_Blocos": al_alcance,
                            "Area_Blocos": ar_area,
                            "Custo_Total_PC": custo_total_pc,
                            "Dano_Medio": round(dano_medio_calculado, 2),
                            "Custo_Dano": custo_dano,
                            "Custo_Alcance": custo_alcance,
                            "Custo_Area": custo_area
                        }
                        valid_builds.append(build_info)

    end_time = time.time()
    print(f"Validação concluída em {end_time - start_time:.2f} segundos.")
    print(f"Total de {iteracoes_totais:,} combinações testadas.")

    # --- Análise e Geração de Relatório ---
    if not valid_builds:
        print("Nenhuma build válida foi encontrada com os parâmetros fornecidos.")
        return

    print(f"Total de {len(valid_builds):,} builds válidas (<= {MAX_PC_BUDGET} PC) encontradas.")

    # Salvar em CSV
    output_filename = "validacao_builds_de_poder.csv"
    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as f:
            # Pega as chaves do primeiro dicionário para usar como cabeçalho
            fieldnames = valid_builds[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(valid_builds)

        print(f"\n[SUCESSO] Todas as builds válidas foram salvas em '{output_filename}'")

    except Exception as e:
        print(f"\n[ERRO] Não foi possível salvar o arquivo CSV: {e}")

    # --- Análise Rápida (Insights) ---
    print("\n--- Análise Rápida das Builds ---")

    # Encontrar a build com o maior Dano Médio possível (o "Canhão de Vidro")
    build_max_dano_geral = max(valid_builds, key=lambda b: b["Dano_Medio"])
    print(f"🥇 Build com Maior Dano Médio (Geral):")
    print(f"   {build_max_dano_geral['Descricao_Dano']} (Média: {build_max_dano_geral['Dano_Medio']})")
    print(f"   Alcance: {build_max_dano_geral['Alcance_Blocos']}, Área: {build_max_dano_geral['Area_Blocos']}")
    print(f"   Custo: {build_max_dano_geral['Custo_Total_PC']} PC")

    # Encontrar builds que custam exatamente 60 PC
    builds_nivel_maximo = [b for b in valid_builds if b["Custo_Total_PC"] == MAX_PC_BUDGET]

    if builds_nivel_maximo:
        print(f"\nEncontradas {len(builds_nivel_maximo)} builds de 'nível máximo' (exatos 60 PC).")

        # Encontrar a build de 60 PC com maior dano
        build_max_dano_60pc = max(builds_nivel_maximo, key=lambda b: b["Dano_Medio"])
        print(f"🎯 Build de Maior Dano (custando exatos 60 PC):")
        print(f"   {build_max_dano_60pc['Descricao_Dano']} (Média: {build_max_dano_60pc['Dano_Medio']})")
        print(f"   Alcance: {build_max_dano_60pc['Alcance_Blocos']}, Área: {build_max_dano_60pc['Area_Blocos']}")

        # Encontrar a build de 60 PC com maior alcance
        build_max_alcance_60pc = max(builds_nivel_maximo, key=lambda b: b["Alcance_Blocos"])
        print(f"🔭 Build de Maior Alcance (custando exatos 60 PC):")
        print(f"   {build_max_alcance_60pc['Descricao_Dano']} (Média: {build_max_alcance_60pc['Dano_Medio']})")
        print(f"   Alcance: {build_max_alcance_60pc['Alcance_Blocos']}, Área: {build_max_alcance_60pc['Area_Blocos']}")

        # Encontrar a build de 60 PC com maior área
        build_max_area_60pc = max(builds_nivel_maximo, key=lambda b: b["Area_Blocos"])
        print(f"💥 Build de Maior Área (custando exatos 60 PC):")
        print(f"   {build_max_area_60pc['Descricao_Dano']} (Média: {build_max_area_60pc['Dano_Medio']})")
        print(f"   Alcance: {build_max_area_60pc['Alcance_Blocos']}, Área: {build_max_area_60pc['Area_Blocos']}")
    else:
        print("\nNenhuma build encontrada que custe exatamente 60 PC.")


# --- Para Rodar o Script ---
if __name__ == "__main__":
    validar_todas_as_builds()