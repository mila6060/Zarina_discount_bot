import telebot
from telebot import types
import json
import os
from dotenv import load_dotenv
import re

# Загружаем токен из .env файла
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Проверяем токен
if not TOKEN:
    print("❌ ОШИБКА: Не найден токен бота!")
    print("Создайте файл .env с содержимым:")
    print("BOT_TOKEN=ваш_токен_бота")
    exit()

# Создаем бота
bot = telebot.TeleBot(TOKEN)
print("✅ Бот создан успешно!")

# Пробуем загрузить товары
try:
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    print(f"📦 Загружено {len(products)} товаров")
except:
    print("⚠️ Файл products.json не найден")
    print("Сначала запустите run_parser.py")
    products = []
    

# Функция для создания клавиатуры
def create_keyboard():
    """Создаем клавиатуру с кнопками"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Первая строка
    btn1 = types.KeyboardButton("👗 Платья")
    btn2 = types.KeyboardButton("👚 Блузки")
    
    # Вторая строка
    btn3 = types.KeyboardButton("✨ Юбки")
    btn4 = types.KeyboardButton("👖 Брюки")
    
    # Третья строка
    btn5 = types.KeyboardButton("🔥 Скидки")
    btn6 = types.KeyboardButton("💰 Дешевые")
    btn7 = types.KeyboardButton("💎 Дорогие")
    
    # Четвертая строка
    btn8 = types.KeyboardButton("📊 Статистика")
    btn9 = types.KeyboardButton("ℹ️ Помощь")
    
    keyboard.add(btn1, btn2)
    keyboard.add(btn3, btn4)
    keyboard.add(btn5, btn6, btn7)
    keyboard.add(btn8, btn9)
    
    return keyboard
# Функции для сортировки
def get_discount_value(product):
    """Возвращает значение скидки товара для сортировки"""
    return product.get('discount', 0)

def get_price_value(product):
    """Возвращает значение цены товара для сортировки"""
    return product.get('price', 0)

def get_price_value_with_default(product):
    """Возвращает значение цены товара с дефолтным большим значением"""
    return product.get('price', 99999)

# Функция-фильтр для декоратора
def handle_all_messages(message):
    """Функция, которая всегда возвращает True для обработки всех сообщений"""
    return True
# Команда /start
@bot.message_handler(commands=['start'])
def start_message(message):
    """Приветственное сообщение"""
    welcome = """
👋 *Привет! Я бот для магазина Zarina!*

Я помогу найти лучшие товары и скидки!

*Что я умею:*
• Показывать товары по категориям
• Искать товары со скидками
• Фильтровать по цене
• Показывать статистику

*Используйте кнопки ниже или команды:*
/start - начать
/help - помощь
/sales - товары со скидкой
/stats - статистика

*Можно писать в чат:*
"платья" - все платья
"до 2000" - товары до 2000 руб
"дешевые" - недорогие товары
"""
    
    bot.send_message(message.chat.id, welcome, 
                    reply_markup=create_keyboard(),
                    parse_mode='Markdown')

# Команда /help
@bot.message_handler(commands=['help'])
def help_message(message):
    """Справка по использованию бота"""
    help_text = """
📚 *СПРАВКА ПО ИСПОЛЬЗОВАНИЮ БОТА*

*КНОПКИ:*
👗 Платья - покажет все платья
👚 Блузки - блузки и рубашки
✨ Юбки - все юбки
👖 Брюки - брюки и джинсы
🔥 Скидки - товары со скидкой
💰 Дешевые - самые дешевые товары
💎 Дорогие - самые дорогие товары
📊 Статистика - сколько всего товаров

*КОМАНДЫ:*
/sales - товары со скидкой
/stats - статистика по товарам

*ПРИМЕРЫ ЗАПРОСОВ:*
"платья до 3000" - платья до 3000 рублей
"юбки" - все юбки
"блузки со скидкой" - блузки со скидкой
"до 2000" - все товары до 2000 рублей
"""
    
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

# Команда /sales
@bot.message_handler(commands=['sales'])
def show_sales(message):
    """Показать товары со скидкой со ссылками"""
    if not products:
        bot.send_message(message.chat.id, "😔 Товары не загружены. Сначала запустите парсер.")
        return
    
    # Ищем товары со скидкой
    sales = []
    for product in products:
        if product.get('discount', 0) > 0:
            sales.append(product)
    
    if not sales:
        bot.send_message(message.chat.id, "😔 Нет товаров со скидкой")
        return
    
    # Сортируем по скидке (самые большие сначала)
    def get_discount_value(product):
      return product.get('discount', 0)

sales.sort(key=get_discount_value, reverse=True)    
    # Формируем ответ со ссылками
    text = "🔥 *ТОВАРЫ СО СКИДКОЙ:*\n\n"
    
    for i, product in enumerate(sales[:5], 1):
        name = product['name']
        if len(name) > 40:
            name = name[:40] + "..."
        
        text += f"*{i}. {name}*\n"
        text += f"💰 *{product.get('price', '?')} руб*"
        
        if product.get('old_price'):
            text += f" (было {product['old_price']} руб)"
        
        text += f"\n🎯 Скидка: *{product.get('discount', 0)}%*\n"
        
        # ДОБАВЛЯЕМ ССЫЛКУ
        if product.get('url'):
            text += f"🔗 [Посмотреть на сайте]({product['url']})\n"
        elif product.get('category'):
            text += f"🏷️ {product['category']}\n"
        
        text += "\n"
    
    if len(sales) > 5:
        text += f"*...и еще {len(sales)-5} товаров*"
    
    bot.send_message(
        message.chat.id, 
        text, 
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

# Команда /stats
@bot.message_handler(commands=['stats'])
def show_stats(message):
    """Показать статистику"""
    if not products:
        bot.send_message(message.chat.id, "😔 Товары не загружены")
        return
    
    total = len(products)
    
    # Считаем товары со скидкой
    with_discount = 0
    for product in products:
        if product.get('discount', 0) > 0:
            with_discount += 1
    
    # Считаем товары со ссылками
    with_url = 0
    for product in products:
        if product.get('url'):
            with_url += 1
    
    # Считаем по категориям
    categories = {}
    for product in products:
        category = product.get('category', 'Другое')
        categories[category] = categories.get(category, 0) + 1
    
    # Формируем ответ
    text = f"""
📊 *СТАТИСТИКА ZARINA*

📦 Всего товаров: {total}
💰 Со скидкой: {with_discount} ({round(with_discount/total*100, 1) if total > 0 else 0}%)
🔗 Со ссылками: {with_url}

*Товаров по категориям:*
"""
    
    for category, count in categories.items():
        text += f"• {category}: {count} шт.\n"
    
    # Средняя цена
    if products:
        total_price = 0
        count = 0
        for product in products:
            price = product.get('price')
            if price:
                total_price += price
                count += 1
        
        if count > 0:
            avg_price = total_price // count
            text += f"\n💵 Средняя цена: {avg_price} руб"
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

def show_product_list(message, product_list, title):
    """Показать список товаров со ссылками"""
    if not product_list:
        bot.send_message(message.chat.id, f"😔 В '{title}' ничего не найдено")
        return
    
    text = f"📋 *{title}*\n"
    text += f"📊 Найдено: *{len(product_list)}* товаров\n\n"
    
    # Показываем первые 5 товаров
    show_count = min(5, len(product_list))
    
    for i in range(show_count):
        product = product_list[i]
        name = product['name']
        if len(name) > 40:
            name = name[:40] + "..."
        
        text += f"*{i+1}. {name}*\n"
        
        if product.get('price'):
            text += f"💰 *{product['price']} руб*\n"
            
            if product.get('discount', 0) > 0:
                text += f"🎯 Скидка: {product['discount']}%\n"
        
        # ДОБАВЛЯЕМ ССЫЛКУ, если она есть
        if product.get('url'):
            text += f"🔗 [Посмотреть на сайте]({product['url']})\n"
        elif product.get('category'):
            text += f"🏷️ {product.get('category', '')}\n"
        
        text += "\n"
    
    if len(product_list) > show_count:
        remaining = len(product_list) - show_count
        text += f"*... и еще {remaining} товаров*"
    
    bot.send_message(
        message.chat.id, 
        text, 
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

def show_category(message, category_name):
    """Показать товары категории"""
    # Фильтруем товары по категории
    filtered = []
    for product in products:
        if category_name.lower() in product.get('category', '').lower():
            filtered.append(product)
    
    show_product_list(message, filtered, category_name)

def show_cheapest(message):
    """Показать самые дешевые товары со ссылками"""
    # Фильтруем товары с ценой
    with_price = []
    for product in products:
        if product.get('price'):
            with_price.append(product)
    
    # Сортируем по цене
    def get_price_value_with_default(product):
    return product.get('price', 99999)

with_price.sort(key=get_price_value_with_default)    
    show_product_list(message, with_price[:10], "💰 Самые дешевые товары")

def show_most_expensive(message):
    """Показать самые дорогие товары со ссылками"""
    # Фильтруем товары с ценой
    with_price = []
    for product in products:
        if product.get('price'):
            with_price.append(product)
    
    # Сортируем по цене в обратном порядке
     
    show_product_list(message, with_price[:10], "💎 Самые дорогие товары")
def get_price_value(product):
    return product.get('price', 0)

with_price.sort(key=get_price_value, reverse=True)
def show_by_price(message, max_price):
    """Показать товары до указанной цены со ссылками"""
    filtered = []
    for product in products:
        price = product.get('price', 99999)
        if price <= max_price:
            filtered.append(product)
    
    if not filtered:
        bot.send_message(message.chat.id, f"😔 Нет товаров до {max_price} рублей")
        return
    
    # Сортируем по цене
    filtered.sort(key=get_price_value)    
    show_product_list(message, filtered, f"💰 Товары до {max_price} руб")

def search_products(message, search_text):
    """Поиск товаров по названию со ссылками"""
    found = []
    for product in products:
        if search_text in product['name'].lower():
            found.append(product)
    
    if found:
        show_product_list(message, found, f"🔍 По запросу '{search_text}'")
        return True
    
    # Если не нашли по точному совпадению, ищем частичное
    for product in products:
        if any(word in product['name'].lower() for word in search_text.split()):
            found.append(product)
    
    if found:
        show_product_list(message, found, f"🔍 По запросу '{search_text}'")
        return True
    
    return False

# Обработка всех текстовых сообщений
# Заменяем эту строку в декораторе:
# @bot.message_handler(func=lambda message: True)

def handle_all_messages(message):
    """Функция, которая всегда возвращает True для обработки всех сообщений"""
    return True

@bot.message_handler(func=handle_all_messages)
def handle_text(message):
    """Обрабатываем все текстовые сообщения"""
    text = message.text.lower()
    
    if not products and text != 'ℹ️ помощь':
        bot.send_message(message.chat.id, 
                        "📭 Сначала загрузите товары!\n\nЗапустите файл run_parser.py",
                        reply_markup=create_keyboard())
        return
    
    # Обрабатываем кнопки
    if "плать" in text or "👗" in text:
        show_category(message, "Платья")
    elif "блуз" in text or "👚" in text:
        show_category(message, "Блузки")
    elif "юбк" in text or "✨" in text:
        show_category(message, "Юбки")
    elif "брюк" in text or "👖" in text:
        show_category(message, "Брюки")
    elif "скидк" in text or "🔥" in text:
        show_sales(message)
    elif "дешев" in text or "💰" in text:
        show_cheapest(message)
    elif "дорог" in text or "💎" in text:
        show_most_expensive(message)
    elif "статистик" in text or "📊" in text:
        show_stats(message)
    elif "помощ" in text or "ℹ️" in text:
        help_message(message)
    elif "до" in text:
        # Ищем число в тексте
        numbers = re.findall(r'\d+', text)
        if numbers:
            max_price = int(numbers[0])
            show_by_price(message, max_price)
        else:
            bot.send_message(message.chat.id, "Напишите 'до 2000' или 'до 3000'")
    elif len(text) > 2:
        # Если запрос длиннее 2 символов, ищем товары
        if not search_products(message, text):
            bot.send_message(message.chat.id,
                           f"🔍 *По запросу '{text}' ничего не найдено*\n\nПопробуйте другой запрос или напишите /help для справки",
                           parse_mode='Markdown',
                           reply_markup=create_keyboard())
    else:
        bot.send_message(message.chat.id,
                       "🤔 Не понял запрос\n\nНапишите /help для справки",
                       reply_markup=create_keyboard())

# Запуск бота
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🤖 TELEGRAM БОТ ДЛЯ ZARINA")
    print("=" * 50)
    print("\n📱 Откройте Telegram")
    print("🔍 Найдите своего бота")
    print("💬 Напишите /start чтобы начать")
    print("🛑 Для остановки нажмите Ctrl+C")
    print("=" * 50 + "\n")
    
    try:
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:

        print(f"❌ Ошибка: {e}")

