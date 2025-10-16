car_0 = {
    "model":"huyndai",
    "yil":2020,
    "rangi":"qizil",
    "karobka":"avtomat",
    "narx":20000,
    "yurgan_masofasi": 0
}

car_1 = {
    "model":"kia",
    "yil":2023,
    "rangi":"qora",
    "karobka":"avtomat",
    "narx":30000,
    "yurgan_masofasi": 0
}

car_2 = {
    "model":"ferrari",
    "yil":2024,
    "rangi":"qizil",
    "karobka":"avtomat",
    "narx":50000,
    "yurgan_masofasi": 0
}

""" hamma lug'atlarni bitta ro'yxatga joylaymiz """
cars = [car_0,car_1,car_2]
for car in cars:
    print(
        f"{car['model'].title()}, {car['yil']}-yil ,rangi {car['rangi']},"
        f" karobkasi {car['karobka']} karobka, narxi {car['narx']} $,"
        f" yurgani {car['yurgan_masofasi']} km "
    )
print("---------------------------------------------------------------------")

""" ro'yxatni ichidagi lug'atlarning qiymatiga murojaat qilamiz """
car = cars[1]['model']
print(f'\n{car.title()}')
print("---------------------------------------------------------------------")


""" royxat yartib unig ichiga append orqali lug'atlarni qo'shamiz  """

malibus = []
for malibu in range(10):
    new_car = {
        "model": "malibu",
        "rangi": None,
        "yil": 2020,
        "narx": None,
        "km":0,
        "karobka":"avtomat"
    }
    malibus.append(new_car)

for malibu in malibus[:3]:
    malibu['rangi'] = "qizil"

for malibu in malibus[3:6]:
    malibu['rangi'] = "qora"

for malibu in malibus[6:]:
    malibu['rangi'] = "oq"
    malibu['karobka'] = "mexanika"

for malibu in malibus:
    if malibu["karobka"] == "avto":
        malibu['narx'] = 40000
    else:
        malibu['narx'] = 35000

car_num = 1
for malibu in malibus:
    print(
        f"\n{car_num}-mashina"

        f"\nModeli: {malibu['model'].title()} "
        f"\nRangi: {malibu['rangi'].title()} " 
        f"\nYili: {malibu['yil']}-yil"
        f"\nNarxi: {malibu['narx']} $ "
        f"\nYurgan masofasi: {malibu['km']} km "
        f"\nKarobkasi: {malibu['karobka'].title()}"
        )
    car_num += 1
print("---------------------------------------------------------------------")



""" endi lug'atlar ichida ro'yxatlarni saqlaymiz """
dasturchilar = {
    "ali":["python","c++"],
    "vali":["java","php","python"],
    "maryam":["c","js","ruby"],
    "hasan":["html","sql","css"],
    "husan":["java","c#"]
}
for ism,tillar in dasturchilar.items():
    print(f"\n{ism.title()} quyidagi tillarni biladi: ",end='\n')
    for til in tillar:
        print(f"{til.upper()}\n",end='')

print("---------------------------------------------------------------------")



""" lug'atlar ichiga lug'atlar joylaymiz """
hamkasblar = {
    "ali" : {
        "familiya": "zokirov",
        "t_yil": 2001,
        "malumoti": "oliy",
        "language" : ["python","c++"],
             
             },

    "vali" : {
        "familiya": "qodirov",
        "t_yil": 2001,
        "malumoti": "oliy",
        "language" : ["java","php","python"],
             
             },
    "maryam" : {
        "familiya": "Abdullayeva",
        "t_yil": 2001,
        "malumoti": "oliy",
        "language" : ["c","js","ruby"],
             
             },

             
}

for ism,info in hamkasblar.items():
    print(
        
        f"\n{info['familiya'].title()} {ism.title()} {info['t_yil']}-yilda tug'ilgan "
        f"\nMa'lumoti: {info['malumoti'].title()}"
        )
    print("Quyidagi dasturlash tillarini biladi: ")
    for til in info['language']:
        print(f"{til.upper()}")
print("---------------------------------------------------------------------")



