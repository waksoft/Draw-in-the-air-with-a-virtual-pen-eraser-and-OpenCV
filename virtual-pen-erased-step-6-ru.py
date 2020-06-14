# Шаг 6: Добавим стирания следа  ручки

# Начните с импорта необходимых библиотек
import cv2
import numpy as np
import time

load_from_disk = True
if load_from_disk:
    penval = np.load('penval.npy')

cap = cv2.VideoCapture(0)

# Загрузите две картинки и сделайте их размер одинаковым
pen_img = cv2.resize(cv2.imread('pen.png',1),(50, 50))
eraser_img = cv2.resize(cv2.imread('eraser.jpg',1),(50, 50))

kernel = np.ones((5,5),np.uint8)

# Сделать размер окна изменяемым
cv2.namedWindow('image', cv2.WINDOW_NORMAL)

# Это холст, на котором мы будем рисовать
canvas = None

# Создание объекта для фонового вычитания
backgroundobject = cv2.createBackgroundSubtractorMOG2(detectShadows = False)

# Этот порог, который определяет количество нарушений в фоновом режиме
background_threshold = 600

# Переменная, которая говорит вам, используете ли вы ручку или ластик
switch = 'Pen'

# С помощью этой переменной мы будем отслеживать время между предыдущими переключениями
last_switch = time.time()

# Инициализация точек (x1, y1)
x1,y1=0,0

# Порог шума
noiseth = 800

# Порог для стрирания, размер контура должен быть больше для 
# очистки холста
wiper_thresh = 40000

# Переменная, которая сообщает, когда очистить холст
clear = False

while(1):
    _, frame = cap.read()
    frame = cv2.flip( frame, 1 )
    
    # Инициализируйте чёрного холста того же размера, что и фрейм
    if canvas is None:
        canvas = np.zeros_like(frame)
        
    # Возьмите верхнюю левую часть кадра и сделайте там вычитание фона
    top_left = frame[0: 50, 0: 50]
    fgmask = backgroundobject.apply(top_left)
    
    # Обратите внимание на количество пикселей, которые являются белыми, это уровень 
    # нарушения
    switch_thresh = np.sum(fgmask==255)
    
    # Если нарушение превышает фоновый порог и имеет место быть 
    # через некоторое время после предыдущего переключения, то можно изменить 
    # тип объекта
    if switch_thresh>background_threshold and(time.time()-last_switch) > 1:

        # Save the time of the switch. 
        last_switch = time.time()
        
        if switch == 'Pen':
            switch = 'Eraser'
        else:
            switch = 'Pen'

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
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, 
    cv2.CHAIN_APPROX_SIMPLE)
    
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
        if x1 == 0 and y1 == 0:
            x1,y1= x2,y2
            
        else:
            if switch == 'Pen':
                # Рисуем линию на холсте
                canvas = cv2.line(canvas,(x1,y1),
               (x2,y2), [255,0,0], 5)
                
            else:
                cv2.circle(canvas,(x2, y2), 20,
               (0,0,0), -1)
            
            
        
        # После того, как линия нарисована, новые точки становятся предыдущими точками
        x1,y1= x2,y2
        
        # Теперь, если площадь больше порога очистки, установите 
        # переменную clear в true
        if area > wiper_thresh:
           cv2.putText(canvas,'Clearing Canvas',(0,200), 
           cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 1, cv2.LINE_AA)
           clear = True 

    else:
        # Если контуры не обнаружены, то назначим x1, y1 = 0
        x1,y1 =0,0
    
   
    # Этот кусок кода предназначен только для плавного рисования.(Необязательный)
    _ , mask = cv2.threshold(cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY), 20, 
    255, cv2.THRESH_BINARY)
    foreground = cv2.bitwise_and(canvas, canvas, mask = mask)
    background = cv2.bitwise_and(frame, frame,
    mask = cv2.bitwise_not(mask))
    frame = cv2.add(foreground,background)

    # Переключайте изображения в зависимости от того, что мы используем, перо или ластик
    if switch != 'Pen':
        cv2.circle(frame,(x1, y1), 20,(255,255,255), -1)
        frame[0: 50, 0: 50] = eraser_img
    else:
        frame[0: 50, 0: 50] = pen_img

    cv2.imshow('image',frame)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
    
    # Очистим холст через 1 секунду, если переменная clear имеет значение true
    if clear == True: 
        time.sleep(1)
        canvas = None
        
        # и вернём clear в false
        clear = False
        
cv2.destroyAllWindows()
cap.release()
