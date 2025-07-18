#!/usr/bin/env python3
"""
Тестирование форматирования номеров телефонов при создании ассистентов
"""

import sys
import os
import requests
import json

# Добавляем родительскую директорию в path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models

def get_manager_token():
    """Получить токен менеджера для авторизации"""
    login_data = {
        "phone": "+79999999999",
        "password": "admin123"
    }
    
    response = requests.post("http://localhost:8000/api/v1/management/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Ошибка авторизации менеджера: {response.text}")
        return None

def test_assistant_creation_with_phone_formats():
    """Тестирование создания ассистентов с различными форматами номеров"""
    
    # Получаем токен менеджера
    token = get_manager_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Тестовые номера в различных форматах
    test_cases = [
        {
            "name": "Тест 1: +79123456781",
            "phone_input": "+79123456781",
            "expected_db": "+79123456781",
            "assistant_name": "Тестовый Ассистент 1"
        },
        {
            "name": "Тест 2: 89123456782", 
            "phone_input": "89123456782",
            "expected_db": "+79123456782",
            "assistant_name": "Тестовый Ассистент 2"
        },
        {
            "name": "Тест 3: 79123456783",
            "phone_input": "79123456783", 
            "expected_db": "+79123456783",
            "assistant_name": "Тестовый Ассистент 3"
        },
        {
            "name": "Тест 4: 9123456784",
            "phone_input": "9123456784",
            "expected_db": "+79123456784", 
            "assistant_name": "Тестовый Ассистент 4"
        }
    ]
    
    db = SessionLocal()
    results = []
    
    print("🧪 Тестирование форматирования номеров телефонов при создании ассистентов\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📞 {test_case['name']}")
        print(f"   Входной номер: {test_case['phone_input']}")
        print(f"   Ожидаемый в БД: {test_case['expected_db']}")
        
        # Подготавливаем данные ассистента
        assistant_data = {
            "name": test_case["assistant_name"],
            "phone": test_case["phone_input"],
            "email": f"test{i}@example.com",
            "password": "testpass123",
            "specialization": "personal_only",
            "telegram_username": f"test_assistant_{i}"
        }
        
        try:
            # Отправляем запрос на создание ассистента
            response = requests.post(
                "http://localhost:8000/api/v1/management/assistants/create",
                headers=headers,
                json=assistant_data
            )
            
            if response.status_code == 200:
                result_data = response.json()
                print(f"   ✅ Ассистент создан: {result_data['name']}")
                
                # Проверяем номер в базе данных
                user = db.query(models.User).filter(
                    models.User.name == test_case["assistant_name"]
                ).first()
                
                if user:
                    actual_phone = user.phone
                    expected_phone = test_case["expected_db"]
                    
                    if actual_phone == expected_phone:
                        print(f"   ✅ Номер в БД корректный: {actual_phone}")
                        results.append({
                            "test": test_case["name"],
                            "status": "PASS",
                            "input": test_case["phone_input"], 
                            "expected": expected_phone,
                            "actual": actual_phone
                        })
                    else:
                        print(f"   ❌ Номер в БД некорректный: ожидалось {expected_phone}, получено {actual_phone}")
                        results.append({
                            "test": test_case["name"],
                            "status": "FAIL",
                            "input": test_case["phone_input"],
                            "expected": expected_phone, 
                            "actual": actual_phone
                        })
                else:
                    print(f"   ❌ Пользователь не найден в БД")
                    results.append({
                        "test": test_case["name"],
                        "status": "FAIL",
                        "input": test_case["phone_input"],
                        "expected": test_case["expected_db"],
                        "actual": "NOT_FOUND"
                    })
                    
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                print(f"   ❌ Ошибка создания: {error_data}")
                results.append({
                    "test": test_case["name"],
                    "status": "ERROR",
                    "input": test_case["phone_input"],
                    "expected": test_case["expected_db"],
                    "actual": f"API_ERROR: {error_data}"
                })
                
        except Exception as e:
            print(f"   ❌ Исключение: {str(e)}")
            results.append({
                "test": test_case["name"],
                "status": "EXCEPTION",
                "input": test_case["phone_input"],
                "expected": test_case["expected_db"],
                "actual": f"EXCEPTION: {str(e)}"
            })
        
        print()
    
    # Итоговые результаты
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print("=" * 80)
    
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    
    for result in results:
        status_emoji = "✅" if result["status"] == "PASS" else "❌"
        print(f"{status_emoji} {result['test']}")
        print(f"   Вход: {result['input']} → Ожидаемый: {result['expected']} → Фактический: {result['actual']}")
        print()
    
    print(f"🎯 Успешно: {passed}/{total} тестов")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Форматирование номеров работает корректно.")
    else:
        print("⚠️  Есть проблемы с форматированием номеров.")
    
    db.close()

def cleanup_test_assistants():
    """Очистка тестовых ассистентов"""
    db = SessionLocal()
    
    test_names = [
        "Тестовый Ассистент 1",
        "Тестовый Ассистент 2", 
        "Тестовый Ассистент 3",
        "Тестовый Ассистент 4"
    ]
    
    deleted_count = 0
    for name in test_names:
        user = db.query(models.User).filter(models.User.name == name).first()
        if user:
            # Удаляем профиль ассистента
            if user.assistant_profile:
                db.delete(user.assistant_profile)
            
            # Удаляем пользователя
            db.delete(user)
            deleted_count += 1
    
    db.commit()
    print(f"🧹 Удалено {deleted_count} тестовых ассистентов")
    db.close()

if __name__ == "__main__":
    print("🚀 Запуск тестирования форматирования номеров телефонов...")
    print()
    
    # Сначала очищаем возможные предыдущие тестовые данные
    cleanup_test_assistants()
    print()
    
    # Запускаем тесты
    test_assistant_creation_with_phone_formats()
    print()
    
    # Очищаем тестовые данные после тестов
    print("🧹 Очистка тестовых данных...")
    cleanup_test_assistants() 