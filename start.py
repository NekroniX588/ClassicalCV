import cv2
import matplotlib.pyplot as plt
import numpy as np
import time as t
import math
import imutils
import tkinter as tk
from PIL import Image, ImageTk

cap = cv2.VideoCapture(0) #Делаем захват изображения с камеры

def get_frame(mininum, maximum): #Функция, которая получает кадр с камеры
	ret, frame = cap.read() #Считываем кадр с камеры
	frame = cv2.flip(frame, 1)
	image = cv2.resize(frame, (256, 256), interpolation = cv2.INTER_AREA)#Переводим кадр в размеры 128, 128
	image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)# Переводим в цветовую палитру HSV
	matrix = np.zeros((256, 256), dtype='uint8')  #Создаем матрицу для бинарного изображения

	for i in range(image.shape[0]):
		for j in range(image.shape[1]):
			if image[i,j][0]>mininum and image[i,j][0]<maximum: # Заполняем матрицу бинарного изображения в тех пикселях, где на основном изображении цвет лежит в указанном диапазоне
				matrix[i,j] = 255
	# cv2.imwrite('1.jpg', frame)
	matrix_RGB = cv2.cvtColor(matrix, cv2.COLOR_GRAY2BGR) #Переводим бинарное изображение в BGR

	return frame, matrix_RGB 

class Application(tk.Frame):  # Класс в котором содержаться все виджеты 
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.master = master
		self.pack()
		self.createWidgets() # При инициализации вызываем функцию, которая отприсовывает все виджеты

	def createWidgets(self): 
		
		image, matrix_RGB = get_frame(100, 120) #Получаем изображение с камеры и бинарное изображение руки
		cv2_im1 = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
		cv2_im2 = cv2.cvtColor(matrix_RGB,cv2.COLOR_BGR2RGB)
		pil_im1 = Image.fromarray(cv2_im1)
		pil_im2 = Image.fromarray(cv2_im2)
		img = ImageTk.PhotoImage(pil_im1) #Переводим в формат PIL
		img_bi = ImageTk.PhotoImage(pil_im2) #Переводим в формат PIL
		self.panel = tk.Label(self, image=img) #Создаеам область для открисовки изображений
		self.panel.pack(side = tk.LEFT)
		self.pane2 = tk.Label(self, image=img_bi)#Создаеам область для открисовки изображений
		self.pane2.pack(side = tk.BOTTOM)
		self.w1 = tk.Scale(self, from_=0, to=179, orient=tk.HORIZONTAL)#Создаем слайдеры для настройки изображения
		self.w1.set(100) #Выставляем начальные значения слайдера
		self.w1.pack(side = tk.BOTTOM)
		self.w2 = tk.Scale(self, from_=0, to=179, orient=tk.HORIZONTAL)#Создаем слайдеры для настройки изображения
		self.w2.set(120)#Выставляем начальные значения слайдера
		self.w2.pack(side =tk.BOTTOM)

		

		self.QUIT = tk.Button(self, text="Make photo", fg="red",    #Создаем кнопку для фотографии
		                                    command=self.make_photo) 
		self.QUIT.pack(side=tk.BOTTOM)
		# initial time display
		self.onUpdate()

	def onUpdate(self):  # Отрисовываем каждое новое иображение в окне
		image, matrix_RGB = get_frame(self.w1.get(),self.w2.get())  #Получаем изображение с камеры и бинарное изображение руки
		cv2_im1 = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
		cv2_im2 = cv2.cvtColor(matrix_RGB,cv2.COLOR_BGR2RGB)
		pil_im1 = Image.fromarray(cv2_im1)
		pil_im2 = Image.fromarray(cv2_im2)
		img = ImageTk.PhotoImage(pil_im1)#Переводим в формат PIL
		img_bi = ImageTk.PhotoImage(pil_im2)#Переводим в формат PIL
		self.panel.configure(image=img)#отрисовываем изображение
		self.panel.image = img
		self.pane2.configure(image=img_bi)#отрисовываем изображение
		self.pane2.image = img_bi
		# schedule timer to call myself after 1 second
		self.after(10, self.onUpdate)

	def make_photo(self): #При нажании кнопи Make_photo записывается формат настроек слайдеров в файл и сохраняется изображение для дальнейшего выделения пальцев
		with open('settings.txt', 'w') as f:
			f.write(str(self.w1.get()) + ' ' + str(self.w2.get()) + '\n')
		image, matrix_RGB = get_frame(self.w1.get(),self.w2.get())
		cv2.imwrite('background.jpg',matrix_RGB)
		self.master.destroy()

def started():
	root = tk.Tk()
	app = Application(master=root)
	root.mainloop()

if __name__ == '__main__':
	started()