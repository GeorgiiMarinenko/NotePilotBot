#!/bin/bash

CONTAINER_NAME="telegram-bot-container"
IMAGE_NAME="telegram-bot"
LOG_DIR="logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/deploy_$(date +'%Y-%m-%d_%H-%M-%S').log"

check_error() {
  if [ $? -ne 0 ]; then
    echo "Ошибка на этапе: $1" | tee -a "$LOG_FILE"
    exit 1
  fi
}

echo "Остановка и удаление старого контейнера..." | tee -a "$LOG_FILE"
docker stop $CONTAINER_NAME >> "$LOG_FILE" 2>&1
docker rm $CONTAINER_NAME >> "$LOG_FILE" 2>&1
check_error "Удаление старого контейнера"

echo "Пересборка образа..." | tee -a "$LOG_FILE"
docker build -t $IMAGE_NAME . >> "$LOG_FILE" 2>&1
check_error "Сборка образа"

echo "Запуск нового контейнера..." | tee -a "$LOG_FILE"
docker run -d \
  --name $CONTAINER_NAME \
  --restart=always \
  --network=host \
  --memory="512m" \
  --cpus="1" \
  $IMAGE_NAME >> "$LOG_FILE" 2>&1

check_error "Запуск контейнера"

echo "Проверка состояния контейнера..." | tee -a "$LOG_FILE"
docker ps -f "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\nПоследние логи контейнера:" | tee -a "$LOG_FILE"
docker logs --tail=10 $CONTAINER_NAME | tee -a "$LOG_FILE"

echo -e "\n✅ Обновление завершено успешно!" | tee -a "$LOG_FILE"
