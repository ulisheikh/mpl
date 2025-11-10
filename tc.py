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
                  "[echo]":"Biror bir fayl yaratmoqchi yoki matn qo'shishda ishlatiladi ,eng qulayi - bir qator yoziladi",
                  "[cat]":"Fayl yaratadi (ex: file.txt/.py/.c) va oddiy bir turdagi fayllarni aniq o'qiydi (.txt,.py vahkz)",
                  "[cat >] [file_name]":"Aagar fayl bor bo'lsa tozalab yangidan yozadi saqlash uchun ctrl+d bosiladi",
                  "[cat >>] [file_name]":"Kiritilgan faylga yangi ma'lumot yozish uchun",
                  "[touch]":"Fayl yaratadi (ex: file.txt/.py/.c)",
                  "[nano]":"Fayl yaratadi)",
                  "[cp]":"Fayl nusxalaydi",
                  "[cp -r]":"Diretory nusxalaydi",
                  "[mv]":"Fayl yoki katalog cut va paste qiladi yoki nomini o'zgartiradi",
                  "[rm]":"Faylni o'chiradi",
                  "[rm -r]":"Direktory ni o'chiradi (!!! LEKIN JUDA XAVFLI BILMASDAN BUTUN TIZIMNI O'CHIRIB YUBORISH VAXFI JUDA HAM YUQORI !!!)",
                  "[echo 'text' | sudo tee file_location]":"root faylga yozganda (>) redirect ning kuchi yetmaydi shuning uchun sudo tee ishlatiladi , tee ham ma'lumot yozadi",
                  "[sudo bash -c] 'echo [text]> file_location":"bash yordamida root faylga ma'lumot yozish uchun ishlatiladi ",
                  "[tee -a text file_location]":"-a append qiladi ya'ni fayl ichidagi mavjud ma'lumotlar o'chib ketnaydi",
                  "[sudo cp etc/resolv.conf.bak]":"bir faylni o'zgartirishdan oldin xavfsizlik nuqtai nazaridan copy qilib olish \
                   (.bak o'rniga hohlagan nom bersa bo'ladi)",

                  
                  },
    "chapter-2" : {"[head]":"Text faylning boshini chiqaradi (ex: head -20 fayl_nomi)",
                   "[tail]":"Text faylning oxirini chiqaradi (ex: tail -20 fayl_nomi)",
                   "[nl]":"Qatorlarga raqam beradi bu holatda bo'sh qatorlar raqamlanmaydi",
                   "[nl -ba]":"Qatorlarga raqam beradi hatto bo'sh qatorgga ham ",
                   "[sed]":"Textning ichidagi biror bir so'zni o'zgartirish yoki tahrirlah uchun foydalaniladi\
                    [g] opsiyasi qo'yilasa faqat birinchi so'z tahrir agar o'rniga son qo'yilsa shu inex tahrir bo'ladi",
                   "[sed -i]":"sed (-i) insert opsiyasi ma'lum bir qatordan oldidan yozadi ex: sed -i /127/.0/.0/.0\i new_text file_location\
                    agar quyidagidek yozilsa ex: sed -i '3i new_text /file_location/ 3- qatorga qo'shib beradi ",
                   "sed -a":"sed append opsiyasi ma'lum bir qator pastidan yozadi ex: sed -i /127/.0/.0/.0\a new_text file_location ",
                   "[more]":"Text faylni o'qiydi cat sifatiga o'xshash chiqish uchun [q] bosiladi",
                   "[less]":"[more] ga o'xshash lekin funksiyasi ko'proq [/] dan so'ng so'z kiritsa shu so'zni topadi [n] bosilsa keyingisiga o'tadi"
                },
    "chapter-3" : {"[ifconfig]":"Tarmoqlarni ko'rsatadi: eth0/wlan0ip va adress,mac adress,",
                   "[ip adrr show]":"ifconfig bilan funksiyasi bor xil faqat zamonaviy usuli va ma'lumotlar ko'proq chiqad",
                   "[iwconfig]":"wireless ya'ni simsiz tarmoq ma'lumotlarini va holatini ko'rsatadi",
                   "[ifconfig (eth0) 192.168...]":"ip manzil o'zgartirish",
                   "[ifconfig (eth0) 192.168... netmask 255.255.255.0 broadcast 192.168.1.255]":"netmask va broadcast manzilni o'zgartirish",
                   "[ifconfig ether down/ifconfig eth0 hw ether 00.11.22.33.44.aa/ifconfig eth0 up]":"mac manzilni o'zgartirish",
                   "DHCP":"Har qanday qurilmaga ip va tarmoq sozlamalarini AVTOMATIK tarzda beradi",
                   "[dhclient eth0]":"dhcp orqali ip manzilni olish yoki yangilash, avtomatik beradi",
                   "[dhclient -r eth0]":"dhcp orqali olingan ip manzilni bo'shatadi (kill qiladi)",
                   "[dhclient -v eth0]":"jarayonni ko'rsatadi",
                   "[dig example.com ns]":"berilgan dns ning name server va ip manzilini ko'rsatib beradi",
                   "[dig example.com mx]":"email uchun qaysi serverlar javob berishini ko'rsatadi",
                   "[dig example.com]":"berilgan saytning ip manzilini qaytaradi",
                   "[dnsspoof and eyyercap]":"Tarmoq va hostlarni hack qlish uchun yaxshi toollar"
                },
    "chapter-4" : {"[apt-cache search keyword or package_name]":"Bu buyruq orqali berilgan dastur tizimga o'rnatilganmi yo'qmi\
                    bilish mumkin.Kesh fayllarni ham ko'rsatadi",
                    "[apt-get install packagename]":"Bu buyruq yangi dasturni o'rnatish uchun foydalaniladi",
                    "[apt-get remove packkagename]":"Bu dasturlarni o'chirishda ishlatiladigan buyruq lekin konfiguratsiya faylari qoladi",
                    "[apt-get purge packagename]":"Dasturga qo'shib konfiguratsiya fayllarini ham qo'shib o'chiradi",
                    "[apt-get autoremove packagename]":"Dastur ishlashi uchun birgalikda o'rnatilgan fayl va kutubxonalargacha o'chiradigan buyruq",
                    "[apt-update]":"Tizimni bitta yangilaydi va qanday yangilanishlar borligini ko'rsatib beradi lekin o'rnatmaydi",
                    "[apt-get upgrade]":"Tizimdagi barcha yangilanishlarni yangi versiyasi bilan o'rnatadi",
                    "[sources.list (root_file)]":"Dasturiy ta'minot uchun repositoriya",
                    "[synaptic]":"Packagelarni boshqarish uchun interface"                    

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
    wrapped_chapter = chapter.strip() 
    indent = ' ' * 20
    print(f"{indent}{'='*36}")
    print(f"{indent}>>>{wrapped_chapter} komandalar ro'yxati:<<<")
    print(f"{indent}{'='*36}\n")
    
    for cmd , info in commanda.items():
        wrapped = textwrap.fill(info.strip(), width=50, subsequent_indent=" " * 12)
        print(f"    {cmd} : {wrapped}\n{'_' * 75}\n")
