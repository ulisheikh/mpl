from uuid import uuid4

class Avto:
    __num_avto = 0
    def __init__(self,model,rang,narh,km=0):
        self.model = model
        self.rang = rang
        self.narh = narh
        self.__km = km
        self.__id = uuid4()
        Avto.__num_avto+=1

    def get_km(self):
        return self.__km
    
    def get_id(self):
        return self.__id
    
    def add_km(self,km):
        if km >= 0:
            self.__km += km
        else:
            print("Avtomobilning yurgan masofasini kamaytirib bo'lmaydi!")
    @classmethod
    def get_num_avto(cls):
        return cls.__num_avto
        
        
avto1 = Avto('malibu','oq',20000,1000)
avto2 = Avto('gentra','qora',15000,80000)
avto3 = Avto('cobalt','silver',12000,2000)
avto4 = Avto('damas','oq',10000,200000)


# print(avto1.get_num_avto())


