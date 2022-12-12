import os
from os import listdir
from os.path import isfile, join
import cv2
import matplotlib.pylab as plt
from PIL import Image as PImage
from statistics import mean

def load_images(image_directory):
    images_list = listdir(image_directory)
    loaded_images = []
    for image in images_list:
        img = PImage.open(image_directory + image)
        loaded_images.append(img)
    return loaded_images, images_list

def display_nine(imgs):
    plt.figure(figsize=(10,10))
    for i in range(9):
        plt.subplot(3,3,i+1)
        plt.imshow(imgs[i])
    plt.show()
    return

def get_all_dimensions(image_directory, images_list):
    h_set = []
    w_set = []
    c_set = []
    for images in images_list:
        path = os.path.join(image_directory, images)
        h, w, c = _get_dimensions(path)
        h_set.append(h)
        w_set.append(w)
        c_set.append(c)
    #print(h_set)
    _plot_histogram(h_set, "Histogram of Image Heights")
    #print(w_set)
    _plot_histogram(w_set, "Histogram of Image Width")
    #print(c_set)
    #_plot_histogram(c_set, "Histogram of Image Channels")
    avg_h = mean(h_set)
    print("The average height of the dataset images is:", round(avg_h, 2))
    avg_w = mean(w_set)
    print("The average width of the dataset images is:", round(avg_w, 2))
    return

def _get_dimensions(path):
    im = cv2.imread(path)
    #print(type(im))
    dims = im.shape
    #print(im.shape)
    #print(type(im.shape))
    return dims

def _plot_histogram(input_data, plot_title):
    plt.hist(input_data, 10)
    plt.title(plot_title)
    plt.show()
    return

def main():
    image_directory = 'character_recognition\\images\\'
    image_names = [f for f in listdir(image_directory) if isfile(join(image_directory, f))]
    #for i in image_names:
        #print(i)
    imgs, images_list = load_images(image_directory)
    #display_nine(imgs)
    get_all_dimensions(image_directory, image_names)
    return
    
    
if __name__ == '__main__':
	main()