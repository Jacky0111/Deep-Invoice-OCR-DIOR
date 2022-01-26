import os
import re
import wx
import numpy as np

from pathlib import Path
from datetime import datetime
from cv2 import cv2
from PIL import Image
from pdf2image import convert_from_path

from OCR import OCR
from yolov5.Detect import Detect


class main:
    data = []
    images = []  # To store the image converted from chosen invoice
    dataset_images = []  # To store the entire converted samples data
    invoice = None  # Chosen invoice
    img_counter = 0
    file_name = None
    folder_path = None
    dataset_path = None
    samples_data_path = None

    def __init__(self):
        pass

    '''
    Execution function
    '''
    def runner(self):
        choice = self.menu()

        if choice == 1:
            print('--------------------------------------Generating Dataset--------------------------------------')
            self.setDatasetPath()
            current_path = os.getcwd()
            current_path = os.path.abspath(os.path.join(current_path, "../Samples Data"))
            self.data = next(os.walk(current_path), (None, None, []))[2]
            for index, file in enumerate(self.data):
                print(index, file)
                self.convertToImage(f'{current_path}\\{file}', 'dataset')

        elif choice == 2:
            print('----------------------------------------Choosing File-----------------------------------------')
            invoice_path = self.chooseFile()
            print('-----------------------------------Converting PDF to image------------------------------------')
            self.invoice = self.convertToImage(invoice_path, 'ocr')
            self.images.append(self.invoice if isinstance(self.invoice, list) else [self.invoice])
            print('---------------------------------Predicting Header & Content----------------------------------')
            header_content = Detect.parseOpt(self.folder_path)

            head_path = os.path.split(header_content[0])[0]
            tail_path = os.path.split(header_content[0])[1]
            if re.search('content', tail_path):
                header_content = self.reassign(header_content)

            ocr = OCR(head_path)
            for i, image in enumerate(header_content):
                ocr.runner(image)

    '''
    Serialize the order of the list passed from parseOpt(saved_path).
    @return reassigned
    '''
    @staticmethod
    def reassign(ori):
        h = []
        c = []
        reassigned = []

        for path in ori:
            if re.search('head', path):
                h.append(path)
            elif re.search('content', path):
                c.append(path)

        for (a, b) in zip(h, c):
            reassigned.append(a)
            reassigned.append(b)

        return reassigned

    '''
    A main menu that allows user to choose either create a dataset or run ocr.
    @return int
    '''
    @staticmethod
    def menu():
        print('MAIN MENU')
        print('=========')
        print('1. Create Dataset')
        print('2. Run OCR')
        return int(input('Enter your choice: '))

    '''
    Select any file locally by popping up a window.
    @return path
    '''
    @staticmethod
    def chooseFile():
        app = wx.App(None)
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        dialog = wx.FileDialog(None, 'Open', style=style)

        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
        else:
            path = None
        dialog.Destroy()

        return path

    '''
    Set the dataset path name
    '''
    def setDatasetPath(self):
        self.dataset_path = r'Dataset/samples_data'
        try:
            os.makedirs(self.dataset_path)
        except FileExistsError:
            pass

    '''
    Set the folder name for each run of the OCR process inside the “Images” folder.
    @param dir
    '''
    def setFolderName(self, dir):
        if os.path.split(os.getcwd())[1] == 'yolov5':
            os.chdir(os.path.dirname(os.getcwd()))

        self.folder_path = r'/Images/' + Path(dir).stem + '_' + str(
            datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
        self.folder_path = os.getcwd() + self.folder_path
        os.makedirs(self.folder_path)

        try:
            os.chdir('yolov5')
        except FileNotFoundError:
            pass

    '''
    Convert the files to the PNG images format
    @param dir
    @param purpose
    '''
    def convertToImage(self, dir, purpose):
        file_type = os.path.splitext(dir)[1][1:]

        if self.isImageType(file_type)[0]:
            img = Image.open(dir)
        else:
            img = convert_from_path(pdf_path=dir,
                                    poppler_path=r'C:\Program Files\poppler-0.68.0\bin')

        if purpose == 'ocr':
            self.setFolderName(dir)

        self.outputImage(dir, file_type, img, purpose)
        return img

    '''
    Determine whether the file type is image
    @param file_type
    @return isImage
    @return specialFormat
    '''
    @staticmethod
    def isImageType(file_type):
        if (file_type == 'rgb' or
                file_type == 'jpg' or
                file_type == 'jpeg' or
                file_type == 'png' or
                file_type == 'bmp'):
            isImage = True
            specialFormat = False
        elif (file_type == 'tif' or
              file_type == 'tiff'):
            isImage = True
            specialFormat = True
        else:
            isImage = False
            specialFormat = True

        return isImage, specialFormat

    '''
    Store the input images
    @param directory
    @param file_type
    @param image
    @param purpose
    '''
    def outputImage(self, directory, file_type, image, purpose):
        img_path = self.dataset_path if purpose == 'dataset' else f'{self.folder_path}/page'
        file_type = f'.{file_type if not self.isImageType(file_type)[1] else "png"}'

        if isinstance(image, list):
            for i in range(len(image)):
                img = np.array(image[i])
                if purpose == 'dataset':
                    self.img_counter += 1
                    cv2.imwrite(img_path + '/' + str(self.img_counter) + file_type, img)
                else:
                    cv2.imwrite(img_path + str(i + 1) + file_type, img)
        else:
            im = Image.open(directory)
            im = im.copy()
            if purpose == 'dataset':
                self.img_counter += 1
                im.save(f'{img_path}/{str(self.img_counter)}{file_type}')
            else:
                im.save(f'{img_path}{file_type}')

