"""
Data_Reading.py - contains functions and helpers to read in the data image data
for USD AAI 521 Computer Vision Final Project

Authors: Bryan Carr, Leya Joseph, Robert Salamon

Date: 7-12 Dec, 2022


"""

import numpy as np
import cv2
import os
from pathlib import Path
import pandas as pd

def parse_annotation(file_path):
    """
    parse_annotation: A helper function to parse the annotation files
        Reads in a text file as input
        Reads the lines as strings and splits the key ones by spaces
        Extracts the numbers for the bounding boxes, stored as (x, y, w, h)

    Input:
        file_path (String): file directory/pathway for the Text File containing the annotation

    Outputs:
        box_locations (array): An array containing all annotation box locations
            line [0] is the Car
            line [1] is the License Plate box
            Remaining lines are the boxes for characters on the plate
        plate (string): String containing the characters in the license plate

    :param file_path:
    :return:
    """

    with open(file_path, 'r') as f:
        lines = f.readlines() #Read in line by line
        f.close() #Close file when done

    # define car_box annotation:
    # the last 4 entries in the line (strings)
    # helper function converts to integers & array

    car_box = list_convert(lines[1].split()[1:5])

    plate_box = list_convert(lines[7].split()[1:5])

    box_locations = np.concatenate( ([car_box], [plate_box]), axis=0)

    plate = lines[6].split()[1]

    # Loop over the remaining lines - the plate characters - to build their boxes
    for l in lines[8:]:
        char_box = list_convert(l.split()[2:6])
        box_locations = np.append(box_locations, [char_box], axis=0)


    """
    print(car_box)
    print(type(car_box))
    print(plate)
    print(plate_box)
    print(box_locations)
    """

    return box_locations, plate


def list_convert(list):
    """
    list_convert: a helper function to convert a list of Strings to an Array of Integers

    input: list (strings) - a list of numbers in string dtypes

    return: converted_array (array) - the same list, converted to an Array of Integer dtypes
    """
    converted_array = np.array([int(i) for i in list])

    return converted_array

def draw_boxes(boxes, img):
    """
    draw_boxes: a function to plot the annotation boxes onto an image

    input: boxes (array): numpy array of box annotations, as generated by the parse_annotation function
        i.e. original format of annotations

        image_path (string): pathway to the image file where boxes will be plotted on

    outputs: draws the image with the box annotations on it

    :param boxes:
    :param image_path:
    :return:
    """
    # img = cv2.imread(image_path)

    for row in boxes:
        x, y, w, h = row
        cv2.rectangle(img, (x,y), (x+w, y+h), (255,0,0), 1)

    cv2.imshow('image', img)

    cv2.waitKey(0)

def convert_image_and_annotation(source_path, file_name):
    """
    A function to resize the image and convert its annotation into YOYOv5-friendly format.

    Input:
        source_path (string): the path to the image and text annotation file, not including file name

        file_name (string): name of the image file

    Output:
        crop (cv2 image): Cropped image centered on the main detection box for 'Car'
        cent_boxes (array): Array of the centered boxes for Car, Plate and Characters,
            sized for the new cropped image
    """

    img_path = source_path + file_name

    # read in original image
    img = cv2.imread(img_path)

    # get original image dimensions
    height = img.shape[0]
    width = img.shape[1]

    # new dimensions after rescaling/cropping
    new_height = 480
    new_width = 640

    # replace 'png' extension with 'txt' and parse to collect original Annotations
    annotation_path = img_path[:-3] + 'txt'
    old_annotations, plate_chars = parse_annotation(annotation_path)

    # We need to set up coords in both image 'systems'
    # the 'Old' coords refer to 1920x1080
    # the 'New' coords refer to 640x480, or other new dimensions defined
    old_centre_x = old_annotations[0][0] + (old_annotations[0][2] / 2)
    old_centre_y = old_annotations[0][1] + (old_annotations[0][3] / 2)

    old_x1 = max( int(old_centre_x - (new_width / 2) ), 0)
    old_y1 = max( int(old_centre_y - (new_height / 2) ), 0)

    # translate the old boxes into the new, smaller size
    new_boxes = np.empty( [0,4], int)
    for row in old_annotations:
        new_x = row[0] - old_x1
        new_y = row[1] - old_y1

        new_boxes = np.append(new_boxes, np.array([[new_x, new_y, row[2], row[3]]]), axis=0)

    # translate boxes into centered, percentage-sized ones
    cent_boxes = np.empty([0,4], float)
    for row in new_boxes:
        new_cent_x = row[0] / new_width
        new_cent_y = row[1] / new_height
        new_cent_w = row[2] / new_width
        new_cent_h = row[3] / new_height

        #if box out of bounds, set to centered & max size -- will help for some large vehicles
        if new_cent_x < 0:
            new_cent_x = 0.5
            new_cent_w = 0.999
        if new_cent_y < 0:
            new_cent_y = 0.5
            new_cent_w = 0.999

        #write, including minimums for width and height - again will help with large vehicles
        cent_boxes = np.append(cent_boxes, np.array([[new_cent_x, new_cent_y, min(new_cent_w, 0.999), min(new_cent_h,0.999 )]]), axis=0)

#    print(cent_boxes)

    # crop the image
    crop = img[old_y1: (old_y1+new_height), old_x1: (old_x1+new_width)]

    ###############################
    ##### UN COMMENT THIS LINE TO VIEW CROPPED IMAGES ON BOXES FOR TESTING
    ###############################
#    draw_boxes(new_boxes, crop)

    return crop, cent_boxes

def write_text_annotation(boxes, file_name):
    """
    write_text_annotation: writes the annotation toa  .txt file, in the current directory

    Inputs:
        boxes (array): locations of the detection boxes, in YOLOv5-friendly centered and scaled format

        file_name (string): name of file to be written. SHould be same as image.
            Can be the image name, as the extension will be replaced with '.txt' in this function

    Outputs:
            writes the text file in the current directory
    """
    #write the annotation file
    with open(file_name[:-3] + 'txt', 'w') as f:
        # convert to loop over rows
        # first char, for label: incrimenter, write max of (inc, 2) as 2 is last char (for Character on Plate)
        inc = 0
        for row in boxes:
            # write the label character
            f.write(str(min(inc,2)) + ' ')

            #write the contents of the centered box
            for i in row:
                f.write(str(i) + ' ')

            # increase incrimenter for next row, and add a line break
            inc += 1
            f.write('\n')


        f.close()

    return


label_dict = {
    0 : 'car',
    1 : 'plate',
    2 : 'character'
}

def make_directories():
    """
    Helper function to make directories for our target data

    Returns: Nil
    Outputs: File structure is created using hard-coded paths
    """
    p = Path('C:/Users/bcarr/Documents/GitHub/USD_Computer_Vision_Final/data/train/images')
    p.mkdir(exist_ok=True, parents=True)

    p = Path('C:/Users/bcarr/Documents/GitHub/USD_Computer_Vision_Final/data/train/labels')
    p.mkdir(exist_ok=True, parents=True)

    p = Path('C:/Users/bcarr/Documents/GitHub/USD_Computer_Vision_Final/data/test/images')
    p.mkdir(exist_ok=True, parents=True)

    p = Path('C:/Users/bcarr/Documents/GitHub/USD_Computer_Vision_Final/data/test/labels')
    p.mkdir(exist_ok=True, parents=True)

    return

def convert_dataset(source_dir, new_dir = r'C:/Users/bcarr/Documents/GitHub/USD_Computer_Vision_Final/data/test/'):
    """
    convert_dataset: Function to convert the data to the smaller, yolo-friendly format

    Inputs:
        source_dir (string): pathway for the source directory

        new_dir (string): pathway for the destination directory
            Defaults to the desired pathway on my local drive

    Outputs:
        nil Returns
        Writes the Image to new_dir/images
        Writes the Text Annotation to new_dir/labels
    """
    # search for all subdirectories
    directory_list = os.listdir(source_dir)

    for dir in directory_list:
        pathway = source_dir + '/' + dir + '/'

        #first search for all images in the input directory
        png_list = [f for f in os.listdir(pathway) if (f[-3:] == 'png')]

        for f in png_list:
            image, boxes = convert_image_and_annotation(pathway, f)

            #write cropped image to new directory
            os.chdir(new_dir + 'images/')
            cv2.imwrite(f, image)

            #write text annotations
            os.chdir(new_dir + 'labels/')
            write_text_annotation(boxes, f)

        #feedback on progress
        print('finished with directory: ' + str(dir))



    return

def crop_plate(source_dir = r'C:/Users/bcarr/Documents/USD AAI/AAI 521 Computer Vision/UFPR-ALPR/UFPR-ALPR dataset',
               output_dir = r'C:\Users\bcarr\Documents\GitHub\USD_Computer_Vision_Final'):
    """
    crop_plate: a function to crop out the plates ONLY

    Inputs:
        source_dir (string): the source directory for folders to be searched, with structure:
            source_dir/training/ <run> / <images and annotation here>
            source_dir/validation/ <run> / <images and annotation here>
            source_dir/testing/ <run> / <images and annotation here>

        image (cv2 image): the file of the image to be read and cropped

        boxes (array): the bounding boxes from annotations
            'old' full resolution format

        plate (string): the string annotation for the plate

    Outputs:
        nil Returns
        writes

    """

    #set up output directory
    os.chdir(output_dir + '/plates/')
    #os.mkdir('plates')

    #initialize pandas dataframe to store plates
    plate_df = pd.DataFrame(columns=['file_name', 'plate_chars'])

    #search for sub directories in source dir
    sub_dirs = os.scandir(source_dir)
    for dir in sub_dirs:
        if dir.is_dir():
            directory_list = os.scandir(dir.path)
            for subdir in directory_list:
                # get list of files
                file_list = os.listdir(subdir.path)

                #take first file
                file_name = file_list[0]
                text_name = file_name[:-3] + 'txt'
                img_name = file_name[:-3] + 'png'

                box, plate = parse_annotation(subdir.path +'/'+ text_name)

                plate_df = plate_df.append({'file_name' : img_name, 'plate_chars' : plate}, ignore_index=True)

                img = cv2.imread(subdir.path + '/' + img_name)

                crop = [] #reset the Cropped image
                crop = img[box[1][1] : (box[1][1] + box[1][3]), box[1][0]: (box[1][0] + box[1][2])]

                cv2.imwrite(img_name, crop)

    plate_df.to_csv('plate_chars.csv')




#    print(sub_dirs)

    return


#use the r character to read the string exactly as printed
# otherwise Python will attempt to interpret the backslashes as special characters/commands
# better to replace all the Backslashes with Forward Slashes - python works better with them
#test_path = r"C:\Users\bcarr\Documents\USD AAI\AAI 521 Computer Vision\UFPR-ALPR\UFPR-ALPR dataset\training\track0001\track0001[01].txt"

#test_img_path = r"C:\Users\bcarr\Documents\USD AAI\AAI 521 Computer Vision\UFPR-ALPR\UFPR-ALPR dataset\training\track0001\track0001[01].png"

#annotations, plate = parse_annotation(test_path)

#draw_boxes(annotations, test_img_path)

#test_path2 = r"C:/Users/bcarr/Documents/USD AAI/AAI 521 Computer Vision/UFPR-ALPR/UFPR-ALPR dataset/training/track0006/"
#test_fn = r'track0006[01].png'
#write_text_annotation(boxes, test_fn)

import os
print(os.getcwd())

# Run this once to create the required directories
#make_directories()

# For building the dataset in the newly made directories above
# Adjust pathways manually, as needed, for additional runs
#convert_dataset(r"C:/Users/bcarr/Documents/USD AAI/AAI 521 Computer Vision/UFPR-ALPR/UFPR-ALPR dataset/testing")

crop_plate()

