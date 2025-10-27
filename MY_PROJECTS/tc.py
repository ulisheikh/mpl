import textwrap
print("Bu yerda linux terminal comandalarini lug'at ko'rinnishida yozamiz \n")

ltc = {
    "chapter-1" : {"[pwd]":"Hozirgi katalog",
                  "[whoami]":"Qandey userda ekaniligini bilish",
                  "[cd]":"Directiryga kirish",
                  "[ls]":"Katalog ichidagi fayllarni chiqarish",
                  "[ls -la]":"Katalog ichidagi fayllarni kengaytma, hajm , vaqtigacha chiqarish",
                  "[man]":"Buyruq yoki comandalarning ma'lumotini ko'rsatib beradi (--help kabi)",
                  "[locate]":"Berilgan so'z bo'yicha tizimdan har qandey ma'lumot izlaydi ,faqat 24 soat ichidagi ma'lumotlarni chiqaradi",
                  "[whereis]":"Binary ya'ni o'rnatilgan dasturlarni va uning elementlarini topadi",
                  "[which]":"PATH orqali faqat binary ichida so'ralgan dastur bor yoki yo'qligini tekshiradi",
                  "[find]":"Eng kuchli qidiruv comandasi bo'lib unga katalog nomi va fayl formati hamda fayl nomi kiritiladi va grep bilan ko'p qo'llanladi",
                  "[grep]":"Boshqa bir buyruqni natijasini olib ikkinnchi buyruq orqali comandalarni bajarish uchun ishlatiladi [quvur]",
                  "[ps]":"Hozirda ishlab turgan barcha process larni ko'rsatib beradi",
                  "[cat]":"Fayl yaratadi (ex: file.txt/.py/.c) va oddiy bir turdagi fayllarni aniq o'qiydi (.txt,.py vahkz)",
                  "[cat >] [fayl_nomi]":"Aagar fayl bor bo'lsa tozalab yangidan yozadi saqlash uchun ctrl+d bosiladi",
                  "[cat >>] [file_nomi]":"Kiritilgan faylga yangi ma'lumot yozish uchun",
                  "[touch]":"Fayl yaratadi (ex: file.txt/.py/.c)",
                  "[nano]":"Fayl yaratadi)",
                  "[cp]":"Fayl nusxalaydi",
                  "[cp -r]":"Diretory nusxalaydi",
                  "[mv]":"Fayl yoki katalog cut va paste qiladi yoki nomini o'zgartiradi",
                  "[rm]":"Faylni o'chiradi",
                  "[rm -r]":"Direktory ni o'chiradi (!!! LEKIN JUDA XAVFLI BILMASDAN BUTUN TIZIMNI O'CHIRIB YUBORISH VAXFI JUDA HAM YUQORI !!!)",
                  },
    "chapter-2" : {

                },
    "chapter-3" : {

                },
    "chapter-4" : {

                },
    "chapter-5" : {

                },
    "chapter-6" : {

                },
    "chapter-7" : {

                },
    "chapter-8" : {

                },
    "chapter-9" : {

                },
    "chapter-10" : {

                },
    "chapter-11" : {

                },
    "chapter-12" : {

                },
    "chapter-13" : {

                },
    "chapter-14" : {

                },
    "chapter-15" : {

                }
}

for chapter, commanda in ltc.items():
    print(f"                    {chapter} komandalar ro'yxati:\n")
    for cmd , info in commanda.items():
        wrapped = textwrap.fill(info.strip(), width=50, subsequent_indent=" " * 8)
        print(f"    {cmd} : {wrapped}\n{'=' * 75}")
        print()
