import requests
from bs4 import BeautifulSoup
import json
import time
import re

class ZarinaParser:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.base_url = "https://zarina.ru"
    
    def get_html(self, url):
        """Получаем HTML страницу"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            return response.text
        except:
            print(f"Ошибка загрузки {url}")
            return ""
    
    def find_product_info(self, card, category_name):
        """Ищем информацию о товаре в карточке"""
        try:
            product = {}
            
            # 1. Ищем название
            name = "Товар"
            
            # Ищем в заголовках
            for tag in ['h3', 'h4', 'h5', 'h6']:
                title = card.find(tag)
                if title:
                    name = title.text.strip()
                    break
            
            # Если не нашли, ищем в ссылках
            if name == "Товар":
                link = card.find('a')
                if link and len(link.text) > 5:
                    name = link.text.strip()
            
            product['name'] = name[:80]  # Обрезаем слишком длинные названия
            
            # 2. Ищем ССЫЛКУ на товар
            product_link = None
            
            # Ищем все ссылки
            all_links = card.find_all('a', href=True)
            for link in all_links:
                href = link['href']
                # Проверяем, похоже ли это на ссылку на товар
                if '/product/' in href or '/item/' in href or 'platya' in href or 'bluzki' in href:
                    product_link = href
                    break
            
            # Если нашли ссылку, формируем полный URL
            if product_link:
                if product_link.startswith('http'):
                    product['url'] = product_link
                else:
                    product['url'] = self.base_url + product_link
            
            # 3. Ищем цены
            text = card.get_text()
            numbers = re.findall(r'\d[\d\s]+', text)
            
            prices = []
            for num in numbers:
                try:
                    clean_num = int(num.replace(' ', ''))
                    # Реальные цены одежды
                    if 100 < clean_num < 50000:
                        prices.append(clean_num)
                except:
                    pass
            
            if prices:
                prices.sort()
                product['price'] = prices[0]
                
                # Если есть несколько цен, то самая большая - старая цена
                if len(prices) > 1 and prices[-1] > product['price']:
                    product['old_price'] = prices[-1]
            
            # 4. Добавляем категорию
            product['category'] = category_name
            
            # 5. Считаем скидку
            if product.get('old_price') and product['old_price'] > product.get('price', 0):
                discount = ((product['old_price'] - product['price']) / product['old_price']) * 100
                product['discount'] = int(discount)
            else:
                product['discount'] = 0
            
            return product
            
        except Exception as e:
            print(f"Ошибка парсинга карточки: {e}")
            return None
    
    def parse_category(self, url, category_name):
        """Парсим одну категорию товаров"""
        print(f"📦 Парсим {category_name}...")
        
        html = self.get_html(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Ищем все карточки товаров разными способами
        
        # Способ 1: Ищем по классам
        card_selectors = [
            'div.product-card',
            'div.catalog-item',
            'article.product-item',
            'div.item',
            'div[data-product]'
        ]
        
        cards = []
        for selector in card_selectors:
            found = soup.select(selector)
            if found:
                cards.extend(found)
                break
        
        # Способ 2: Если не нашли по классам, ищем все div с товарами
        if not cards:
            all_divs = soup.find_all('div')
            for div in all_divs:
                # Пропускаем слишком маленькие div
                if len(str(div)) > 200:
                    cards.append(div)
        
        print(f"Найдено карточек: {len(cards)}")
        
        # Парсим каждую карточку
        for i, card in enumerate(cards):
            # Ограничиваем количество товаров
            if len(products) >= 15:
                break
                
            product_info = self.find_product_info(card, category_name)
            
            if product_info and product_info.get('price'):
                # Добавляем ID товара
                product_info['id'] = f"{category_name}_{i}"
                products.append(product_info)
                
                # Выводим информацию для отладки
                name_short = product_info['name'][:30] + "..." if len(product_info['name']) > 30 else product_info['name']
                print(f"  {len(products)}. {name_short} - {product_info['price']} руб")
        
        print(f"✅ Найдено товаров: {len(products)}")
        return products
    
    def save_products(self, products, filename='products.json'):
        """Сохраняем товары в файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"💾 Сохранено {len(products)} товаров")
    
    def load_products(self, filename='products.json'):
        """Загружаем товары из файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                products = json.load(f)
            print(f"📖 Загружено {len(products)} товаров")
            return products
        except:
            print("Файл с товарами не найден")
            return []