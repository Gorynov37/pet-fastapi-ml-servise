"""
Streamlit интерфейс для предсказания цен на квартиры
"""

import streamlit as st
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

ip_api = "prediction-api"
port_api = "4242"

PREDICT_ENDPOINT = "/predict"  # при необходимости поменяй на актуальный эндпоинт

st.title("Apartment Price / Prediction")

st.write("Введите параметры квартиры:")

# --- Числовые поля (float) ---
minutes_to_metro = st.text_input("Minutes to metro (minutes_to_metro)", value="10")
number_of_rooms = st.text_input("Number of rooms (number_of_rooms)", value="2")
area = st.text_input("Total area, m² (area)", value="50")
living_area = st.text_input("Living area, m² (living_area)", value="30")
kitchen_area = st.text_input("Kitchen area, m² (kitchen_area)", value="10")
floor = st.text_input("Floor (floor)", value="5")

# --- Числовое поле (int) ---
number_of_floors = st.text_input("Number of floors in building (number_of_floors, int)", value="16")

# --- Строковые поля ---
apartment_type = st.selectbox(
    "Apartment type (apartment_type)",
    ['Secondary', 'New building'],
)

metro_station = st.text_input("Metro station (metro_station)", value="Алтуфьево")

region = st.selectbox(
    "Region (region)",
    ['Moscow region', 'Moscow'],
)

renovation = st.selectbox(
    "Renovation (renovation)",
    ['Cosmetic', 'European-style renovation', 'Without renovation', 'Designer'],
)

# -----------------------
# Вспомогательные функции
# -----------------------
def parse_float(field_name: str, raw_value: str) -> float:
    """
    Преобразует строку в float. Поддерживает запятую как разделитель.
    Выбрасывает ValueError с понятным текстом.
    """
    if raw_value is None:
        raise ValueError(f"{field_name}: значение пустое")
    s = raw_value.strip().replace(",", ".")
    if s == "":
        raise ValueError(f"{field_name}: значение пустое")
    try:
        return float(s)
    except ValueError as exc:
        raise ValueError(f"{field_name}: нужно число (например 10 или 10.5)") from exc


def parse_int(field_name: str, raw_value: str) -> int:
    """
    Преобразует строку в int.
    Выбрасывает ValueError с понятным текстом.
    """
    if raw_value is None:
        raise ValueError(f"{field_name}: значение пустое")
    s = raw_value.strip()
    if s == "":
        raise ValueError(f"{field_name}: значение пустое")
    # допускаем ввод "16.0" как ошибку, чтобы не было скрытого округления
    if any(ch in s for ch in [".", ","]):
        raise ValueError(f"{field_name}: нужно целое число (например 16)")
    try:
        return int(s)
    except ValueError as exc:
        raise ValueError(f"{field_name}: нужно целое число (например 16)") from exc


def non_empty_str(field_name: str, raw_value: str) -> str:
    s = (raw_value or "").strip()
    if not s:
        raise ValueError(f"{field_name}: строка не должна быть пустой")
    return s


# Мягкая inline-валидация (покажем ошибки сразу под полями)
numeric_errors = []

for name, raw in [
    ("minutes_to_metro", minutes_to_metro),
    ("number_of_rooms", number_of_rooms),
    ("area", area),
    ("living_area", living_area),
    ("kitchen_area", kitchen_area),
    ("floor", floor),
]:
    try:
        parse_float(name, raw)
    except ValueError as e:
        numeric_errors.append(str(e))

try:
    parse_int("number_of_floors", number_of_floors)
except ValueError as e:
    numeric_errors.append(str(e))

if numeric_errors:
    # Показываем все найденные ошибки, но не блокируем ввод — блок будет только на Predict
    for err in numeric_errors:
        st.error(err)

# -----------------------
# Отправка на API
# -----------------------
if st.button("Predict"):
    errors = []

    # Парсим числа
    try:
        minutes_to_metro_f = parse_float("minutes_to_metro", minutes_to_metro)
    except ValueError as e:
        errors.append(str(e))

    try:
        number_of_rooms_f = parse_float("number_of_rooms", number_of_rooms)
    except ValueError as e:
        errors.append(str(e))

    try:
        area_f = parse_float("area", area)
    except ValueError as e:
        errors.append(str(e))

    try:
        living_area_f = parse_float("living_area", living_area)
    except ValueError as e:
        errors.append(str(e))

    try:
        kitchen_area_f = parse_float("kitchen_area", kitchen_area)
    except ValueError as e:
        errors.append(str(e))

    try:
        floor_f = parse_float("floor", floor)
    except ValueError as e:
        errors.append(str(e))

    try:
        number_of_floors_i = parse_int("number_of_floors", number_of_floors)
    except ValueError as e:
        errors.append(str(e))

    # Строки
    try:
        apartment_type_s = non_empty_str("apartment_type", apartment_type)
    except ValueError as e:
        errors.append(str(e))

    try:
        metro_station_s = non_empty_str("metro_station", metro_station)
    except ValueError as e:
        errors.append(str(e))

    try:
        region_s = non_empty_str("region", region)
    except ValueError as e:
        errors.append(str(e))

    try:
        renovation_s = non_empty_str("renovation", renovation)
    except ValueError as e:
        errors.append(str(e))

    if errors:
        for err in errors:
            st.error(err)
    else:
        data = {
            "minutes_to_metro": minutes_to_metro_f,
            "number_of_rooms": number_of_rooms_f,
            "area": area_f,
            "living_area": living_area_f,
            "kitchen_area": kitchen_area_f,
            "floor": floor_f,
            "number_of_floors": number_of_floors_i,
            "apartment_type": apartment_type_s,
            "metro_station": metro_station_s,
            "region": region_s,
            "renovation": renovation_s,
        }

        try:
            url = f"http://{ip_api}:{port_api}{PREDICT_ENDPOINT}"
            response = requests.post(url, json=data, timeout=10)

            if response.status_code == 200:
                # Универсально: если API вернёт {"prediction": ...} — покажем так же, как в твоём коде.
                # Если вернёт другой ключ — покажем весь JSON.
                try:
                    payload = response.json()
                except ValueError:
                    st.error("API вернул не-JSON ответ.")
                    st.text(response.text)
                else:
                    if isinstance(payload, dict) and "prediction" in payload:
                        st.success(f"Prediction: {payload['prediction']}")
                    else:
                        st.success("Response received:")
                        st.json(payload)
            else:
                st.error(f"Request failed with status code {response.status_code}")
                st.text(response.text)

        except ConnectionError:
            st.error("Failed to connect to the server.")
        except Timeout:
            st.error("Request timed out.")
        except RequestException as e:
            st.error("Request error.")
            st.text(str(e))
