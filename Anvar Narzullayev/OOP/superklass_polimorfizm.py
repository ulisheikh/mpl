from datetime import datetime
bugun = datetime.today()
year = bugun.year
class Shaxs():
    def __init__(self,ism,familiya,passport,t_yil):
        self.ism = ism
        self.familiya = familiya
        self.passport = passport
        self.t_yil = t_yil

    def get_info(self):
        info = f"\nIsm: {self.ism.title()} {self.familiya.title()}\
                \nPassport: {self.passport} \
                \nTug'ilgan yili: {self.t_yil}"
        return info
    
    def get_age(self):
        yosh = year - self.t_yil
        return yosh

inson1 = Shaxs("Aliyev","Vali","FA12345678",2001)
# print(inson1.get_info())

class Talaba(Shaxs):
    def __init__(self,ism,familiya,passport,t_yil,id_raqam,manzil):
        super().__init__(ism,familiya,passport,t_yil)
        self.Id = id_raqam
        self.manzil = manzil
        self.bosqich = 1

    def get_info(self):
        info = f"\nIsm: {self.ism.title()} {self.familiya.title()}\
                \nPassport: {self.passport} \
                \nTug'ilgan yili: {self.t_yil}\
                \nID: {self.Id}\
                \nBosqich: {self.bosqich}"
        return info


class Manzil():
    """Manzil obyektini yaratuvchi klass"""
    def __init__ (self,viloyat,tuman,kocha,uy):
        self.viloyat = viloyat
        self.tuman = tuman
        self.kocha = kocha
        self.uy = uy
    
    def get_manzil(self):
        """Manzil qaytaruvchi metod"""
        manzil = (f"\nManzil: {self.viloyat.capitalize()} viloyati "
              f"{self.tuman.capitalize()} tumani "
              f"{self.kocha.capitalize()} ko'chasi "
              f"{self.uy}-uy")
        return manzil


manzil = Manzil('Namangan','chust','charog\'on',24)
talaba = Talaba("Aliyev","Vali","FA12345678",2001,"NAD80744tER",manzil)
print(talaba.get_age())
