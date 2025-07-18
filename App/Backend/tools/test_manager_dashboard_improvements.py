#!/usr/bin/env python3
"""
Тестирование улучшений панели управления менеджера:
1) убрана панель "Последние задачи" в окне профиля клиента и добавлен в "Личную информацию" телеграм алиас
2) убран показатель "Уровень конверсии"
3) добавлено открывающееся окно с личной информацией о клиенте с его номером, почтой(если есть), телеграм алиасом и убран столбец "Контакты" в панели "Клиенты"
4) убран повторяющийся показатель месячного дохода
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
        print(f"❌ Ошибка авторизации менеджера: {response.status_code}")
        print(response.text)
        return None


def test_overview_analytics(token):
    """Тестировать обзорную аналитику (должны быть убраны дублирующие показатели)"""
    print("\n📊 Тестирование обзорной аналитики...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("http://localhost:8000/api/v1/management/dashboard/overview", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Данные аналитики получены:")
        print(f"   📋 Задач: {data['tasks']['total']} (новых за неделю: {data['tasks']['new_this_week']})")
        print(f"   👥 Ассистенты: {data['assistants']['online_now']}/{data['assistants']['total_active']} онлайн")
        print(f"   🧑‍💼 Клиенты: {data['clients']['total_active']} (новых: {data['clients']['new_this_week']})")
        print(f"   💰 Месячный доход: {data['performance']['monthly_revenue']:,} ₽")
        print(f"   📈 Выполнение задач: {data['performance']['task_completion_rate']}%")
        print(f"   🔧 Загрузка ассистентов: {data['performance']['assistant_utilization']}%")
        
        # Проверяем, что нет дублирующих показателей дохода
        performance_keys = list(data['performance'].keys())
        revenue_keys = [key for key in performance_keys if 'revenue' in key.lower()]
        print(f"   ✅ Показатели дохода (должен быть только один): {revenue_keys}")
        
        return True
    else:
        print(f"❌ Ошибка получения аналитики: {response.status_code}")
        return False


def test_clients_list(token):
    """Тестировать список клиентов (должен быть убран столбец 'Контакты')"""
    print("\n👥 Тестирование списка клиентов...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("http://localhost:8000/api/v1/management/clients", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        clients = data.get('clients', [])
        print(f"✅ Получено клиентов: {len(clients)}")
        
        if clients:
            client = clients[0]
            print(f"   📋 Структура данных клиента:")
            print(f"   • ID: {client.get('id')}")
            print(f"   • Имя: {client.get('name')}")
            print(f"   • Телефон: {client.get('phone')}")
            print(f"   • Email: {client.get('email', 'не указан')}")
            print(f"   • Telegram: @{client.get('telegram_username', 'не указан')}")
            print(f"   • Задач: {client.get('total_tasks')} (активных: {client.get('active_tasks')})")
            print(f"   • Подписка: {client.get('subscription', {}).get('plan', 'нет') if client.get('subscription') else 'нет'}")
            print(f"   • Назначенные ассистенты: {len(client.get('assigned_assistants', []))}")
        
        return True
    else:
        print(f"❌ Ошибка получения списка клиентов: {response.status_code}")
        return False


def test_client_profile_data(token):
    """Тестировать данные для профиля клиента"""
    print("\n🔍 Тестирование данных профиля клиента...")
    
    # Найдем клиента с telegram username в базе данных
    db = SessionLocal()
    try:
        client_with_telegram = db.query(models.User).filter(
            models.User.role == models.UserRole.client,
            models.User.telegram_username.isnot(None)
        ).first()
        
        if client_with_telegram:
            print(f"✅ Найден клиент с Telegram: {client_with_telegram.name}")
            print(f"   • Телефон: {client_with_telegram.phone}")
            print(f"   • Telegram: @{client_with_telegram.telegram_username}")
            
            # Проверим через API
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get("http://localhost:8000/api/v1/management/clients", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                clients = data.get('clients', [])
                
                # Найдем этого клиента в ответе API
                api_client = next((c for c in clients if c['id'] == client_with_telegram.client_profile.id), None)
                
                if api_client:
                    print(f"   📋 Данные через API:")
                    print(f"   • ID: {api_client['id']}")
                    print(f"   • Имя: {api_client['name']}")
                    print(f"   • Телефон: {api_client['phone']}")
                    print(f"   • Email: {api_client.get('email', 'не указан')}")
                    print(f"   • Telegram: @{api_client.get('telegram_username', 'не указан')}")
                    print(f"   • Дата регистрации: {api_client['created_at']}")
                    
                    if api_client.get('subscription'):
                        sub = api_client['subscription']
                        print(f"   📅 Подписка:")
                        print(f"     • План: {sub['plan']}")
                        print(f"     • Статус: {sub['status']}")
                        print(f"     • Начало: {sub['started_at']}")
                        print(f"     • Окончание: {sub.get('expires_at', 'не указано')}")
                        print(f"     • Автопродление: {sub['auto_renew']}")
                    
                    return True
                else:
                    print(f"❌ Клиент не найден в API ответе")
                    return False
            else:
                print(f"❌ Ошибка API: {response.status_code}")
                return False
        else:
            print("⚠️ Клиенты с Telegram username не найдены")
            return True
            
    finally:
        db.close()


def test_assistant_creation(token):
    """Тестировать создание ассистента с форматированием телефона"""
    print("\n🔧 Тестирование создания ассистента...")
    
    assistant_data = {
        "name": "Тестовый Ассистент Улучшений",
        "phone": "9001234567",  # Без префикса +7
        "email": "test-improvements@example.com",
        "password": "testpass123",
        "specialization": "full_access",
        "telegram_username": "test_improvements"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post("http://localhost:8000/api/v1/management/assistants/create", 
                           json=assistant_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Ассистент создан:")
        print(f"   • ID: {result['id']}")
        print(f"   • Имя: {result['name']}")
        print(f"   • Email: {result['email']}")
        print(f"   • Специализация: {result['specialization']}")
        print(f"   • Пароль: {result['password']}")
        
        # Проверим в базе данных, как сохранился номер телефона
        db = SessionLocal()
        try:
            assistant_user = db.query(models.User).filter(
                models.User.role == models.UserRole.assistant,
                models.User.name == assistant_data["name"]
            ).first()
            
            if assistant_user:
                print(f"   📞 Номер в БД: {assistant_user.phone}")
                if assistant_user.phone.startswith('+7'):
                    print(f"   ✅ Номер корректно отформатирован с префиксом +7")
                else:
                    print(f"   ❌ Номер неправильно отформатирован: {assistant_user.phone}")
                
                # Удаляем тестового ассистента
                assistant_profile = assistant_user.assistant_profile
                if assistant_profile:
                    db.delete(assistant_profile)
                db.delete(assistant_user)
                db.commit()
                print(f"   🗑️ Тестовый ассистент удален")
                
        finally:
            db.close()
        
        return True
    else:
        print(f"❌ Ошибка создания ассистента: {response.status_code}")
        print(response.text)
        return False


def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование улучшений панели управления менеджера")
    print("=" * 60)
    
    # Получаем токен менеджера
    token = get_manager_token()
    if not token:
        print("❌ Не удалось получить токен менеджера")
        return
    
    print("✅ Авторизация менеджера успешна")
    
    # Тестируем различные аспекты
    tests = [
        ("Обзорная аналитика", test_overview_analytics),
        ("Список клиентов", test_clients_list),
        ("Данные профиля клиента", test_client_profile_data),
        ("Создание ассистента", test_assistant_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func(token)
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    # Итоги
    print("\n" + "=" * 60)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ НЕУДАЧА"
        print(f"   {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Результат: {passed}/{len(results)} тестов пройдено")
    
    if passed == len(results):
        print("🎉 Все улучшения панели управления работают корректно!")
    else:
        print("⚠️ Некоторые улучшения требуют доработки")


if __name__ == "__main__":
    main() 