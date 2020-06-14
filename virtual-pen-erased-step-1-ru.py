# Шаг 1: Найдём цветовую гамму объекта и сохраним её

# Начните с импорта необходимых библиотек
import cv2
import numpy as np
import time

# Описание функции обратного вызова, которая необходима для создания трекбаров
def nothing(x):
    pass

# Инициализируем веб-камеру
cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

# Создаём окно с именем Trackbars.
cv2.namedWindow("Trackbars")

# Теперь создаём 6 трекбаров, которые будут управлять нижним и верхним диапазоном 
# H, S и V каналов. Аргументы: имя трека, 
# имя окна, диапазон, функция обратного вызова. Для оттенков диапазон от 0 до 179, а
# для S, V от 0 до 255.
cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)
 
 
while True:
    # Начинаем кадр за кадром читать веб-камеру
    ret, frame = cap.read()
    if not ret:
        break
    # Перевернём рамку горизонтально(не обязательно)
    frame = cv2.flip(frame, 1) 
    
    # Преобразуем изображение из BGR в HSV.
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # В режиме реального времени получаем новые значения трекбара по мере их изменения
    l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    u_v = cv2.getTrackbarPos("U - V", "Trackbars")
 
    # Устанавливаем нижний и верхний диапазоны HSV в соответствии с выбранным значением
    # рядом с дорожкой ползунка
    lower_range = np.array([l_h, l_s, l_v])
    upper_range = np.array([u_h, u_s, u_v])
    
    # Фильтруем изображение и получаем бинарную маску, где белый цвет заменяет 
    # ваш целевой цвет 
    mask = cv2.inRange(hsv, lower_range, upper_range)
 
    # Можно визуализировать реальную часть целевого цвета(необязательно)
    res = cv2.bitwise_and(frame, frame, mask=mask)
    
    # Преобразование бинарной маски в 3-канальное изображение, только так 
    # можно сложить его вместе с другими
    mask_3 = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    
    # Сложим маску с исходным фреймом и отфильтруем результат
    stacked = np.hstack((mask_3,frame,res))
    
    # Покажем результирующий фрейм в 40% от размера.
    cv2.imshow('Trackbars', cv2.resize(stacked,None,fx=0.4,fy=0.4))
    
    # Если нажать клавишу ESC, то программа завершиться
    key = cv2.waitKey(1)
    if key == 27:
        break
    
    # Если нажать "s", то распечатаем гамму
    if key == ord('s'):
        
        thearray = [ [l_h,l_s,l_v], [u_h, u_s, u_v] ]
        print(thearray)
        
        # и сохраним её в файле penval.npy
        np.save('penval', thearray)
        break
    
# Выключаем камеру и уничтожаем все окна.
cap.release()
cv2.destroyAllWindows()
