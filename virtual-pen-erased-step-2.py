# Начните с импорта необходимых библиотек
import cv2
import numpy as np
import time

# Эта переменная определяет, хотим ли мы загрузить диапазон цветов с диска
# или используйте те, которые определены здесь.
load_from_disk = True

# Если True, тогда загружаем с диска
if load_from_disk:
    penval = np.load('penval.npy')

cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

# Создание ядра размером 5x5 для морфологических операций
kernel = np.ones((5,5),np.uint8)

while(1):
    ret, frame = cap.read()
    if not ret:
        break
        
    frame = cv2.flip( frame, 1 )

    # Конвертировать BGR в HSV
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
    # Оперрация erode (размытие) съедает белую часть, в то время как dilate (распространить) расширяет ее
    mask = cv2.erode(mask,kernel,iterations = 1)
    mask = cv2.dilate(mask,kernel,iterations = 2)

    res = cv2.bitwise_and(frame,frame, mask= mask)

    mask_3 = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    
    # сложим все кадры и покажем их
    stacked = np.hstack((mask_3,frame,res))
    cv2.imshow('Trackbars',cv2.resize(stacked, None, fx=0.4, fy=0.4))
    
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
cap.release()
