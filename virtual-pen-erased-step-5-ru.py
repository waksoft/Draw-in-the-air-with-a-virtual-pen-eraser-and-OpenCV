# Шаг 5: Добавим очистку экрана

# Начните с импорта необходимых библиотек
import cv2
import numpy as np
import time

load_from_disk = True
if load_from_disk:
    penval = np.load('penval.npy')

cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

kernel = np.ones((5,5),np.uint8)

# Настройка размера окна
cv2.namedWindow('image', cv2.WINDOW_NORMAL)

# Это холст, на который мы будем опираться
canvas=None

# Инициализация точек (x1, y1)
x1,y1=0,0

# Порог для шума
noiseth = 800

# Порог для стирания, размер контура должен быть больше чем для нас
# очистить холст
wiper_thresh = 40000

# Переменная, которая говорит, когда очищать холст, если его True, тогда мы очищаем холст
clear = False

while(1):
    _, frame = cap.read()
    frame = cv2.flip( frame, 1 )
    
    # Инициализируйте чёрного холста того же размера, что и рамка
    if canvas is None:
        canvas = np.zeros_like(frame)

    # Преобразование BGR в HSV
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
    
    # Ищем контуры
    contours, hierarchy = cv2.findContours(mask,
    cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
    # Убедитесь, что контур присутствует, а также убедитесь, что его размер
    # больше порога шума
    if contours and cv2.contourArea(max(contours,
                                   key = cv2.contourArea)) > noiseth:
                
        c = max(contours, key = cv2.contourArea)    
        x2,y2,w,h = cv2.boundingRect(c)
        
        # Get the area of the contour
        area = cv2.contourArea(c)
        
        # Если предыдущих точек не было, то сохраните обнаруженные x2, y2 
        # в координаты x1, y1. 
        # Это верно, когда мы пишем в первый раз или когда пишем 
        # снова, после того, когда ручка исчезала из виду 
        if x1 == 0 and y1 == 0:
            x1,y1= x2,y2
            
        else:
            # Рисуем линию на чёрном холсте
            canvas = cv2.line(canvas,(x1,y1),(x2,y2),
            [255,0,0], 5)
        
        # После того, как линия нарисована, новые точки становятся 
		# предыдущими точками
        x1,y1= x2,y2
        
        # Теперь, если площадь контура больше порога очистки, установите
        # переменную в True и предупредите пользователя.
        if area > wiper_thresh:
           cv2.putText(canvas,'Clearing Canvas',(100,200), 
           cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,255), 5, cv2.LINE_AA)
           clear = True 

    else:
        # Если контуров не обнаружено, то присвоим x1, y1 = 0
        x1,y1 =0,0
    
   
    # Этот фрагмент кода предназначен только для плавного рисования. (Необязательно)
    _ , mask = cv2.threshold(cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY), 20, 
    255, cv2.THRESH_BINARY)
    foreground = cv2.bitwise_and(canvas, canvas, mask = mask)
    background = cv2.bitwise_and(frame, frame,
    mask = cv2.bitwise_not(mask))
    frame = cv2.add(foreground,background)

    cv2.imshow('image',frame)
    
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
    
    # Очистить холст через 1 секунду, если переменная clear равна True
    if clear == True:
        
        time.sleep(1)
        canvas = None
        
        # И затем установите значение False
        clear = False
        
cv2.destroyAllWindows()
cap.release()
