from .exceptions import ObjectAlreadyExist, ObjectDoesNotExist





class Manager:
    def __init__(self, model):
        self._model = model
        self._objects = []
        
    def create(self, **kwargs):
        new_object = self._model(**kwargs)
        self._objects.append(new_object)
        return new_object
    
    def remove(self, **kwargs):
        for obj in self._objects:
            for key, value in kwargs.items():
                if getattr(obj, key) == value:
                    self._objects.remove(obj)
                    return
        raise ObjectDoesNotExist(f'Object with {kwargs} does not exist')

    def all(self):
        return self._objects

    def get(self, **kwargs):
        for obj in self._objects:
            for key, value in kwargs.items():
                if getattr(obj, key) == value:
                    return obj
        raise ObjectDoesNotExist(f'Object with {kwargs} does not exist')

    def filter(self, **kwargs):
        result = []
        for obj in self._objects:
            for key, value in kwargs.items():
                if getattr(obj, key) == value:
                    result.append(obj)
        return result


class Model:
    
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'objects'):
            cls._objects = Manager(cls)
        return super().__new__(cls)
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.__dict__})'
    
    @property
    def objects(self):
        return self._objects
    
    def remove(self) -> None:
        self.objects.remove(**self.__dict__)
    
    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)