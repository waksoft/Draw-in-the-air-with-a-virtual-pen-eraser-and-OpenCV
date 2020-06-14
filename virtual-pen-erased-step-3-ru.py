# Шаг 3: Найдём и отследим контуры цветного объекта

# Начните с импорта необходимых библиотек
import cv2
import numpy as np
import time

# Эта переменная определяет, хотим ли мы загрузить диапазон цветов с диска
# или используйте те, которые определены здесь.
load_from_disk = True

# Если True, то загружаем диапазон с диска
if load_from_disk:
    penval = np.load('penval.npy')

cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

# определим ядро для морфологических операций
kernel = np.ones((5,5),np.uint8)

# установим окно в автоматический размер для просмра на полном экране
cv2.namedWindow('image', cv2.WINDOW_NORMAL)

# Этот порог используется для фильтрации шума, площадь контура должна быть
# больше этого, чтобы считаться фактическим контуром.
noiseth = 500

while(1):
    
    _, frame = cap.read()
    frame = cv2.flip( frame, 1 )

    # Преобразуем BGR в HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Если вы читаете с диска, берём верхний и нижний диапазоны оттуда
    if load_from_disk:
            lower_range = penval[0]
            upper_range = penval[1]
            
    # В противном случае определяем свои собственные значения для верхнего и нижнего диапазона.
    # Указанные здесь значения для верхнего и нижнего диапазона верны для оттенков синего и 
    # в вашей ситуации могут не работать
    else:             
       lower_range  = np.array([26,80,147])
       upper_range = np.array([81,255,255])
    
    mask = cv2.inRange(hsv, lower_range, upper_range)
    
    # Выполним морфологические операции для избавления от шума
    mask = cv2.erode(mask,kernel,iterations = 1)
    mask = cv2.dilate(mask,kernel,iterations = 2)
    
    # Ищем контуры в фрейме
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE)
    
    # Убедитесь, что контур присутствует, а также убедитесь, что его размер
    # больше порога шума.
    if contours and cv2.contourArea(max(contours, 
                               key = cv2.contourArea)) > noiseth:
        
        # Захватить самый большой по площади контур
        c = max(contours, key = cv2.contourArea)
        
        # Получите координаты ограничивающего прямоугольника вокруг этого контура
        x,y,w,h = cv2.boundingRect(c)
        
        # Нарисуйте эту ограничивающую рамку
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,25,255),2)        

    cv2.imshow('image',frame)
    
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
cap.release()
