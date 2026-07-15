import cv2
import numpy as np
from ultralytics import YOLO

# Carrega o modelo YOLO de Pose
model = YOLO('yolo26x-pose.pt')

# Caminho do vídeo de entrada e saída
video_path = 'heian_shodan.mp4'
output_path = 'esqueleto_karate.mp4'

# Abre o vídeo com OpenCV
cap = cv2.VideoCapture(video_path)

# Pega as propriedades do vídeo (largura, altura e FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Configura o gravador de vídeo (VideoWriter) para salvar o resultado
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

print("Iniciando processamento com mapeamento cromático anatômico...")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break  # Fim do vídeo

    # Roda o rastreamento no frame atual
    results = model.track(frame, persist=True, verbose=False)
    result = results[0]

    # Cria um fundo 100% preto com as mesmas dimensões do vídeo
    frame_esqueleto = np.zeros((height, width, 3), dtype=np.uint8)

    # Verifica se existem pessoas e pontos mapeados no frame
    if result.keypoints is not None and len(result.keypoints) > 0:
        # Extrai as coordenadas XY e as confianças de forma limpa via NumPy
        xys = result.keypoints.xy.cpu().numpy()
        confs = result.keypoints.conf.cpu().numpy() if result.keypoints.conf is not None else None

        for idx in range(len(xys)):
            xy = xys[idx]
            conf = confs[idx] if confs is not None else np.ones(17)

            # -----------------------------------------------------------------
            # LÓGICA DE ORIENTAÇÃO PEDIDA: Validação pelos pontos do rosto
            # Índices do rosto no COCO: 0 (Nariz), 1 (Olho E), 2 (Olho D), 3 (Orelha E), 4 (Orelha D)
            # Se pelo menos 2 pontos faciais tiverem confiança aceitável (> 0.4), está de frente/perfil
            pontos_rosto = [0, 1, 2, 3, 4]
            rosto_visivel = sum(1 for i in pontos_rosto if conf[i] > 0.4) >= 3
            status_orientacao = "FRENTE/PERFIL" if rosto_visivel else "COSTAS"
            # -----------------------------------------------------------------

            # CONFIGURAÇÃO DE CORES (Padrão OpenCV é BGR)
            # Lado DIREITO Anatômico = CORES FRIAS (Azul e Ciano)
            cor_braco_dir = (255, 80, 80)     # Azul Claro
            cor_perna_dir = (255, 255, 0)    # Ciano / Teal

            # Lado ESQUERDO Anatômico = CORES QUENTES (Vermelho e Laranja)
            cor_braco_esq = (80, 80, 255)     # Vermelho Vivo
            cor_perna_esq = (0, 140, 255)     # Laranja

            # Estruturas Centrais
            cor_torso = (255, 0, 255)         # Magenta / Rosa
            cor_cabeca = (0, 255, 0)          # Verde

            # MATRIZ DE CONEXÕES FIXAS (Garante que a cor não mude ao girar o corpo)
            # Índices Pares = Lado Direito Anatômico | Índices Ímpares = Lado Esquerdo Anatômico
            conexoes = [
                # Membros Direitos (Anatômicos) -> Cores Frias
                (6, 8, cor_braco_dir), (8, 10, cor_braco_dir),        # Ombro-Cotovelo, Cotovelo-Pulso (Direito)
                (12, 14, cor_perna_dir), (14, 16, cor_perna_dir),    # Quadril-Joelho, Joelho-Tornozelo (Direito)

                # Membros Esquerdos (Anatômicos) -> Cores Quentes
                (5, 7, cor_braco_esq), (7, 9, cor_braco_esq),        # Ombro-Cotovelo, Cotovelo-Pulso (Esquerdo)
                (11, 13, cor_perna_esq), (13, 15, cor_perna_esq),    # Quadril-Joelho, Joelho-Tornozelo (Esquerdo)

                # Caixa Estrutural do Torso
                (5, 6, cor_torso), (6, 12, cor_torso),
                (12, 11, cor_torso), (11, 5, cor_torso)
            ]

            # 1. Desenha as linhas do rosto apenas se detectado de Frente/Perfil
            if rosto_visivel:
                conex_rosto = [(0, 1), (0, 2), (1, 3), (2, 4)]
                for p1, p2 in conex_rosto:
                    if conf[p1] > 0.4 and conf[p2] > 0.4:
                        pt1 = (int(xy[p1][0]), int(xy[p1][1]))
                        pt2 = (int(xy[p2][0]), int(xy[p2][1]))
                        cv2.line(frame_esqueleto, pt1, pt2, cor_cabeca, 3)

            # 2. Desenha as linhas dos membros e torso
            for p1, p2, cor in conexoes:
                if conf[p1] > 0.4 and conf[p2] > 0.4:
                    pt1 = (int(xy[p1][0]), int(xy[p1][1]))
                    pt2 = (int(xy[p2][0]), int(xy[p2][1]))
                    cv2.line(frame_esqueleto, pt1, pt2, cor, 3)

            # 3. Desenha as articulações (Keypoints) como círculos preenchidos
            for i in range(17):
                if conf[i] > 0.4:
                    pt = (int(xy[i][0]), int(xy[i][1]))

                    # Seleção de cor do nó baseado no membro real
                    if i in [0, 1, 2, 3, 4]:
                        if not rosto_visivel: continue  # Pula desenho facial se estiver de costas
                        cor_pt = cor_cabeca
                    elif i in [5, 7, 9]:     cor_pt = cor_braco_esq
                    elif i in [11, 13, 15]:  cor_pt = cor_perna_esq
                    elif i in [6, 8, 10]:    cor_pt = cor_braco_dir
                    elif i in [12, 14, 16]:  cor_pt = cor_perna_dir
                    else:                    cor_pt = cor_torso

                    cv2.circle(frame_esqueleto, pt, 6, cor_pt, -1)

            # 4. Escreve a orientação na tela (Agrega valor técnico para o relatório e para a LLM)
            cv2.putText(frame_esqueleto, f"Orientacao: {status_orientacao}", (40, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # Salva o frame customizado no novo arquivo de vídeo
    out.write(frame_esqueleto)

# Libera os recursos e fecha as janelas
cap.release()
out.release()
cv2.destroyAllWindows()
print("Vídeo processado com sucesso! Arquivo salvo em:", output_path)