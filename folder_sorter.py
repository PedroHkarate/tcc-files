import os
import shutil

# =====================================================================
# 1. CONFIGURAÇÕES DE CAMINHO
# =====================================================================
pasta_origem = "captured_screens"  # Onde estão as suas 420 fotos misturadas
pasta_destino_kfold = "dataset_kfold"

# Lista oficial de praticantes para o Group K-Fold
# praticantes = ["P1", "P2", "P3", "P4", "P5"]
praticantes = ["P1", "P2", "P3"]
# =====================================================================
# 2. MAPEAMENTO OFICIAL DO HEIAN SHODAN (Sua lógica de negócio)
# =====================================================================
mapeamento_movimentos = {
    # Gedan Barai
    "mov01": "zenkutsu_gedan_barai_esquerdo",
    "mov06": "zenkutsu_gedan_barai_esquerdo",
    "mov10": "zenkutsu_gedan_barai_esquerdo",
    "mov14": "zenkutsu_gedan_barai_esquerdo",

    "mov03": "zenkutsu_gedan_barai_direito",
    "mov12": "zenkutsu_gedan_barai_direito",

    # Oi Zuki
    "mov05": "zenkutsu_oi_zuki_esquerdo",
    "mov13": "zenkutsu_oi_zuki_esquerdo",
    "mov16": "zenkutsu_oi_zuki_esquerdo",

    "mov02": "zenkutsu_oi_zuki_direito",
    "mov11": "zenkutsu_oi_zuki_direito",
    "mov15": "zenkutsu_oi_zuki_direito",
    "mov17": "zenkutsu_oi_zuki_direito",

    # Age Uke
    "mov08": "zenkutsu_age_uke_esquerdo",

    "mov07": "zenkutsu_age_uke_direito",
    "mov09": "zenkutsu_age_uke_direito",

    # Tetsui
    "mov04": "zenkutsu_tetsui_direito",

    # Shuto Uke
    "mov18": "kokutsu_shuto_uke_esquerdo",
    "mov21": "kokutsu_shuto_uke_esquerdo",

    "mov19": "kokutsu_shuto_uke_direito",
    "mov20": "kokutsu_shuto_uke_direito"
}

# CONTADORES PARA O RELATÓRIO FINAL
arquivos_processados = 0
arquivos_ignorados = 0

print("=== INICIANDO DISTRIBUIÇÃO AUTOMÁTICA EM KFOLD ===")

# Certifica-se de que a pasta de origem existe
if not os.path.exists(pasta_origem):
    print(f"Erro: A pasta '{pasta_origem}' não foi encontrada. Crie-a e coloque as fotos dentro.")
    exit()

# =====================================================================
# 3. PROCESSAMENTO E DISTRIBUIÇÃO DOS ARQUIVOS
# =====================================================================
for arquivo in os.listdir(pasta_origem):
    # Ignora arquivos que não sejam imagens JPG
    if not (arquivo.lower().endswith('.jpg') or arquivo.lower().endswith('.jpeg')):
        continue

    # Extrai o ID do praticante (Ex: 'P1' de 'P1_frontal_mov01_f12.jpg')
    partes = arquivo.split('_')
    p_id = partes[0]

    if p_id not in praticantes:
        print(f"Aviso: Arquivo '{arquivo}' não começa com um ID válido (P1 a P3). Ignorado.")
        arquivos_ignorados += 1
        continue

    # Descobre a qual movimento (classe) o arquivo pertence
    classe_atual = None
    for mov_chave, nome_classe in mapeamento_movimentos.items():
        if mov_chave in arquivo:
            classe_atual = nome_classe
            break

    # Se o frame não corresponder a nenhum movimento mapeado, pula
    if not classe_atual:
        print(f"Aviso: Não encontramos mapeamento para o movimento do arquivo '{arquivo}'. Ignorado.")
        arquivos_ignorados += 1
        continue

    # Distribui a imagem de forma cruzada nos 5 Folds distintos
    for i, p_teste in enumerate(praticantes, start=1):
        fold_nome = f"fold_{i}"

        # Regra de Ouro do Group K-Fold:
        # Se o praticante do arquivo for o escolhido para teste NESTE fold, vai para 'val'.
        # Se for qualquer um dos outros 4 praticantes, vai para 'train'.
        subpasta = "val" if p_id == p_teste else "train"

        # Constrói o caminho final da árvore de diretórios
        caminho_final_pasta = os.path.join(pasta_destino_kfold, fold_nome, subpasta, classe_atual)
        os.makedirs(caminho_final_pasta, exist_ok=True)

        # Copia fisicamente o arquivo para o destino correto
        shutil.copy2(os.path.join(pasta_origem, arquivo), os.path.join(caminho_final_pasta, arquivo))

    arquivos_processados += 1

# =====================================================================
# 4. RELATÓRIO DE EXECUÇÃO
# =====================================================================
print("\n" + "="*40)
print("🏆 PROCESSO CONCLUÍDO COM SUCESSO!")
print(f"-> Imagens organizadas nos 5 folds: {arquivos_processados}")
print(f"-> Arquivos ignorados/fora do padrão: {arquivos_ignorados}")
print(f"-> Destino: {os.path.abspath(pasta_destino_kfold)}")
print("="*40)