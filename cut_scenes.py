import cv2
import os

# =====================================================================
# 1. CONFIGURAÇÕES DA EXTRAÇÃO (Atualize essas variáveis a cada vídeo)
# =====================================================================
p_id = "P1"             # ID do Praticante (Ex: P1 a P4 para treino, P5 para Sensei/val)
angulo = "frontal"      # Ângulo (Ex: frontal, traseira, lat_dir, lat_esq)

# O script vai iniciar neste número e somar +1 automaticamente a cada 'S' pressionado
movimento_inicial = 1   

# Caminho do vídeo já processado com o esqueleto e fundo preto (gerado pelo Script 1)
video_path = "heian_shodan.mp4" 

# =====================================================================
# 2. INICIALIZAÇÃO DO PLAYER
# =====================================================================
# Usa a variável video_path definida acima para abrir o esqueleto no fundo preto
cap = cv2.VideoCapture(video_path)
frame_count = 0
pausado = False
movimento_atual = movimento_inicial

print("=== EXTRATOR DE FRAMES AUTOMÁTICO - TCC ===")
print("-> Pressione 'Espaço' para PAUSAR/DAR PLAY no vídeo.")
print("-> Pressione 'S' para SALVAR o frame atual e AVANÇAR para o próximo movimento.")
print("-> Pressione 'Q' para SAIR.\n")
print(f"Pronto para capturar. Próximo movimento esperado: mov{movimento_atual:02d}")

# Lê o primeiro frame antes de entrar no loop para já ter imagem na tela
success, frame = cap.read()
if not success:
    print("Erro: Não foi possível abrir o vídeo. Verifique o caminho ou o arquivo gerado pelo Script 1.")
    exit()

frame_count += 1

# =====================================================================
# 3. LOOP DE CONTROLE (O Player)
# =====================================================================
while cap.isOpened():
    
    # Só avança os frames se o vídeo não estiver pausado
    if not pausado:
        success, frame = cap.read()
        if not success:
            print("Fim do vídeo alcançado.")
            break
        frame_count += 1

    # Mostra o frame atual do vídeo na tela
    cv2.imshow("Extrator de Frames TCC", frame)
    
    # Aguarda o comando do teclado. O '30' é o delay em milissegundos (~33 fps).
    key = cv2.waitKey(30) & 0xFF
    
    # Tecla Espaço: Alterna entre Pausado e Play
    if key == ord(' '):
        pausado = not pausado
        estado = "PAUSADO" if pausado else "RODANDO"
        print(f"Vídeo {estado} no frame {frame_count}")
        
    # Tecla S: Salva o frame na nomenclatura oficial e incrementa o movimento
    if key == ord('s'):
        # Formata o número atual para o padrão 'mov01', 'mov02', etc. (:02d garante 2 dígitos)
        mov_formatado = f"mov{movimento_atual:02d}"
        
        # Mapeia dinamicamente para onde essa imagem deve ir baseando-se no movimento atual
        # NOTA: O script vai criar a pasta dinamicamente se ela não existir.
        # Ajuste o nome da subpasta se decidir usar o mapeamento exato de nomes de classes feito na etapa anterior!
        pasta_destino = "dataset_karate/train/praticante_01"
        os.makedirs(pasta_destino, exist_ok=True)
        
        # Monta o nome científico do arquivo
        nome_arquivo = f"{p_id}_{angulo}_{mov_formatado}_f{frame_count}.jpg"
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)
        
        # Salva a imagem no HD
        cv2.imwrite(caminho_completo, frame)
        print(f"✅ Kime capturado! Salvo em: {caminho_completo}")
        
        # Incrementa o contador para o próximo movimento do Kata
        movimento_atual += 1
        print(f"👉 Variável atualizada! O próximo clique salvará como: mov{movimento_atual:02d}")
        
    # Tecla Q: Interrompe a execução
    if key == ord('q'):
        print("Finalizando o extrator...")
        break

# Limpa a memória
cap.release()
cv2.destroyAllWindows()