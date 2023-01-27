import re
import pytesseract
from cv2 import cv2

from Invoice import Invoice

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class Content(Invoice):
    TYPE_HEAD = 'head'  # Type of content
    TYPE_BODY = 'body'  # Type of content

    counter = 0
    identity = None  # Either header or content

    head = []  # First line of the table
    body = []  # Content of the table

    table_data = dict()  # Store the entire content

    def __init__(self, x=0, y=0, width=0, height=0, conf=0, text=None, identity=None, ):
        super().__init__(x, y, width, height, conf, text)
        self.head = []
        self.identity = identity

    '''
    Execution function
    @param df
    @param img
    @param counter
    @param save_path
    @return self.table_data
    @return self.counter + 1
    '''
    def runner(self, df, img, counter, save_path):
        self.table_data.clear()
        self.body.clear()
        self.counter = counter
        print('---------------------------------------This is Content----------------------------------------')
        print('-------------------------------------Assigning Coordinate-------------------------------------')
        whole = super().assignCoordinate(df)
        print('------------------------------------Identifying Text Type-------------------------------------')
        while True:
            self.identifyTextType(whole)
            if self.isHeader(img):
                break
            whole = self.body
            self.head.clear()
            self.body = []
        if self.head:
            print('--------------------------------------Readjusting Header--------------------------------------')
            self.readjustTableHeader(img, save_path)
            for ele in self.head:
                print(ele)
        print('--------------------------------------Allocating Content--------------------------------------')
        self.allocateContent()
        return self.table_data, self.counter + 1

    '''
    Identify the type of the recognized text. Either is HEAD or BODY.
    @param data
    '''
    def identifyTextType(self, data):
        min_y = 0
        first_line = 0
        previous = None

        if not self.head:
            for i, row in enumerate(data):
                if i == 0:
                    first_line = row.y
                    row.identity = self.TYPE_HEAD
                    previous = row
                    self.head.append(row)
                elif first_line - 20 <= row.y <= first_line + 20:
                    row.identity = self.TYPE_HEAD
                    if previous is not None and row.x - (previous.x + previous.width) <= 30:
                        self.head[-1].text += ' ' + row.text
                        self.head[-1].width += row.x - (previous.x + previous.width) + row.width
                        previous = row
                    else:
                        self.head.append(row)
                        print(row.text)
                else:
                    row.identity = self.TYPE_BODY
                    self.body.append(row)
                    continue
                previous = row

        else:
            for i, row in enumerate(data):
                if i == 0:
                    min_y = row.y
                elif min_y == 0:
                    break
                elif row.y < min_y:
                    min_y = row.y

            for i, row in enumerate(data):
                if row.y > min_y + 20:
                    self.body.append(row)

    '''
    Readjust the coordinate of the table header
    @param img
    @param path
    '''
    def readjustTableHeader(self, img, path):
        temp_x = 0
        temp_width = 0
        black = (0, 0, 0)
        font = cv2.FONT_HERSHEY_SIMPLEX

        for i, ele in enumerate(self.head):
            if i == 0:
                ele.width = (ele.x - 0) * 2 + ele.width
                ele.x = 0
                temp_x = ele.x
                temp_width = ele.width
            elif i == len(self.head) - 1:
                ele.width = ele.x - (temp_x + temp_width) + ele.width + (img.shape[1] - ele.x - ele.width)
                ele.x = temp_x + temp_width
            else:
                ele.width = (ele.x - (temp_x + temp_width)) * 2 + ele.width
                ele.x = temp_x + temp_width
                temp_x = ele.x
                temp_width = ele.width

        self.isOverlapped(img.shape[1])

        for ele in self.head:
            table = cv2.rectangle(img, (ele.x, ele.y), (ele.x + ele.width, ele.y + ele.height), (255, 0, 0))
            cv2.putText(table, f'({str(ele.x)},{str(ele.y)}) to ({str(ele.x + ele.width)}, {str(ele.y + ele.height)})',
                        (ele.x, ele.y + 20 + ele.height), font, 0.5, black, 1)
            cv2.imwrite(f'{path}\\table.png', table)

    '''
    Determine whether the coordinate of the table header text is overlapped.
    Looking for the width with negative value.
    x1 = x
    x2 = x + width
    @param img_width
    '''
    def isOverlapped(self, img_width):
        for i in range(len(self.head) - 1):
            try:
                # Check whether the width is negative to determine the coordinate is overlapped
                if self.head[i].width < 0:
                    # Assign current(x2) to current(x1)
                    self.head[i].x = self.head[i].x + self.head[i].width
                    # Invert the current width
                    self.head[i].width = -self.head[i].width
                    # Assign to next(x1) with the updated current(x1) + current(width)
                    self.head[i + 1].x = self.head[i].x + self.head[i].width
                    # next(width) = next(x2) - next(x1)
                    temp_width = self.head[i + 2].x - self.head[i + 1].x
                    extra_width = self.head[i + 1].width - temp_width
                    self.head[i + 1].width = temp_width - extra_width
            except IndexError:
                pass

        for i in range(len(self.head) - 1, -1, -1):
            try:
                if i == len(self.head) - 1 and self.head[i].x != self.head[i - 1].x + self.head[i - 1].width:
                    self.head[i].x = self.head[i - 1].x + self.head[i - 1].width
                    self.head[i].width = img_width - self.head[i].x

                # Check whether the current(x2) is similar to next(x1), current(x2) = next(x1)
                elif self.head[i].x + self.head[i].width != self.head[i + 1].x:
                    temp_width = self.head[i + 1].x - self.head[i].x  # 401
                    extra_width = self.head[i].width - temp_width     # 145
                    self.head[i].x = self.head[i].x + extra_width     # 777
                    self.head[i].width = temp_width - extra_width     # 1033
                    self.head[i - 1].width = self.head[i].x - self.head[i - 1].x

            # Last element of the list will cause IndexError
            except IndexError:
                pass

    '''
    Allocate the content to respective header
    '''
    def allocateContent(self):
        row_dict = dict()  # Store current row data
        current = ''       # Current text
        previous = ''      # Previous text
        temp_y = []        # Store previous y from body
        prev_count = 0     # Previous row counter
        self.table_data[self.counter] = dict.fromkeys([i.text for i in self.head],
                                                      None)  # Initialize the key of the dict

        for index1, ele1 in enumerate(self.body):
            x1 = ele1.x
            y1 = ele1.y
            width1 = ele1.width
            x_width_1 = x1 + width1

            if index1 == 0:
                temp_y.append(ele1.y)
                # Initialize the key of the row_dict
                row_dict = dict.fromkeys([i.text for i in self.head], None)

            for index2, ele2 in enumerate(self.head):
                x2 = ele2.x
                width2 = ele2.width
                x_width_2 = x2 + width2

                try:
                    # Check whether the body text is within current header
                    if x2 <= x_width_1 <= x_width_2 or x2 <= x1 <= x_width_2 or width1 > width2:
                        if x2 <= x_width_1 <= x_width_2 and x2 <= x1 <= x_width_2:
                            pass
                        elif (x_width_2 - x1) > (x_width_1 - self.head[index2 + 1].x):
                            pass
                        else:
                            continue
                    else:
                        continue
                except IndexError:
                    pass

                # Check whether current and previous header are same. True, then combine both text
                if previous == ele2.text:
                    try:
                        if ele1.text[0] == '.' or self.body[index1 - 1].text[-1] == '.' or \
                                (re.search('\.', ele1.text) and isinstance(int(ele1.text[0]), int)):
                            current += ele1.text
                        elif isinstance(int(ele1.text), int) and 10 <= int(ele1.text) <= 99:
                            current += '.' + ele1.text
                        else:
                            current += ' ' + ele1.text
                    except ValueError:
                        current += ' ' + ele1.text
                        pass
                else:
                    current = ele1.text
                    previous = ele2.text

                if prev_count != self.counter:
                    temp_y.append(ele1.y)

                prev_count = self.counter

                # Increase row counter when the body text is out of current acceptable range
                self.counter += 0 if temp_y[-1] - 20 <= ele1.y <= temp_y[-1] + 20 else 1

                print('-----------------------------------------------')
                print(f'current y: {ele1.y}, standard y: {temp_y[-1]}')

                # If row counter is increased, row_dict has to be initialized.
                if prev_count != self.counter:
                    # When the first or second column is None
                    if (row_dict[self.head[0].text] is None or row_dict[self.head[1].text] is None) and \
                            ele1.y - temp_y[-1] > 20:
                        # temp_y.pop()
                        prev_count -= 1
                        self.counter -= 1

                        try:
                            row_dict[ele2.text] = current
                            self.table_data[self.counter - 1] = Content.update(self.table_data[self.counter - 1],
                                                                               row_dict)
                            print(f'self.table_data[{self.counter - 1}]: {self.table_data[self.counter - 1]}')
                            current = ''
                            self.table_data.popitem()
                        except KeyError:
                            pass
                    row_dict = dict.fromkeys([i.text for i in self.head], None)

                # Store value into particular key. Store the current text once it is None. Else, store the combination text
                row_dict[ele2.text] = ele1.text if row_dict[ele2.text] is None else current

                # Store current record into self.table_data`
                self.table_data[self.counter] = row_dict
                print(f'row_dict[{ele2.text}]: {row_dict[ele2.text]}')
                print(f'self.table_data[{self.counter}]: {self.table_data[self.counter]}')
                print()
                break

    '''
    Determine the authenticity of the detected header
    @param img
    @return True if the last element is large than image width divide by 2, False otherwise
    '''
    def isHeader(self, img):
        width = img.shape[1]
        last = self.head[-1]
        return True if last.x >= width / 2 else False

    '''
    Check whether all elements in within are None
    @param dict_to_check
    @return True if there are all None elements within the list, False otherwise.  
    '''
    @staticmethod
    def checkAllNone(dict_to_check):
        for value in dict_to_check.values():
            if value is not None:
                return False
        return True

    '''
    Update multiple lines data in a row
    @param d1
    @param d2
    @return d3
    '''
    @staticmethod
    def update(d1, d2):
        d3 = dict()
        update = ''

        for key1, key2 in zip(d1.keys(), d2.keys()):
            old = d1[key1]
            new = d2[key2]

            try:
                if old == new or new is None:
                    update = old
                elif old in new:
                    update = new
                elif new is not None or old != new:
                    update = old + ' ' + new
            except TypeError:
                update = new

            d3.update({key1: update})
        return d3

    def __str__(self):
        return f'{super.__str__(self)}, id: {self.identity}'
