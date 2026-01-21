from abc import ABC, abstractmethod

class IProductCreator(ABC):
    @abstractmethod
    def create_product(self, data):
        pass

class IProductReader(ABC):
    @abstractmethod
    def get_all_products(self):
        pass

    @abstractmethod
    def get_products(self, product_id):
        pass

class IProductUpdater(ABC):
    @abstractmethod
    def update_product(self, product_id, data):
        pass

class IProductDeleter(ABC):
    @abstractmethod
    def delete_product(self, product_id):
        pass

                                    #Category_Interface


class ICategoryCreator(ABC):
    @abstractmethod
    def create_category(self, data):
        pass

class ICategoryReader(ABC):
    @abstractmethod
    def get_all_categories(self):
        pass

    @abstractmethod
    def get_category(self,category_id):
        pass

class ICategoryUpdater(ABC):
    @abstractmethod
    def update_category(self, category_id, data):
        pass

class ICategoryDeleter(ABC):
    @abstractmethod
    def delete_category(self, category_id):
        pass