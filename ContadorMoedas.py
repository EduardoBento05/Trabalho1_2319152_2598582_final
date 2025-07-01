import cv2
import numpy as np
from tkinter import Tk, filedialog


def classificar_moeda(raio, roi_colorida):

    valor = 0.0
    nome = "N/A"


    if roi_colorida.size == 0:
        return 0.0, "Erro ROI"

    # Etapa de análise de cor
    hsv = cv2.cvtColor(roi_colorida, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, np.array([0, 1, 1]), np.array([255, 255, 255]))


    if cv2.countNonZero(mascara) > 0:
        cor_media = cv2.mean(hsv, mask=mascara)
        saturacao_media = cor_media[1]
    else:
        saturacao_media = 0



    # Verificamos se a saturação é baixa e se o tamanho é compatível.
    if saturacao_media < 55 and (raio > 64 and raio < 78):
        valor = 0.50
        nome = "R$ 0.50"

    else:
        # Moeda de 1 Real (a maior de todas)
        if raio >= 78:
            valor = 1.00
            nome = "R$ 1.00"

        # Moeda de 25 Centavos (dourada e grande)
        elif raio > 70 and raio <= 75:
            valor = 0.25
            nome = "R$ 0.25"


        # Moeda de 10 Centavos (dourada e a menor)
        elif raio > 58 and raio <= 64:
            valor = 0.10
            nome = "R$ 0.10"

    return valor, nome


def detectar_e_somar_moedas():


    Tk().withdraw()
    caminho_imagem = filedialog.askopenfilename(title="Selecione a imagem com as moedas")

    if not caminho_imagem:
        print("Nenhuma imagem selecionada.")
        return

    img_original = cv2.imread(caminho_imagem)
    if img_original is None:
        print("Erro: Não foi possivel carregar a imagem.")
        return


    img = cv2.resize(img_original, (600, 600))
    output = img.copy()

    # Pré-processamento
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 11)

    #Detecção de Círculos com Hough
    circulos = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
        param1=50, param2=30,
        minRadius=58, maxRadius=85  # Ajustado para os raios medidos (60 a 82)
    )


    if circulos is not None:
        circulos = np.round(circulos[0, :]).astype("int")
        total_monetario = 0.0

        print(f"Deteccao robusta: {len(circulos)} moedas encontradas! Classificando...")

        for (x, y, r) in circulos:
            # Recorta (ROI)
            roi = img[y - r:y + r, x - r:x + r]

            # função  valor da moeda
            valor, nome = classificar_moeda(r, roi)


            if valor > 0:
                total_monetario += valor
                cv2.circle(output, (x, y), r, (0, 255, 0), 2)
                cv2.putText(output, nome, (x - 25, y + 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Escreve o valor total final na tela
        texto_final = f"Total: R$ {total_monetario:.2f}".replace('.', ',')
        cv2.putText(output, texto_final, (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 5, cv2.LINE_AA)
        cv2.putText(output, texto_final, (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Resultado Final", output)
        cv2.waitKey(0)

    else:
        print("Nenhum círculo foi detectado.")

    cv2.destroyAllWindows()



if __name__ == "__main__":
    detectar_e_somar_moedas()