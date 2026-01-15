import json
import os
from typing import List, Dict, Optional

class DictionaryHandler:
    """DictinoryBot papkasidagi dictionary.json ni o'qish (AVTOMATIK YANGILANISH)"""
    
    def __init__(self, json_path: str):
        self.json_path = json_path
        self._cache = None
        self._last_mtime = 0  # Faylning oxirgi o'qilgan vaqti
    
    def _load_json(self) -> Dict:
        """Fayl o'zgargan bo'lsagina uni qayta yuklash"""
        try:
            if not os.path.exists(self.json_path):
                return {}

            # Faylning diskdagi oxirgi o'zgarish vaqtini olish
            current_mtime = os.path.getmtime(self.json_path)
            
            # Agar fayl vaqti bizdagi vaqtdan yangi bo'lsa yoki kesh hali yo'q bo'lsa
            if self._cache is None or current_mtime > self._last_mtime:
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
                self._last_mtime = current_mtime
                # print(f"🔄 Lug'at yangilandi!") # Debug uchun kerak bo'lsa yoqing
                
        except Exception as e:
            print(f"Error loading dictionary: {e}")
            return self._cache if self._cache else {}
        
        return self._cache
    
    def get_all_topics(self) -> List[str]:
        """Barcha topik nomlarini olish (Topik-35, Topik-36...)"""
        data = self._load_json()
        return list(data.keys())
    
    def get_topic_sections(self, topic: str) -> List[str]:
        """Topikdagi bo'limlarni olish (reading, writing, listening)"""
        data = self._load_json()
        topic_data = data.get(topic, {})
        return list(topic_data.keys())
    
    def get_section_chapters(self, topic: str, section: str) -> List[str]:
        """Bo'limdagi boblarnni olish (9-savol so'zlari, 13-savol...)"""
        data = self._load_json()
        section_data = data.get(topic, {}).get(section, {})
        return list(section_data.keys())
    
    def get_chapter_words(self, topic: str, section: str, chapter: str) -> Dict[str, str]:
        """Bob ichidagi so'zlarni olish"""
        data = self._load_json()
        return data.get(topic, {}).get(section, {}).get(chapter, {})
    
    def get_all_words(self) -> List[Dict[str, str]]:
        """Barcha so'zlarni ro'yxat ko'rinishida olish"""
        data = self._load_json()
        all_words = []
        word_id = 1
        
        for topic, topic_data in data.items():
            for section, section_data in topic_data.items():
                for chapter, words in section_data.items():
                    for korean, uzbek in words.items():
                        all_words.append({
                            'id': word_id,
                            'korean': korean,
                            'uzbek': uzbek,
                            'topic': topic,
                            'section': section,
                            'chapter': chapter
                        })
                        word_id += 1
        return all_words
    
    def get_total_words(self) -> int:
        """Jami so'zlar soni"""
        return len(self.get_all_words())
    
    def get_word_by_id(self, word_id: int) -> Optional[Dict]:
        """ID bo'yicha so'z topish"""
        words = self.get_all_words()
        for word in words:
            if word['id'] == word_id:
                return word
        return None
    
    def search_by_korean(self, korean: str) -> Optional[Dict]:
        """Koreys so'z bo'yicha qidirish"""
        words = self.get_all_words()
        for word in words:
            if word['korean'].strip() == korean.strip():
                return word
        return None
    
    def reload(self):
        """Keshni tozalash va qayta yuklash"""
        self._cache = None
        self._load_json()

# --- Qo'shimcha funksiya ---
async def get_formatted_word_stats():
    from database.db import get_words_sorted_by_usage
    
    words = await get_words_sorted_by_usage()
    structured_data = {}

    for w in words:
        category = w['category'] # 35-topik
        sub_cat = w['sub_category'] # reading
        
        if category not in structured_data:
            structured_data[category] = {}
        if sub_cat not in structured_data[category]:
            structured_data[category][sub_cat] = []
            
        structured_data[category][sub_cat].append(w)
    
    return structured_data