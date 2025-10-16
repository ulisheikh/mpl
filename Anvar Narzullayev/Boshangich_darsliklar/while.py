""" while sikldan foydalanamiz """
# son = 1
# while son <= 10:
#     print(son, end=' ')
#     son += 1
# print(" Dastur tugadi!")

# savol = "Hohlagan soningizni kiriting "
# savol += "dasturni to'xtatish uchun 'exit' deb yozing:\n>>>"
# qiymat = ''
# while qiymat != "exit":
#     qiymat = input(savol)
#     if qiymat != "exit":
#         print(float(qiymat)**2)
# print("Dastur tugadi! ")

""" continue bir qadam o'tkazib yuboradi va continue dan keyingi kodlar bajarilmaydi """
son = 0
while son < 10:
    son += 1
    if son%2 != 0:
        print(son)
    else:
        continue
print("Dastur tugadi")

