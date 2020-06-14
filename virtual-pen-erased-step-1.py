import cv2
import numpy as np
import time

# Функция обратного вызова, которая небходими для функций трекбаров.
def nothing(x):
    pass

# Инициализируем канал веб-камеры.
cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

# Создаём окно с именем Trackbars.
cv2.namedWindow("Trackbars")

# # Теперь создаём 6 трекбаров, которые будут управлять нижним и верхним диапазоном 
# H, S и V каналов. Аргументы: имя панели треков, 
# имя окна, диапазон, функция обратного вызова. Для оттенка диапазон составляет 0-179 и
# для S, V его 0-255.
cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)
 
 
while True:
    # Начнинаем кадр за кадром читать канал веб-камеры.
    ret, frame = cap.read()
    if not ret:
        break
    # Переверните рамку горизонтально (не обязательно)
    frame = cv2.flip(frame, 1) 
    
    # Преобразуем изображение из BGR в HSV.
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
	# Получаем новые значения трекбара в режиме реального времени по мере их изменения пользователем 
    l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    u_v = cv2.getTrackbarPos("U - V", "Trackbars")
 
	# Устаннавливаем нижний и верхний диапазоны HSV в соответствии с выбранным значением
    # рядом с дорожкой ползунка
    lower_range = np.array([l_h, l_s, l_v])
    upper_range = np.array([u_h, u_s, u_v])
    
    # Фильтруем изображение и получаем двоичную маску, где белый цвет представляет собой 
    # ваш целевой цвет
    mask = cv2.inRange(hsv, lower_range, upper_range)
 
    # Можно визуализировать реальную часть целевого цвета (необязательно)
    res = cv2.bitwise_and(frame, frame, mask=mask)
    
    # Преобразование двоичной маски в 3-канальное изображение, только так 
    # можно сложить его вместе с другими
    mask_3 = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    
    # Сложим маску с исходным фреймом и отфильтруем результат
    stacked = np.hstack((mask_3,frame,res))
    
    # Покажем сложенную фрейм в 40% от размера.
    cv2.imshow('Trackbars', cv2.resize(stacked,None,fx=0.4,fy=0.4))
    
    # Если нажать клавишу ESC, то программа завершиться
    key = cv2.waitKey(1)
    if key == 27:
        break
    
    # Если нажать "s", то распечатаем этот массив.
    if key == ord('s'):
        
        thearray = [[l_h,l_s,l_v],[u_h, u_s, u_v]]
        print(thearray)
        
        # и сохраним его в файле penval.npy
        np.save('penval', thearray)
        break
    
# Выключаем камеру и уничтожаем все окна.
cap.release()
cv2.destroyAllWindows()
