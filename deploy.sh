#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Переходим в рабочую директорию
cd /root/project/App

log "Начинаю развертывание Telegram Assistant на продакшн сервере..."

# Остановка существующих процессов
log "Остановка существующих процессов..."
pkill -f "uvicorn" || true
pkill -f "npm start" || true
pkill -f "cloudflared" || true

# Установка зависимостей для Backend
log "Установка зависимостей для Backend..."
cd Backend
python3 -m pip install -r requirements.txt
cd ..

# Установка зависимостей для Frontend приложений
log "Установка зависимостей для Frontend приложений..."

# Основное приложение
cd Frontend/client-app
npm install
cd ../..

# Менеджер приложение
cd Frontend/manager-app
npm install
cd ../..

# Ассистент приложение
cd Frontend/assistant-app
npm install
cd ../..

# Инициализация базы данных
log "Инициализация базы данных..."
cd Backend
python3 init_db.py
cd ..

# Создание systemd сервисов
log "Создание systemd сервисов..."

# Backend сервис
cat > /etc/systemd/system/rent-assistant-backend.service << 'EOF'
[Unit]
Description=Rent Assistant Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/project/App/Backend
Environment=PATH=/usr/bin:/usr/local/bin
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Frontend Client сервис
cat > /etc/systemd/system/rent-assistant-client.service << 'EOF'
[Unit]
Description=Rent Assistant Client App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/project/App/Frontend/client-app
Environment=PATH=/usr/bin:/usr/local/bin:/usr/local/lib/nodejs/bin
Environment=NODE_ENV=production
Environment=PORT=3000
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Frontend Manager сервис
cat > /etc/systemd/system/rent-assistant-manager.service << 'EOF'
[Unit]
Description=Rent Assistant Manager App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/project/App/Frontend/manager-app
Environment=PATH=/usr/bin:/usr/local/bin:/usr/local/lib/nodejs/bin
Environment=NODE_ENV=production
Environment=PORT=3001
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Frontend Assistant сервис
cat > /etc/systemd/system/rent-assistant-assistant.service << 'EOF'
[Unit]
Description=Rent Assistant Assistant App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/project/App/Frontend/assistant-app
Environment=PATH=/usr/bin:/usr/local/bin:/usr/local/lib/nodejs/bin
Environment=NODE_ENV=production
Environment=PORT=3002
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Cloudflared Tunnel сервис
cat > /etc/systemd/system/rent-assistant-tunnel.service << 'EOF'
[Unit]
Description=Rent Assistant Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/project/App
ExecStart=/usr/local/bin/cloudflared tunnel --config cloudflared-config.yml run
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка systemd
log "Перезагрузка systemd..."
systemctl daemon-reload

# Включение и запуск сервисов
log "Включение и запуск сервисов..."
systemctl enable rent-assistant-backend
systemctl enable rent-assistant-client
systemctl enable rent-assistant-manager
systemctl enable rent-assistant-assistant
systemctl enable rent-assistant-tunnel

systemctl start rent-assistant-backend
systemctl start rent-assistant-client
systemctl start rent-assistant-manager
systemctl start rent-assistant-assistant
systemctl start rent-assistant-tunnel

# Проверка статуса сервисов
log "Проверка статуса сервисов..."
sleep 5

services=("rent-assistant-backend" "rent-assistant-client" "rent-assistant-manager" "rent-assistant-assistant" "rent-assistant-tunnel")

for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        log "✅ $service: Запущен"
    else
        error "❌ $service: Не запущен"
        systemctl status "$service" --no-pager -l
    fi
done

# Проверка портов
log "Проверка портов..."
ports=(8000 3000 3001 3002)

for port in "${ports[@]}"; do
    if netstat -tuln | grep -q ":$port "; then
        log "✅ Порт $port: Открыт"
    else
        warn "⚠️ Порт $port: Не открыт"
    fi
done

warn "ВАЖНО: Для завершения настройки необходимо создать DNS записи в Cloudflare!"
warn "Следуйте инструкциям в файле DNS_SETUP_INSTRUCTIONS.md"
log "Развертывание завершено!"
log "После настройки DNS записей ваше приложение будет доступно по адресу: https://rent-assistant.ru" 