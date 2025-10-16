# LIST
# 2024/09/14

# talaba1 degan bo'sh lug'at yaratib uni to'ldiramiz
# talaba1 = {}
# talaba1['ism'] = "ali"
# talaba1['familiya'] = "valivey"
# talaba1['yosh'] = 23

# del yordamida elementni o'chiramiz
# del talaba1['ism']
# print(talaba1)

# get() metodi
# print(talaba1.get('ism',"Bunday kalit mavjud emas"))

# items() metodi 
# for kalit,qiymat in talaba1.items():
#     print(f"Kalit: {kalit}")
#     print(f"Qiymat: {qiymat}")

# bozorlik = ["non","un","shakar","baliq","nok","olma"]
# mahsulotlar = {
#     "non": 3500,
#     "anor": 12000,
#     "baliq": 15000,
#     "shakar": 5000,
#     'makaron': 3200,
#     "yog'":15000
# }

#values() metodi yordamida qiymatlarni chiqaramiz
# for q in mahsulotlar.values():
#     print(q)

# lug'atning elementlariga murojaat qilish
# print(mahsulotlar['non'])

# keys() metodi
# for mahsulot in mahsulotlar:
#     if mahsulot in bozorlik:
#         print(f"{mahsulot.title()} do'konimizda bor narxi {mahsulotlar[mahsulot]} so'm")
#     elif mahsulot not in bozorlik:
#         print(f"{mahsulot.title()} do'konimizda yo'q ")
    
# sorted() yordamida lug'at ichidagi kalit va qiymatlarni sartirovka qila olamiz undan foydalanganda tartib o'zgarmaydi
# for mahsulot in sorted(mahsulotlar):
#     print(mahsulot)

# telefonlar = {

#     "ali":"nokia",
#     "ulee":"iphone",
#     "vali":"redmi",
#     "husan":"lg",
#     "hasan":"samsung",
#     "olim": "samsung",
#     "orif": "iphone"
# }

# set() yordamida biz takrorlangan ma'lumotlarni faqat bir marotaba chiqaramiz
# for t in set(telefonlar.values()):
#     print(t)