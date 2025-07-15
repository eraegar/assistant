#!/usr/bin/env python3
"""
Create a manager user in the database
"""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
import models
import auth

def create_manager():
    """Create or update manager"""
    print("🔧 Создание или обновление менеджера...")
    
    db = database.SessionLocal()
    try:
        manager_phone = "+79089050077"
        manager_password = "admin32451124"
        manager_email = "Malina2701@mail.ru"
        
        # Check if manager already exists
        manager = db.query(models.User).filter(
            models.User.phone == manager_phone,
            models.User.role == models.UserRole.manager
        ).first()
        
        hashed_password = auth.get_password_hash(manager_password)
        
        if manager:
            print(f"🔄 Менеджер с телефоном {manager_phone} уже существует. Обновление пароля...")
            manager.password_hash = hashed_password
            manager.name = "Менеджер"
            
            if not manager.manager_profile:
                # Add profile if it's missing for some reason
                manager_profile = models.ManagerProfile(
                    user_id=manager.id,
                    email=manager_email,
                    department="Operations"
                )
                db.add(manager_profile)
            else:
                manager.manager_profile.email = manager_email

            print("✅ Пароль менеджера успешно обновлен.")
        
        else:
            print("✨ Создание нового менеджера...")
            # Create user
            db_user = models.User(
                phone=manager_phone,
                name="Менеджер Алина",
                password_hash=hashed_password,
                role=models.UserRole.manager,
                telegram_username="main_manager"
            )
            db.add(db_user)
            db.flush()
        
            # Create manager profile
            manager_profile = models.ManagerProfile(
                user_id=db_user.id,
                email=manager_email,
                department="Operations"
            )
            db.add(manager_profile)
            manager = db_user
            print("✅ Новый менеджер успешно создан.")
        
        db.commit()
        db.refresh(manager)
        
        print("\n🎉 Готово!")
        print(f"   ID: {manager.id}")
        print(f"   Имя: {manager.name}")
        print(f"   Телефон: {manager.phone}")
        
        # Verify password
        is_valid = auth.verify_password(manager_password, manager.password_hash)
        print(f"   Пароль '{manager_password}' установлен: {'✅' if is_valid else '❌'}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_manager() 