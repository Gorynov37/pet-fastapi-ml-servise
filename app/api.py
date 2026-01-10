"""
Простое API для предсказания цен на квартиры
"""

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Загружаем модель один раз при старте
try:
    model = joblib.load("price_model_light.pkl")
    print("✅ Модель загружена успешно")
except:
    print("❌ Не удалось загрузить модель")
    model = None

# Создаем приложение
app = FastAPI(title="Price Prediction API", version="1.0")

# Модель для входных данных (все поля обязательные)
class ApartmentInput(BaseModel):
    minutes_to_metro: float
    number_of_rooms: float
    area: float
    living_area: float
    kitchen_area: float
    floor: float
    number_of_floors: int
    apartment_type: str
    metro_station: str
    region: str
    renovation: str

# Ручка для проверки здоровья
@app.get("/health")
async def health_check():
    """Проверка доступности сервиса"""
    return {
        "status": "ok" if model is not None else "error",
        "model_loaded": model is not None
    }

# Основная ручка для предсказания
@app.post("/predict")
async def predict(apartment: ApartmentInput):
    """Предсказать цену квартиры"""
    if model is None:
        return {"error": "Модель не загружена"}
    
    try:
        # Преобразуем входные данные в DataFrame
        data = pd.DataFrame([{
            'Minutes to metro': apartment.minutes_to_metro,
            'Number of rooms': apartment.number_of_rooms,
            'Area': apartment.area,
            'Living area': apartment.living_area,
            'Kitchen area': apartment.kitchen_area,
            'Floor': apartment.floor,
            'Number of floors': apartment.number_of_floors,
            'Apartment type': apartment.apartment_type,
            'Metro station': apartment.metro_station,
            'Region': apartment.region,
            'Renovation': apartment.renovation
        }])
        
        # Делаем предсказание
        prediction = model.predict(data)[0]
        
        return {
            "price": float(prediction),
            "currency": "RUB",
            "success": True
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}

# Корневая ручка
@app.get("/")
async def root():
    """Информация о API"""
    return {
        "name": "Price Prediction API",
        "version": "1.0",
        "endpoints": {
            "GET /": "Эта страница",
            "GET /health": "Проверка здоровья",
            "POST /predict": "Предсказать цену"
        }
    }

# Запуск сервера
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)