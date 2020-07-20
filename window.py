import cv2
import numpy as np
import time
from start import started

refPt = []
refSu = []
cropping = False
count = 0
image = np.zeros((256, 256), dtype='uint8')


def getMaxContourInd(contours): # Функция для нахождения индекса максимального контура (работает как обычный поиск максимума)
	maxIndex = 0
	maxArea = 0
	for i in range(len(contours)):
		cnt = contours[i]
		area = cv2.contourArea(cnt)
		if area > maxArea:
			maxArea = area
			maxIndex = i
	return maxIndex

def click_and_crop(event, x, y, flags, param): #Функция для выделения квадратов на бинарном изображении
	global refPt, cropping, count, image
	if event == cv2.EVENT_LBUTTONDOWN: # если левая кнопка мыши нажата, то:
		refPt.append((x, y)) # добавляем координаты того пикселя, на который мы нажали
		count += 1 # инкрементируем число опорных точек
	# check to see if the left mouse button was released
	elif event == cv2.EVENT_LBUTTONUP: # если левая кнопка мыши отжата, то:
		count += 1 # инкрементируем число опорных точек
		refPt.append((x, y)) # добавляем координаты того пикселя, на котором мы отжали кнопку мыши
		# print(count)
		# draw a rectangle around the region of interest
		# print(refPt[count-2], refPt[count-1])
		cv2.rectangle(image, refPt[count-2], refPt[count-1], (0, 255, 0), 2) # отрисовываем прямоугольник по тем координатам, которые мы выделили
		cv2.imshow("image", image)


# load the image, clone it, and setup the mouse callback function

def generate_boxes():
	global refPt, refSu, cropping, count, image
	im_path = 'background.jpg'
	settings_path = 'settings.txt'
	answer = input('Do you want to load previous settings? Press y to accept or n to rewrite the file.') #Предлагаем выбор использования предыдущих настроек или настроить сейчас
	if answer == 'y': #При использовании предыдущих, считываем все данные сфайла
		with open(settings_path, 'r') as set_file:
			for i, lines in enumerate(set_file):
				if i > 0:
					if len(lines)>5:
						print(len(lines))
						coords = lines[1:-2]
						coords_tuple = tuple(int(c) for c in coords.split(', '))
						refPt.append(coords_tuple)
					else:
						refSu.append(float(lines))
		return refPt, refSu

	else: #При настройке в данный момент времени
		started() #Вызываем функцию Started из файла Start которая делает бинарное фото руки и записывает в файл setting текущие настройки диапозона цвета 
		image = cv2.imread(im_path) #Считываем бинарное фото руки
		image = cv2.resize(image, (256, 256)) 
		clone = image.copy()

		cv2.namedWindow("image")
		cv2.setMouseCallback("image", click_and_crop) # устанавливаем поведение программы при нажатии кнопок мыши. Это поведение было описано в ф-ии click_and_crop
		while True:
			cv2.imshow("image", image)
			key = cv2.waitKey(1) & 0xFF
			if key == ord("r"): # сбросить выделенные прямоугольники при нажатии клавиши r (начать выделение завново)
				image = clone.copy()
				refPt = []
				count = 0
			elif key == ord("c"): # сохранить выделенные прямоугольники нажатием клавиши c
				image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
				refSu = calculate_area(image, refPt) #Вычисляем исходное заполнение на кадре
				with open(settings_path, 'a') as setting:
					for i, points in enumerate(refPt):
						setting.write(str(points))
						setting.write('\n')
					for i in range(len(refSu)):
						setting.write(str(refSu[i])+'\n')
						# if i % 2 == 1:
						# 	setting.write('\n')
				break
		# print(refPt)
		return refPt, refSu
		# cv2.destroyAllWindows()

def display_boxes(image, name, ref_points, img_size, perimetr=False): #Функция отрисовки квадратов на изображении (параметр perimetr дает возможность отрисовывать контур руки красынм)
	if perimetr: 
		matrix =cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #Создаем 1-канальное изображение
		contours,hierarchy = cv2.findContours(matrix,2,1) #Находим все контуры
		if len(contours)>0:
			maxContourInd = getMaxContourInd(contours)#находим максимальный контур
			cnt = contours[maxContourInd]

			hull = cv2.convexHull(cnt,returnPoints = False)
			defects = cv2.convexityDefects(cnt,hull)#Находим дефекты на изображении
			if defects is not None:
				for i in range(defects.shape[0]): #для каждого дефекта отрисовываем линию, соединяющую начальную и конечную точку
					s,e,f,d = defects[i,0]
					start = tuple(cnt[s][0])
					end = tuple(cnt[e][0])
					cv2.line(image,start,end,[0,0,255],2)

	for i in range(0, len(ref_points) - 1, 2):#отрисовываем все прямоугольники в масштабе изрбражения
		cv2.rectangle(image, ((int(ref_points[i][0]*img_size/256)), (int(ref_points[i][1]*img_size/256))), ((int(ref_points[i+1][0]*img_size/256)), (int(ref_points[i+1][1]*img_size/256))), (0, 255, 0), 2)
	cv2.imshow(name, image)
	


def calculate_area(matrix, ref_points): # Функция для подсчета процента заполняемости квадрата
	summ = []
	for i in range(len(ref_points)//2):
		si = np.sum(matrix[ref_points[2*i][1]:ref_points[2*i+1][1], ref_points[2*i][0]:ref_points[2*i+1][0]])//255#Считаем кол-во пикселей руки в квадрате
		pi = (ref_points[2*i+1][0]-ref_points[2*i][0])*(ref_points[2*i+1][1]-ref_points[2*i][1])# Считаем количество всех пикселей
		summ.append(round(si/pi, 2))
	return summ

def area_ratio(ref_sum, cur_sum):#Считаем процент заполняемости относительно исходного кадра
	if len(ref_sum) != len(cur_sum):
		print('ERROR')
		exit()
	procent = []
	idx = [] 
	for i in range(len(ref_sum)):
		num = round(cur_sum[i]/ref_sum[i], 2) #Делим текущую заполняемость на исходную
		procent.append(num)
		if num>0.6: #Делаем дискретное разделение на 3 класс (Разогнутый, Полусогнутый, Согнутый)
			idx.append(2)
		elif num>0.25 and num<0.6:
			idx.append(1)
		else: 
			idx.append(0)
	return procent, idx


if __name__ == '__main__':
	cap = cv2.VideoCapture(0)
	ref_points, ref_summs = generate_boxes() #Вызываем функцию для извлечения координаток прямоугольников
	print(ref_points)
	with open('settings.txt', 'r') as set_file: #Считываем с файла настройки палитры HSV (диапазон цвета)
		mini, maxi = tuple(int(c) for c in set_file.readline().split())
	print(mini, maxi)
	while(True):
		s1 = time.time()
		ret, frame = cap.read()
		frame = cv2.flip(frame, 1)
		img_show = cv2.resize(frame, (640, 640)) #Выставляем размеры для исходного и бинарного изображения
		image = cv2.resize(frame, (256, 256))

		threshold = 0.5
		image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)# Переводим в цветовую палитру HSV
		matrix = np.zeros((256, 256), dtype='uint8')  #Создаем матрицу для бинарного изображения

		for i in range(image.shape[0]):
			for j in range(image.shape[1]):
				if image[i,j][0]>mini and image[i,j][0]<maxi: # Заполняем матрицу бинарного изображения в тех пикселях, где на основном изображении цвет лежит в указанном диапазоне
					matrix[i,j] = 255
		cur_summ = calculate_area(matrix, ref_points) #Вычисляем текущую заполняемость квадрата

		procent = area_ratio(ref_summs, cur_summ) # Процент заполняемости относительно исходного кадра и дискретное заполнение (Разогнутый, Полусогнутый, Согнутый)
		print('procent',procent)

		matrix = cv2.cvtColor(matrix, cv2.COLOR_GRAY2BGR) #Переводим бинарное изображение в BGR для отрисовки зеленого цвета

		display_boxes(img_show,'image', ref_points, 640) #Открисовывем квадраты на исходном изображении
		display_boxes(matrix,'binary', ref_points, 256, True) #Открисовывем квадраты на бинарном изображении

		matrix = cv2.cvtColor(matrix, cv2.COLOR_BGR2GRAY) # Возвразаем бинарное изображение в оттенки серого
		s2 = time.time()
		print(s2-s1)
		if cv2.waitKey(200) & 0xFF == ord('q'): # Выход из программы при нажатии на клавишу q
			break
	


