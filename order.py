# Model cho order lấy từ mail
import re
from datetime import datetime


class Order:
    def __init__(self):
        self.SalesClassification = ["Sales Classification", "", "dropdown"]
        self.UserProjectCode = ["User Project Code", "", ""]
        self.ProjectName = ["Project Name", "", ""]
        self.InCharge = ["In charge", "", ""]
        self.PlanDeliveryDate = ["Plan Delivery Date", "", ""]
        self.ProductType = ["Product Type", "", "dropdown"]
        self.Product = ["Product", "", "dropdown"]
        self.Customer = ["Customer", "", "dropdown"]
        self.OrderNumber = ["Order Number", "", ""]
        self.DomesticForeign = ["Domestic Foreign", "", "dropdown"]
        self.OrderQuantity = ["Order Quantity", "", ""]
        self.MonetaryUnit = ["Monetary Unit", "", "dropdown"]
        self.OrderPrice = ["Order Price", "", ""]
        self.VatType = ["Vat Type", "", "dropdown"]
        self.VatRate = ["Vat Rate", "", ""]
        self.ExchangeRate = ["Exchange Rate", "", ""]
        self.ExchangeRateDate = ["Exchange Rate Date", "", ""]
        self.OrderTeam = ["Order Team", "", "dropdown"]
        self.ETC = ["ETC", "", ""]

    def getinfo(self, content):
        for attr, value in self.__dict__.items():
            raw_s = r'{}:.*'.format(value[0])
            pattern = re.compile(raw_s)
            matches = pattern.findall(content)
            for match in matches:
                if attr == 'OrderNumber' or attr == 'OrderPrice' or attr == 'OrderQuantity':
                    value[1] = int((str(match).replace(value[0] + ":", "")).strip())
                elif attr == 'PlanDeliveryDate' or attr == 'ExchangeRateDate':
                    dt = datetime.strptime((str(match).replace(value[0] + ":", "")).strip(),
                                                 '%m/%d/%Y')
                    value[1] = dt.strftime('%Y-%m-%d')
                else:
                    value[1] = (str(match).replace(value[0] + ":", "")).strip()

    def toDict(self):
        di = {}
        for attr, value in self.__dict__.items():
            di[attr] = value[1]

        return di
