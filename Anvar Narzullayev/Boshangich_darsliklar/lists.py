# 1 - dars.LIST 
# sana 2024/09/14

#bo'sh list yaratib uni append() metodi yordamida to'ldirib boramiz 

print("\nBo'sh list yaratib uni append() metodi yordamida to'ldirib boramiz") 
fruits = [] 
print(f"\n{fruits}")

# append faqat bitta element yoki list qo'sha oladi va ro'yxat OXIRIGA qo'shadi

print("append faqat bitta element yoki list qo'sha oladi va ro'yxat OXIRIGA qo'shadi")
fruits.append("olma") 
print(f"\n{fruits}")

# extend metodi orqali esa ko'p element qo'sha oladi FAQAT ularni LIST qilib kiritamiz
print("extend metodi orqali esa ko'p element qo'sha oladi FAQAT ularni LIST qilib kiritamiz")
fruits.extend(["o'rik","shaftoli","anjir","qulupnay"]) 
print(fruits)
                                                           
# shuningdek append() metodi orqali list ichiga list ham qo'sha oladi
mevalar = ["olicha","gilos","ananas","anor","xurmo"]
fruits.append(mevalar) 

# list ichidagi listlarrga yoki elementlarga murojaat qilamiz
print(f"\nIkkinchi listning birinchi elementi bu >>> {fruits[5][0].upper()}") 
print(fruits)

# bu usul bilan elementlarni o'zgartiramiz
fruits[5][0] = "uzum" 

# bu usul bilan elementlarni sug'urib olamiz
fruit = fruits.pop(0)
print(

    f"\nBiz pop() metodi orqali <{fruit}>ni sug'urib oldik endi bu maxsulot"
     "\nro'yxatda ko'rinmaydi chunki FRUIT nomli"
     "\no'zgaruvchiga yuklab qo'yildi"
    
    )
print(fruits)

# biz insert() metodi orqali listning HOHLAGAN oralig'iga  element qo'sha olamiz 
fruits.insert(0,"tarvuz")
print(f"\nRo'yxatimizga insert orqali  <tarvuz> qo'shildi\n{fruits}")

# biz del() operatori orqali index bo'yicha elementlarni o'chiramiz
del fruits[0]
print(f"\nBiz del operatori yordamida <tarvuz>ni yana o'chirdik\n{fruits}")

# biz remove() metodi orqali listdan qiymati orqali element o'chira olamiz
fruits.remove("anjir")
print(f"\nBiz remove() metodi orqali <anjir>ni ham o'chirdik\n{fruits}")

# endi list  ichidagi listdan del yordamida elementni o'chiramiz
del fruits[3][0]
print(f"\nBiz del operatori yordamida <uzum>ni o'chirdik\n{fruits}")

# endi remove() metodi orqali element o'chiramiz 
fruits[3].remove("ananas")
print(f"\nBiz remove() metodi yordamida <ananas>ni o'chirdik\n{fruits}")

# print(f"\nNATIJA: {meva}lar ro'yxatda qoldi")
print(len(fruits))
["o'rik", 'shaftoli', 'qulupnay', ['gilos', 'anor', 'xurmo']]
print("Natija: ",end = '')
all_fruits = []
for m in fruits:
    if isinstance(m, list):
        all_fruits.extend(m)
    else:       
        all_fruits.append(m)
print(",".join(all_fruits))    

# split() METODI BIZGA MATNNI AJRATIB ULARNI LIST QILIB QAYTARIB BERADI       
text = "Hello  ?how? are? you?"
words = text.split()
print(len(words),words)


