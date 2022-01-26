class Invoice:
    x = 0  # Text coordinate x
    y = 0  # Text coordinate y
    width = 0  # Text width
    height = 0  # Text height
    conf = 0  # Text confidence
    text = None  # Text Recognized

    def __init__(self, x=0, y=0, width=0, height=0, conf=0, text=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.conf = conf
        self.text = text

    '''
    Assign the coordinate for each recognize text.
    '''
    def assignCoordinate(self, df):
        body = []
        for index in df.index:
            self.x = df.loc[index, 'left']
            self.y = df.loc[index, 'top']
            self.width = df.loc[index, 'width']
            self.height = df.loc[index, 'height']
            self.conf = df.loc[index, 'conf']
            self.text = df.loc[index, 'text']
            # print(f'x: {self.x}, y: {self.y}, width: {self.width}, height: {self.height}, conf: {self.conf}, text: {self.text}, id: {self.identity}')
            invoice = Invoice(self.x, self.y, self.width, self.height, self.conf, self.text)
            body.append(invoice)
        return body

    def allocateContent(self):
        pass

    def __str__(self):
        return f'x: {self.x}, y: {self.y}, width: {self.width}, height: {self.height}, conf: {self.conf}, ' \
               f'text: {self.text}'
