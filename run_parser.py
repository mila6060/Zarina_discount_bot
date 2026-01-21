def main():
    print("=" * 50)
    print("🛒 ПАРСИМ ТОВАРЫ С ZARINA.RU")
    print("=" * 50)
    
    # Создаем парсер
    parser = ZarinaParser()
    all_products = []
    
    # Парсим каждую категорию
    for category_name, url in CATEGORIES.items():
        print(f"\n🔍 Категория: {category_name}")
        print(f"   Ссылка: {url}")
        
        # Получаем товары из категории
        products = parser.parse_category(url, category_name)
        
        # Считаем сколько товаров со ссылками
        with_links = sum(1 for p in products if 'url' in p)
        print(f"   Ссылки найдены: {with_links}/{len(products)}")
        
        all_products.extend(products)
        
        # Делаем паузу между запросами
        time.sleep(2)
    
    # Сохраняем все товары
    parser.save_products(all_products)
    
    # Статистика
    total_with_links = sum(1 for p in all_products if 'url' in p)
    
    print("\n" + "=" * 50)
    print(f"🎉 ВСЕГО ТОВАРОВ: {len(all_products)}")
    print(f"🔗 Со ссылками: {total_with_links}")
    print("=" * 50)
    
    # Показываем примеры товаров со ссылками
    print("\n📊 Примеры найденных товаров (со ссылками):")
    
    examples = [p for p in all_products if 'url' in p][:3]
    for i, product in enumerate(examples, 1):
        print(f"\n{i}. {product['name']}")
        print(f"   Цена: {product.get('price', '?')} руб")
        if product.get('discount', 0) > 0:
            print(f"   Скидка: {product['discount']}%")
        print(f"   Ссылка: {product['url'][:50]}...")
    
    print("\n✅ Теперь запустите main.py для работы бота!")
    print("📱 Бот будет показывать ссылки вида: 🔗 [Посмотреть на сайте](ссылка)")