"""
Streamlit интерфейс для предсказания цен на квартиры
"""

import streamlit as st
import requests
import json

# Конфигурация страницы
st.set_page_config(
    page_title="Предсказание цен на квартиры",
    page_icon="🏠",
    layout="wide"
)

# Стили
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 18px;
    }
    .prediction-result {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin-top: 20px;
    }
    .price-display {
        font-size: 36px;
        font-weight: bold;
        color: #0066cc;
        text-align: center;
        margin: 10px 0;
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Заголовок
st.title("🏠 Предсказание цен на квартиры")
st.markdown("Заполните информацию о квартире и получите предсказанную цену")

# URL API (можно изменить в боковой панели)
with st.sidebar:
    st.header("Настройки")
    api_url = st.text_input(
        "URL API", 
        value="http://localhost:8000",
        help="Адрес FastAPI сервера"
    )
    
    st.markdown("---")
    st.markdown("### Информация")
    st.markdown("Это приложение использует ML модель для предсказания цен на недвижимость.")
    
    # Проверка соединения с API
    if st.button("Проверить соединение с API"):
        try:
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("model_loaded"):
                    st.success("✅ API доступен, модель загружена")
                else:
                    st.warning("⚠️ API доступен, но модель не загружена")
            else:
                st.error(f"❌ API недоступен (код: {response.status_code})")
        except Exception as e:
            st.error(f"❌ Ошибка соединения: {str(e)}")

# Основные поля для ввода - в двух колонках
col1, col2 = st.columns(2)

with col1:
    st.subheader("Основные параметры")
    
    # Числовые параметры
    area = st.number_input(
        "Общая площадь (кв.м)*", 
        min_value=10.0, 
        max_value=300.0, 
        value=55.0,
        step=0.5,
        help="Общая площадь квартиры"
    )
    
    number_of_rooms = st.number_input(
        "Количество комнат*", 
        min_value=0.5, 
        max_value=10.0, 
        value=2.0,
        step=0.5,
        help="Количество комнат (0.5 - студия)"
    )
    
    minutes_to_metro = st.number_input(
        "Минут до метро*", 
        min_value=0.0, 
        max_value=120.0, 
        value=10.0,
        step=0.5,
        help="Время пешком до ближайшей станции метро"
    )
    
    living_area = st.number_input(
        "Жилая площадь (кв.м)*", 
        min_value=5.0, 
        max_value=200.0, 
        value=35.0,
        step=0.5,
        help="Площадь жилых комнат"
    )
    
    kitchen_area = st.number_input(
        "Площадь кухни (кв.м)*", 
        min_value=3.0, 
        max_value=50.0, 
        value=9.0,
        step=0.5,
        help="Площадь кухни"
    )

with col2:
    st.subheader("Дополнительные параметры")
    
    # Категориальные параметры
    region = st.selectbox(
        "Район*",
        ["ЦАО", "СВАО", "ЮАО", "ЗАО", "САО", "ВАО", "ЮВАО", "СЗАО"],
        index=0,
        help="Административный район"
    )
    
    apartment_type = st.selectbox(
        "Тип квартиры*",
        ["Вторичка", "Новостройка"],
        index=0,
        help="Тип недвижимости"
    )
    
    renovation = st.selectbox(
        "Ремонт*",
        ["Без ремонта", "Косметический", "Дизайнерский", "Евроремонт"],
        index=1,
        help="Состояние ремонта"
    )
    
    metro_station = st.text_input(
        "Станция метро*", 
        value="Киевская",
        help="Ближайшая станция метро"
    )
    
    # Параметры этажности
    col_floor1, col_floor2 = st.columns(2)
    
    with col_floor1:
        floor = st.number_input(
            "Этаж*", 
            min_value=1, 
            max_value=50, 
            value=5,
            step=1,
            help="Этаж квартиры"
        )
    
    with col_floor2:
        number_of_floors = st.number_input(
            "Этажей в доме*", 
            min_value=1, 
            max_value=50, 
            value=9,
            step=1,
            help="Всего этажей в доме"
        )

# Проверка корректности ввода
if floor > number_of_floors:
    st.warning("⚠️ Этаж квартиры не может быть больше общего количества этажей в доме")

if living_area > area:
    st.warning("⚠️ Жилая площадь не может быть больше общей площади")

# Кнопка предсказания
st.markdown("---")
if st.button("📊 Предсказать цену", type="primary"):
    # Проверка заполнения всех полей
    required_fields = [
        area, number_of_rooms, minutes_to_metro, living_area, kitchen_area,
        floor, number_of_floors, metro_station
    ]
    
    if not all(required_fields):
        st.error("❌ Пожалуйста, заполните все обязательные поля (отмечены *)")
    elif floor > number_of_floors:
        st.error("❌ Этаж квартиры не может быть больше общего количества этажей в доме")
    elif living_area > area:
        st.error("❌ Жилая площадь не может быть больше общей площади")
    else:
        # Подготовка данных для API
        data = {
            "minutes_to_metro": float(minutes_to_metro),
            "number_of_rooms": float(number_of_rooms),
            "area": float(area),
            "living_area": float(living_area),
            "kitchen_area": float(kitchen_area),
            "floor": float(floor),
            "number_of_floors": int(number_of_floors),
            "apartment_type": apartment_type,
            "metro_station": metro_station,
            "region": region,
            "renovation": renovation
        }
        
        # Индикатор загрузки
        with st.spinner("⏳ Отправка запроса к API..."):
            try:
                # Отправка запроса
                response = requests.post(
                    f"{api_url}/predict",
                    json=data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("success"):
                        price = result.get("price", 0)
                        
                        # Отображение результата
                        st.markdown("### 📈 Результат предсказания")
                        
                        col_result1, col_result2 = st.columns([2, 1])
                        
                        with col_result1:
                            st.markdown(f'<div class="price-display">{price:,.0f} ₽</div>', 
                                      unsafe_allow_html=True)
                            
                            # Конвертация в миллионы
                            price_millions = price / 1_000_000
                            st.markdown(f"**{price_millions:,.1f} млн рублей**")
                            
                            # Дополнительная информация
                            st.markdown("---")
                            st.markdown("#### 📋 Введенные параметры:")
                            
                            # Компактное отображение параметров
                            params_col1, params_col2 = st.columns(2)
                            with params_col1:
                                st.markdown(f"**Площадь:** {area} кв.м")
                                st.markdown(f"**Комнат:** {number_of_rooms}")
                                st.markdown(f"**Район:** {region}")
                                st.markdown(f"**Метро:** {metro_station}")
                            
                            with params_col2:
                                st.markdown(f"**Этаж:** {floor}/{number_of_floors}")
                                st.markdown(f"**Тип:** {apartment_type}")
                                st.markdown(f"**Ремонт:** {renovation}")
                                st.markdown(f"**До метро:** {minutes_to_metro} мин")
                        
                        with col_result2:
                            # Визуализация
                            st.metric(
                                label="Предсказанная цена",
                                value=f"{price_millions:,.1f} млн ₽"
                            )
                            
                            # Кнопка для копирования
                            if st.button("📋 Копировать цену"):
                                st.write(f"Скопировано: {price:,.0f} ₽")
                    
                    else:
                        st.error(f"❌ Ошибка предсказания: {result.get('error', 'Неизвестная ошибка')}")
                
                else:
                    st.error(f"❌ Ошибка API (код {response.status_code}): {response.text}")
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Не удалось подключиться к API. Убедитесь, что сервер запущен.")
                st.info(f"Проверьте адрес: {api_url}")
            
            except requests.exceptions.Timeout:
                st.error("⏰ Таймаут запроса. Сервер не ответил вовремя.")
            
            except Exception as e:
                st.error(f"❌ Неизвестная ошибка: {str(e)}")

# Раздел с примерами
with st.expander("📋 Примеры квартир (быстрый ввод)"):
    col_ex1, col_ex2, col_ex3 = st.columns(3)
    
    with col_ex1:
        if st.button("Студия в ЦАО", use_container_width=True):
            st.session_state.area = 35.0
            st.session_state.number_of_rooms = 0.5
            st.session_state.minutes_to_metro = 5.0
            st.session_state.living_area = 25.0
            st.session_state.kitchen_area = 7.0
            st.session_state.region = "ЦАО"
            st.session_state.apartment_type = "Вторичка"
            st.session_state.renovation = "Косметический"
            st.session_state.metro_station = "Арбатская"
            st.session_state.floor = 3
            st.session_state.number_of_floors = 9
            st.rerun()
    
    with col_ex2:
        if st.button("2-комн. в новостройке", use_container_width=True):
            st.session_state.area = 65.0
            st.session_state.number_of_rooms = 2.0
            st.session_state.minutes_to_metro = 15.0
            st.session_state.living_area = 45.0
            st.session_state.kitchen_area = 12.0
            st.session_state.region = "СВАО"
            st.session_state.apartment_type = "Новостройка"
            st.session_state.renovation = "Без ремонта"
            st.session_state.metro_station = "Бабушкинская"
            st.session_state.floor = 12
            st.session_state.number_of_floors = 25
            st.rerun()
    
    with col_ex3:
        if st.button("3-комн. с ремонтом", use_container_width=True):
            st.session_state.area = 85.0
            st.session_state.number_of_rooms = 3.0
            st.session_state.minutes_to_metro = 8.0
            st.session_state.living_area = 60.0
            st.session_state.kitchen_area = 15.0
            st.session_state.region = "ЮАО"
            st.session_state.apartment_type = "Вторичка"
            st.session_state.renovation = "Дизайнерский"
            st.session_state.metro_station = "Коломенская"
            st.session_state.floor = 7
            st.session_state.number_of_floors = 16
            st.rerun()

# Инструкция
st.markdown("---")
st.markdown("### 📖 Инструкция")
st.markdown("""
1. Заполните все поля формы (обязательные поля отмечены *)
2. Нажмите кнопку **"Предсказать цену"**
3. Дождитесь результата от ML модели

**Примечания:**
- Для быстрого заполнения используйте примеры выше
- Убедитесь, что FastAPI сервер запущен на указанном адресе
- При возникновении ошибок проверьте соединение с API
""")

# Футер
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "ML модель для предсказания цен на недвижимость • "
    f"API: <code>{api_url}</code>"
    "</div>",
    unsafe_allow_html=True
)

# Инициализация состояния сессии
if 'area' not in st.session_state:
    st.session_state.area = 55.0
if 'number_of_rooms' not in st.session_state:
    st.session_state.number_of_rooms = 2.0
if 'minutes_to_metro' not in st.session_state:
    st.session_state.minutes_to_metro = 10.0
if 'living_area' not in st.session_state:
    st.session_state.living_area = 35.0
if 'kitchen_area' not in st.session_state:
    st.session_state.kitchen_area = 9.0
if 'region' not in st.session_state:
    st.session_state.region = "ЦАО"
if 'apartment_type' not in st.session_state:
    st.session_state.apartment_type = "Вторичка"
if 'renovation' not in st.session_state:
    st.session_state.renovation = "Косметический"
if 'metro_station' not in st.session_state:
    st.session_state.metro_station = "Киевская"
if 'floor' not in st.session_state:
    st.session_state.floor = 5
if 'number_of_floors' not in st.session_state:
    st.session_state.number_of_floors = 9