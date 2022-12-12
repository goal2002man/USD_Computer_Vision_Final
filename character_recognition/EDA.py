import os
from os import listdir
from os.path import isfile, join
import cv2
import matplotlib.pylab as plt
from PIL import Image as PImage
from statistics import mean
import numpy as np
from scipy import stats
import random

def load_images(image_directory):
    images_list = listdir(image_directory)
    loaded_images = []
    for image in images_list:
        img = PImage.open(image_directory + image)
        loaded_images.append(img)
    return loaded_images, images_list

def display_nine(imgs, plot_name):
    plt.figure(figsize=(10,10))
    for i in range(9):
        plt.subplot(3,3,i+1)
        plt.imshow(random.choice(imgs))
    plt.savefig(plot_name)
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
    _plot_histogram(h_set, "Histogram of Image Heights", "height_histogram.png")
    #print(w_set)
    _plot_histogram(w_set, "Histogram of Image Width", "width_histogram.png")
    #print(c_set)
    #_plot_histogram(c_set, "Histogram of Image Channels")
    avg_h = np.mean(h_set)
    median_h = np.median(h_set)
    mode_h = stats.mode(h_set, keepdims=True)
    print("The average height of the dataset images is:", round(avg_h, 2))
    print("The median height of the dataset images is:", round(median_h, 2))
    print("The mode height of the dataset images is:", mode_h)
    print("The min height of the dataset images is:", min(h_set))
    print("The max height of the dataset images is:", max(h_set), "\n")
    avg_w = mean(w_set)
    median_w = np.median(w_set)
    mode_w = stats.mode(w_set, keepdims=True)
    print("The average width of the dataset images is:", round(avg_w, 2))
    print("The median width of the dataset images is:", round(median_w, 2))
    print("The mode width of the dataset images is:", mode_w)
    print("The min width of the dataset images is:", min(w_set))
    print("The max width of the dataset images is:", max(w_set))
    return

def _get_dimensions(path):
    im = cv2.imread(path)
    #print(type(im))
    dims = im.shape
    #print(im.shape)
    #print(type(im.shape))
    return dims

def _plot_histogram(input_data, plot_title, plot_name):
    plt.hist(input_data, 10)
    plt.title(plot_title)
    plt.savefig(plot_name)
    plt.show()
    return

def main():
    image_directory = 'character_recognition\\plates\\'
    image_names = [f for f in listdir(image_directory) if isfile(join(image_directory, f))]
    #for i in image_names:
        #print(i)
    imgs, images_list = load_images(image_directory)
    display_nine(imgs, "original_images.png")
    get_all_dimensions(image_directory, image_names)
    return
    
    
if __name__ == '__main__':
	main()