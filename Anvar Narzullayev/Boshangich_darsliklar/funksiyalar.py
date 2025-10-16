""" funksiyalarni def kalit so'zi bilan yaratamiz """
def salom_ber():
    """ Salom beuvchi dastur """
    print("Assalomu aleykum")

# funksiyalardan lug'at olish

# def avto_info(kompanya,model,rang,yil,narx = None):
#     avto = {
#         "kompanya":kompanya,
#         "model" : model,
#         "rang" : rang,
#         "yil" : yil,
#         "narxi" : narx
#     }
#     return avto 


# avto1 = avto_info("hyundai","sonata","qizil",2020,20000)
# avto2 = avto_info("kia","k5","oq",2016)
# avto3 = avto_info("chevrolet","malibu","sedan",2024,25000)
# avtolar = [avto1,avto2,avto3]
# for avto in avtolar:
#     if avto["narxi"]:
#         price = avto["narxi"]
#     else:
#         price = "Noma'lum"
#     print(
#         f"\nKompanya: {avto['kompanya'].title()}"
#         f"\nModel: {avto['model'].title()}"
#         f"\nRangi: {avto['rang'].title()}"
#         f"\nYili: {avto['yil']}-yil"
#         f"\nNarxi: {price} &"
#            )

# range() uzbekchada
# def oraliq(min,max,step = None):
#     sonlar = []
#     while min < max:
#         if step:
#             sonlar.append(min)
#             min += step
#         else:
#             sonlar.append(min)
#             min += 1
#     return sonlar
   
# son = oraliq(0,30,3)
# print(son)

# son2 = list(range(0,30,3))
# print(son2)
