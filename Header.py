from Invoice import Invoice


class Header(Invoice):
    counter = 0
    header_data = dict()

    def __init__(self, x=0, y=0, width=0, height=0, conf=0, text=None):
        super().__init__(x, y, width, height, conf, text)

    '''
    Execution function
    @param df
    @param counter
    @return self.header_data
    @return self.counter + 1
    '''
    def runner(self, df, counter):
        self.header_data.clear()
        self.counter = counter
        print('----------------------------------------This is Header----------------------------------------')
        print('-------------------------------------Assigning Coordinate-------------------------------------')
        data = super().assignCoordinate(df)
        print('--------------------------------------Allocating Content--------------------------------------')
        self.allocateContent(data)
        return self.header_data, self.counter + 1

    def allocateContent(self, texts_list=None):
        if texts_list is None:
            return

        ctn = False
        current = ''
        previous = ''
        current_line = 0

        for index1, ele1 in enumerate(texts_list):
            y1 = ele1.y

            if index1 == 0:
                current_line = y1
                current = ele1.text

            elif current == ':':
                current = ele1.text
                try:
                    if ele1.y - 10 <= texts_list[index1 + 1].y <= ele1.y + 10:
                        current += ' ' + texts_list[index1 + 1].text
                except IndexError:
                    pass
                self.header_data[previous] += current
                print(f'self.header_data[{previous}]: {self.header_data[previous]}')
                previous = current
                current = ''
                current_line = y1
                ctn = True

            elif ele1.text == ':':
                previous = current
                current = ele1.text
                self.header_data[previous] = '' if ele1.text == ':' else current
                print(f'self.header_data[{previous}]: {self.header_data[previous]}')

            elif previous == '' and current == '':
                current = ele1.text

            elif current_line - 10 <= y1 <= current_line + 10:
                current += ' ' + ele1.text

            elif ctn:
                previous = current
                current = ele1.text
                current_line = y1
                ctn = False
                continue

            else:
                self.header_data[self.counter] = current
                print(f'self.header_data[{self.counter}]: {self.header_data[self.counter]}')
                previous = current
                current = ele1.text
                self.counter += 1
                current_line = y1
                ctn = False

        if current != '':
            self.header_data[self.counter] = current

        print(self.header_data)

    def __str__(self):
        return super.__str__(self)
