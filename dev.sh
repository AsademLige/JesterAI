#!/bin/bash

COMPOSE="docker compose"
COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"

compose() {
    $COMPOSE $COMPOSE_FILES "$@"
}

if [ "$1" = "rebuild" ]; then
    echo "reload..."

    compose up -d --build --no-deps api bot

    echo
    echo "reload success"
    exit 0
fi

if [ "$1" = "stop" ] || [ "$1" = "down" ]; then
    echo "🛑 Остановка локального стенда..."
    compose down
    echo "✅ Остановлено."
    exit 0
fi

echo "🚀 Запуск локального стенда Jester TMA..."

compose down > /dev/null 2>&1

compose up -d --build --remove-orphans

echo
echo "⏳ Ожидание Cloudflare Tunnel..."

BATTLE_API_URL=""
FRONTEND_URL=""

for i in {1..60}; do

    if [ -z "$BATTLE_API_URL" ]; then
        BATTLE_API_URL=$(
            compose logs --no-color cloudflared-api 2>&1 |
            grep -Eo 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' |
            head -n 1
        )
    fi

    if [ -z "$FRONTEND_URL" ]; then
        FRONTEND_URL=$(
            compose logs --no-color cloudflared-frontend 2>&1 |
            grep -Eo 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' |
            head -n 1
        )
    fi

    if [ -n "$BATTLE_API_URL" ] && [ -n "$FRONTEND_URL" ]; then
        break
    fi

    printf "."
    sleep 1
done

echo
echo "--------------------------------------------------"

if [ -n "$BATTLE_API_URL" ]; then
    echo "✅ API:"
    echo "   $BATTLE_API_URL"

    mkdir -p src/core/services/mini_app_fighting

    echo "BATTLE_API_URL=$BATTLE_API_URL" \
        > src/core/services/mini_app_fighting/.env
else
    echo "❌ API tunnel не найден"
fi

if [ -n "$FRONTEND_URL" ]; then
    echo "✅ Frontend:"
    echo "   $FRONTEND_URL"
else
    echo "❌ Frontend tunnel не найден"
fi

echo "--------------------------------------------------"
echo "Выход: ./dev.sh stop"