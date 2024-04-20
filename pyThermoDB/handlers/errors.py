

class errHandler(Exception):
    def __init__(self, *args: object):
        if args:
            self.message = args[0]
        else:
            self.message = None


class errGeneral(Exception):
    def __init__(self, errCode, errMessage):
        super().__init__(self, errMessage)
        self.errCode = errCode
        self.errMessage = errMessage

    def __str__(self):
        print('errGeneralClass')
        if self.errMessage:
            return f'errGeneralClass, {self.errMessage} {self.errCode}, {self.errType()}'
        else:
            return 'errGeneralClass has not raised'
        
    def errType(self):
        if self.errCode == 1:
            return 'errGeneralClass'
        elif self.errCode == 2:
            return 'errGeneralClass'
        elif self.errCode == 3:
            return 'errGeneralClass'
        

