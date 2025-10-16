from _1_dars import *

class Fan():
    """Fan nomli class yaratish"""
    def __init__(self,nomi):
        """Class uchun xususiyatlar beramiz"""
        self.nomi = nomi
        self.talabalar_soni = 0
        self.talabalar = []

    def add_student(self,talaba):
        """Fan classiga talabalarni qo'shamiz"""
        self.talabalar.append(talaba)
        self.talabalar_soni += 1

    def get_students(self):
        """Fan classining ichidagi har bir obyektni 
        chiqaramiz va ular ro'yxat bo'lib shakllanadi"""
        student = [talaba.get_fullname() for talaba in self.talabalar]            
        return "\n".join(student)

talaba1 = Talaba('Olim','Olimov',2001)
talaba2 = Talaba('Anvar','Salimov',1986)
talaba3 = Talaba('husan','sotimov',2004)
talaba4 = Talaba('otabek','husanov',2002)

matem = Fan("Informatika")
matem.add_student(talaba1)
matem.add_student(talaba2)
matem.add_student(talaba3)
matem.add_student(talaba4)

# Class larning metodlarini ko'ruvchi funksiya
def see_methods(class_nomi):
    """Classning metodini ko'ruvchi funksiya
    uning ichiga class nomini kiriting"""
    return [ x for x in dir(class_nomi) if x.startswith("__") is False]

print(matem.get_students())
print(see_methods(Talaba))

