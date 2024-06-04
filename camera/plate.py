import cv2
import imutils
import numpy as np
import pytesseract


def plate_():
    # okuma ve çevirme
    img = cv2.imread("images/", cv2.IMREAD_COLOR)
    img = cv2.resize(img, (600, 400))
    # grayscale işlemi
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 13, 15, 15)
    # canny detector, kenar algılama algoritması
    """
    canny (radius, sigma, lower_percent, Upper_percent):
    radius: Bu parametre, gauss filtresinin yarıçapını saklar.
    sigma: Bu parametre, gauss filtresinin standart sapmasını saklar.
    lower_percent: Normalleştirilmiş alt eşiği saklayan bu parametre.
    Upper_percent: Normalize edilmiş üst eşiği saklayan bu parametre.
    Return Value: Bu işlev Wand ImageMagick nesnesini döndürür.
    """
    # kontur aralığı başlangıç ve bitiş
    edged = cv2.Canny(gray, 30, 200)
    # copy(): kopyası, RETR_TREE: tüm kontur ve ilişkilerini bulur, CHAIN_APROX_SIMPLE: daha az noktalarla temsil ederek hafızadan tasarruf sağlar
    contours = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # dönen konturlar ve hiyearşi
    contours = imutils.grab_contours(contours)
    # bulunan konturlar büyükten küçüğe sıralanır ve en büyük '[:10]' konturu seçer
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    screenCnt = None

    # açık eğrisi meydana getirmek için cv2.approxPolyDP
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)

        if len(approx) == 4:
            screenCnt = approx
            break

    # şekil tespit edildiyse çizdir, drawCounters
    if screenCnt is None:
        detected = 0
        print("Şekil Tespit Edilmedi.")
    else:
        detected = 1

    if detected == 1:
        cv2.drawContours(img, [screenCnt], -1, (0, 0, 255), 3)

    # openCV ile maskeleme yapmak için cv2.bitwise_and() 
    mask = np.zeros(gray.shape, np.uint8)
    new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1,)
    new_image = cv2.bitwise_and(img, img, mask=mask)
    
    # blog : https://bayramblog.medium.com/python-opencv-ile-plaka-tan%C4%B1ma-plate-recognition-basit-ef97cf7a7c7c