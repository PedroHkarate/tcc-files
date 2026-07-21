import cv2
import os

# =====================================================================
# 1. CONFIGURAÇÕES DA EXTRAÇÃO (Atualize essas variáveis a cada vídeo)
# =====================================================================
p_id = "P5"             # ID do Praticante
angulo = "traseiro"      # Ângulo (Ex: frontal, traseira, lat_dir, lat_esq)

# O script vai iniciar neste número e somar +1 automaticamente a cada 'S' pressionado
movimento_inicial = 1

# Caminho do vídeo já processado com o esqueleto e fundo preto (gerado pelo Script 1)
video_path = "esqueletos/P5_esqueleto_traseiro.mp4"

# Dimensões exatas desejadas para a tela e para os frames salvos (1280x720)
LARGURA_TELA = 1280
ALTURA_TELA = 720

# =====================================================================
# 2. INICIALIZAÇÃO DO PLAYER
# =====================================================================
cap = cv2.VideoCapture(video_path)
frame_count = 0
pausado = False
movimento_atual = movimento_inicial

print("=== EXTRATOR DE FRAMES AUTOMÁTICO - TCC ===")
print("-> Pressione 'Espaço' para PAUSAR/DAR PLAY no vídeo.")
print("-> Pressione 'S' para SALVAR o frame atual e AVANÇAR para o próximo movimento.")
print("-> Pressione 'Q' para SAIR.\n")
print(f"Pronto para capturar. Próximo movimento esperado: mov{movimento_atual:02d}")

# Configura a janela para ser ajustável e respeitar os 1280x720 no monitor
nome_janela = "Extrator de Frames TCC"
cv2.namedWindow(nome_janela, cv2.WINDOW_NORMAL)
cv2.resizeWindow(nome_janela, LARGURA_TELA, ALTURA_TELA)

# Lê o primeiro frame antes de entrar no loop
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

    # Redimensiona o frame atual para 1280x720 para garantir o enquadramento completo
    frame_exibicao = cv2.resize(frame, (LARGURA_TELA, ALTURA_TELA), interpolation=cv2.INTER_AREA)

    # Mostra o frame redimensionado na janela do OpenCV
    cv2.imshow(nome_janela, frame_exibicao)
    
    # Aguarda o comando do teclado (30ms ~33 fps)
    key = cv2.waitKey(30) & 0xFF
    
    # Tecla Espaço: Alterna entre Pausado e Play
    if key == ord(' '):
        pausado = not pausado
        estado = "PAUSADO" if pausado else "RODANDO"
        print(f"Vídeo {estado} no frame {frame_count}")
        
    # Tecla S: Salva o frame ajustado na nomenclatura oficial e incrementa o movimento
    if key == ord('s'):
        mov_formatado = f"mov{movimento_atual:02d}"
        
        pasta_destino = "captured_screens"
        os.makedirs(pasta_destino, exist_ok=True)
        
        # Monta o nome do arquivo
        nome_arquivo = f"{p_id}_{angulo}_{mov_formatado}_f{frame_count}.jpg"
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)
        
        # Salva o frame já ajustado em 1280x720
        cv2.imwrite(caminho_completo, frame_exibicao)
        print(f"✅ Kime capturado em 1280x720! Salvo em: {caminho_completo}")
        
        # Incrementa o contador do movimento
        movimento_atual += 1
        print(f"👉 Variável atualizada! O próximo clique salvará como: mov{movimento_atual:02d}")
        
    # Tecla Q: Interrompe a execução
    if key == ord('q'):
        print("Finalizando o extrator...")
        break

# Limpa a memória
cap.release()
cv2.destroyAllWindows()