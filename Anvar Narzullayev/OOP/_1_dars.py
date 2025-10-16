from datetime import datetime
bugun = datetime.today()
yil = bugun.year
class Talaba:
    """Talaba nomli class yaratish"""
    def __init__(self,ism,familiya,tyil):
        self.ism = ism
        self.familiya = familiya
        self.tyil = tyil
        self.bosqich = 1

    def get_name(self):
        """Talabaning ismini chiqaruvchi metod"""
        return self.ism.title()

    def get_lastname(self):
        """Talabaning familiyasini chiqaruvchi metod"""
        return self.familiya.title()
    
    def get_tyil(self):
        """Talabaning tug'ilgan yilini chiqaruvchi metod"""
        return self.tyil
    
    def get_fullname(self):
        """Talabaning umumiy ma'lumotlarini  chiqaruvchi metod"""
        return  f"{self.get_name()} {self.get_lastname()} "\
                f"{self.bosqich}-bosqich talabasi, "\
                f"{self.get_tyil()}-yilda tug'ilgan "
         
    
    def set_bosqich(self,yangi_bosqich):
        """Talabaning bosqichini belgilaydi va bu xususiyat <standartdir>!!!"""
        self.bosqich = yangi_bosqich

    def update_bosqich(self):
        """Bosqichni bittaga oshiradi"""
        self.bosqich += 1


