import cv2
import numpy as np
from tkinter import Tk, filedialog
import math

def adicionar_ruido_sal_pimenta(imagem, percentual):
    # Garante que a imagem esteja em escala de cinza para a lógica do ruído
    if len(imagem.shape) > 2:
        img_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    else:
        img_cinza = imagem.copy()

    img_ruidosa = img_cinza.copy()
    altura, largura = img_ruidosa.shape
    num_pixels_a_corromper = int(altura * largura * percentual)

    for _ in range(num_pixels_a_corromper):
        y = np.random.randint(0, altura - 1)
        x = np.random.randint(0, largura - 1)
        if img_ruidosa[y, x] > 127:
            img_ruidosa[y, x] = 255  # Sal
        else:
            img_ruidosa[y, x] = 0    # Pimenta

    print(f"Ruído Sal e Pimenta ({percentual*100}%) adicionado.")
    return img_ruidosa


def aplicar_filtro_media(imagem):
    altura, largura = imagem.shape[:2]

    imagem_filtrada = imagem.copy()
    is_color = len(imagem.shape) == 3

    # Percorre a imagem, ignorando as bordas para a janela 3x3
    for y in range(1, altura - 1):
        for x in range(1, largura - 1):
            if is_color:
                soma_b, soma_g, soma_r = 0, 0, 0
            else:
                soma_cinza = 0

            # Percorre a vizinhança 3x3
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if is_color:
                        b, g, r = imagem[y + dy, x + dx]
                        soma_b += b
                        soma_g += g
                        soma_r += r
                    else:
                        soma_cinza += imagem[y + dy, x + dx]
            
            # Calcula a média e atribui ao pixel da imagem filtrada
            if is_color:
                imagem_filtrada[y, x] = (soma_b // 9, soma_g // 9, soma_r // 9)
            else:
                imagem_filtrada[y, x] = soma_cinza // 9

    print("Filtro da Média 3x3 (manual) aplicado.")
    return imagem_filtrada


def aplicar_filtro_mediana(imagem):
    altura, largura = imagem.shape[:2]
    imagem_filtrada = imagem.copy()
    is_color = len(imagem.shape) == 3

    for y in range(1, altura - 1):
        for x in range(1, largura - 1):
            if is_color:
                vizinhos_b, vizinhos_g, vizinhos_r = [], [], []
            else:
                vizinhos_cinza = []

            # Coleta os valores da vizinhança 3x3
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if is_color:
                        b, g, r = imagem[y + dy, x + dx]
                        vizinhos_b.append(b)
                        vizinhos_g.append(g)
                        vizinhos_r.append(r)
                    else:
                        vizinhos_cinza.append(imagem[y + dy, x + dx])

            # Ordena e pega o valor mediano (o 5º elemento de 9, índice 4)
            if is_color:
                vizinhos_b.sort()
                vizinhos_g.sort()
                vizinhos_r.sort()
                imagem_filtrada[y, x] = (vizinhos_b[4], vizinhos_g[4], vizinhos_r[4])
            else:
                vizinhos_cinza.sort()
                imagem_filtrada[y, x] = vizinhos_cinza[4]

    print("Filtro da Mediana 3x3 (manual) aplicado.")
    return imagem_filtrada

def aplicar_operador_sobel(imagem):
    # Máscaras de Sobel 
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])

    # Converte para escala de cinza, se já não for
    if len(imagem.shape) > 2:
        img_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    else:
        img_cinza = imagem

    altura, largura = img_cinza.shape
    imagem_bordas = np.zeros_like(img_cinza, dtype=np.float64)

    # Aplica a convolução manualmente
    for y in range(1, altura - 1):
        for x in range(1, largura - 1):
            # Extrai a vizinhança 3x3
            vizinhanca = img_cinza[y-1:y+2, x-1:x+2]
            
            # Aplica os kernels Gx e Gy
            grad_x = np.sum(vizinhanca * sobel_x)
            grad_y = np.sum(vizinhanca * sobel_y)
            
            # Calcula a magnitude do gradiente [cite: 366]
            magnitude = math.sqrt(grad_x**2 + grad_y**2)
            imagem_bordas[y, x] = magnitude

    # Normaliza a imagem para o intervalo 0-255 para visualização
    imagem_bordas = cv2.normalize(imagem_bordas, None, 0, 255, cv2.NORM_MINMAX)
    imagem_bordas = np.uint8(imagem_bordas)

    print("Operador de Sobel (manual) aplicado.")
    return imagem_bordas

def main():
    imagem_original = None
    imagem_processada = None

    while True:
        if imagem_original is None:
            print("\nNenhuma imagem carregada.")
            escolha_inicial = input("Deseja carregar uma imagem? (s/n): ").lower()
            if escolha_inicial == 's':
                root = Tk()
                root.withdraw()
                caminho_imagem = filedialog.askopenfilename(title="Selecione a imagem")
                if not caminho_imagem:
                    print("Operação cancelada.")
                    continue
                
                imagem_original = cv2.imread(caminho_imagem)
                if imagem_original is None:
                    print("Erro ao carregar a imagem.")
                    continue
                
                imagem_processada = imagem_original.copy()
                cv2.imshow("Imagem Original", imagem_original)
                cv2.imshow("Imagem Processada", imagem_processada)
                cv2.waitKey(1)
            else:
                break
        
        print("\n--- MENU DE PROCESSAMENTO (IMPLEMENTAÇÃO MANUAL) ---")
        print("1. Adicionar Ruído Sal e Pimenta (5%)")
        print("2. Aplicar Filtro da Média 3x3")
        print("3. Aplicar Filtro da Mediana 3x3")
        print("4. Aplicar Detector de Bordas de Sobel")
        print("5. Restaurar para a imagem original")
        print("6. Carregar nova imagem")
        print("7. Sair")
        
        escolha = input("Escolha uma opção: ")

        imagem_para_processar = imagem_processada if imagem_processada is not None else imagem_original
        
        if escolha == '1':
            imagem_processada = adicionar_ruido_sal_pimenta(imagem_original, 0.05)
        elif escolha == '2':
            imagem_processada = aplicar_filtro_media(imagem_para_processar)
        elif escolha == '3':
            imagem_processada = aplicar_filtro_mediana(imagem_para_processar)
        elif escolha == '4':
            imagem_processada = aplicar_operador_sobel(imagem_original)
        elif escolha == '5':
            imagem_processada = imagem_original.copy()
            print("-> Imagem restaurada para a original.")
        elif escolha == '6':
            imagem_original = None
            cv2.destroyAllWindows()
            continue
        elif escolha == '7':
            break
        else:
            print("Opção inválida. Tente novamente.")

        if imagem_processada is not None:
            cv2.imshow("Imagem Processada", imagem_processada)
            cv2.waitKey(1)

    cv2.destroyAllWindows()
    print("Programa finalizado.")

if __name__ == "__main__":
    main()