
from abc import ABC, abstractmethod

class IPrice(ABC):
    """Interface for price components"""
    @abstractmethod
    def get_price(self):
        pass


class Price(IPrice):
    """Base class representing the original price"""
    def __init__(self, base_price: float):
        self._base_price = base_price

    def get_price(self):
        return self._base_price


class PriceDecorator(IPrice):
    """Abstract decorator that implements IPrice"""
    def __init__(self, price_component: IPrice):
        self._price_component = price_component

    @abstractmethod
    def get_price(self):
        pass


class DiscountDecorator(PriceDecorator):
    """Applies discount to the base price"""
    def __init__(self, price_component: IPrice, discount_percent: float):
        super().__init__(price_component)
        self.discount_percent = discount_percent

    def get_price(self):
        base = self._price_component.get_price()
        return base - (base * (self.discount_percent / 100))


class TaxDecorator(PriceDecorator):
    """Adds tax to the price after discount"""
    def __init__(self, price_component: IPrice, tax_percent: float):
        super().__init__(price_component)
        self.tax_percent = tax_percent

    def get_price(self):
        base = self._price_component.get_price()
        return base + (base * (self.tax_percent / 100))
