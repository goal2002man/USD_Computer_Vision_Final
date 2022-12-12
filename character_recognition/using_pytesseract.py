# Download and install tesseract
# https://codetoprosper.com/tesseract-ocr-for-windows

# Within the character_recognition folder, create the following folders:
# denoise
# gray

# Identify folder of images to process: for this example it was a folder titled "images" - raw_image_path

# Paths in Main will need to be updated based on local paths- 
# Next time may be best to use amazon S3 buckets for data as the free
# Github version limits upload sizes.

import pytesseract as pt
import os
import cv2
import matplotlib.pyplot as plt

def _list_of_images(path, full_temp_path):
	#Clear the output file before adding to it
	open(full_temp_path, 'w').close()
	list_of_input_paths = []

	#Create text file and list of paths
	for imageName in os.listdir(path):
		#Write to text file
		input_path = os.path.join(path, imageName)	
		file1 = open(full_temp_path, "a+")
		file1.write(imageName+"\n")
		file1.close()

		#Create a lsit of input image paths
		list_of_input_paths.append(input_path)
	return list_of_input_paths

def _convert_to_gray(image_list, gray_path):
	gray_directory = gray_path

	for image in image_list:
		filename = os.path.split(image)
		filename = filename[1]
		#print(filename)
		os.chdir(gray_directory)
		img = cv2.imread(image, 0)
		cv2.imwrite(filename, img)
	
		#plt.imshow(img, cmap='gray')
		#plt.show()
	return

def _denoising(image_list, denoising_image_path, gray_image_path):
	denoise_directory = denoising_image_path
	gray_directory = gray_image_path

	for image_name in image_list:
		os.chdir(gray_directory)
		filename = os.path.split(image_name)
		filename = filename[1]
		image = cv2.imread(filename)
		img = cv2.GaussianBlur(image, (5, 5), 0)
		os.chdir(denoise_directory)
		cv2.imwrite(filename, img)
	return

def preprocessing(raw_path, raw_fullTempPath, gray_path, denoising_image_path):
	image_list = _list_of_images(raw_path, raw_fullTempPath)
	_convert_to_gray(image_list, gray_path)
	_denoising(image_list, denoising_image_path, gray_path)
	return image_list

def convert_to_string(image_list, denoising_image_path, output_file_directory):
	denoise_directory = denoising_image_path
	output_file = output_file_directory
	open(output_file, 'w').close()

	for image in image_list:
		os.chdir(denoise_directory)
		img = cv2.imread(image)

		# applying ocr using pytesseract for python
		text = pt.image_to_string(img, lang = 'eng')

		filename = os.path.split(image)
		filename = filename[1]

		# providing the name of the image
		file1 = open(output_file, "a+")
		file1.write(filename+"\n")

		# providing the content in the image
		file1.write(text+"\n")		
	return

def main():
	# raw_image_path: str() Path to folder of images
	# raw_image_path: str() Path with file name to list images
	# gray_image_path: str() Path to save images that have been converted to grayscale
	# denoising_image_path: str() Path to save preprocessed images that have been denoised
	# output_file_directory: str() Path with file name to save image name and text conversion to
	raw_image_path =r"C:\Users\robas\Documents\San Diego U\06 Intro to Computer Vision Round 2\Final Project\USD_Computer_Vision_Final\character_recognition\images"
	raw_image_fullTempPath = r"C:\Users\robas\Documents\San Diego U\06 Intro to Computer Vision Round 2\Final Project\USD_Computer_Vision_Final\character_recognition\image_list"
	gray_image_path = r"C:\Users\robas\Documents\San Diego U\06 Intro to Computer Vision Round 2\Final Project\USD_Computer_Vision_Final\character_recognition\gray"
	denoising_image_path = r"C:\Users\robas\Documents\San Diego U\06 Intro to Computer Vision Round 2\Final Project\USD_Computer_Vision_Final\character_recognition\denoise"
	preprop_images = preprocessing(raw_image_path, raw_image_fullTempPath, gray_image_path, denoising_image_path)
	output_file_directory = r"C:\Users\robas\Documents\San Diego U\06 Intro to Computer Vision Round 2\Final Project\USD_Computer_Vision_Final\character_recognition\output_file"
	#convert_to_string(preprop_images, denoising_image_path, output_file_directory)

	convert_to_string(preprop_images, gray_image_path, output_file_directory)
	return

if __name__ == '__main__':
	main()
