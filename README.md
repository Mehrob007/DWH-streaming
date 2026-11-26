# Streaming DWH: Real-time Analytics with Kafka, Spark, ClickHouse, RustFS, and Superset

Полноценное аналитическое DWH-окружение для потоковой обработки данных в реальном времени.

В отличие от пакетной реализации в `test-DWH` (где Airflow запускал Spark раз в сутки для перезаливки файлов из S3), данная архитектура построена на **непрерывном потоке событий (Streaming)**:
1. Заказы непрерывно поступают в стриминговый брокер **Redpanda (Kafka API)**.
2. Сервис **Apache Spark Structured Streaming** читает поток, на лету выполняет очистку, валидацию и нормализацию данных.
3. Микробатчами (каждые 2 секунды) чистые данные записываются в колоночную СУБД **ClickHouse**.
4. Данные мгновенно отображаются на аналитических дашбордах в **Apache Superset**.
5. Для холодного/сырого слоя и хранения файлов используется S3-совместимое хранилище **RustFS**.

---

## 🏛 Архитектура сервисов

```mermaid
flowchart LR
    A["Генератор заказов\n(scripts/stream_producer.py)"] -->|events| B["Redpanda\n(Kafka: 9092)"]
    A -.->|raw backup| S3["RustFS S3\n(API: 9002, UI: 9001)"]
    B -->|spark.readStream| C["Spark Structured Streaming\n(streaming_orders.py)"]
    C -->|writeStream (micro-batch)| D["ClickHouse DWH\n(sales.orders_clean: 8123)"]
    D --> E["Apache Superset\n(Dashboards: 8088)"]
```

| Сервис | Порты на хосте | Назначение |
| :--- | :--- | :--- |
| **Redpanda** | `9092` | Брокер сообщений Kafka API (топик `orders_stream`) |
| **Spark** | - | Потоковый движок Apache Spark Structured Streaming |
| **ClickHouse** | `8123` (HTTP), `9000` (Native) | Колоночный DWH, база данных `sales`, таблица `orders_clean` |
| **RustFS** | `9002` (S3 API), `9001` (Web UI) | S3-совместимое объектное хранилище (бакет `bronze`) |
| **Superset** | `8088` | BI-платформа дашбордов и визуализации |

---

## 🚀 Быстрый старт

### 1. Запуск всех сервисов

```bash
docker compose up -d --build
```

Compose запустит:
* RustFS и Redpanda;
* ClickHouse с автоматической инициализацией схемы `sales` из `initdb/01_init_sales.sql`;
* Spark Structured Streaming, который подключится к Redpanda и ClickHouse;
* Superset, готовый к работе.

### 2. Запуск непрерывного генератора заказов

Создайте топик `orders_stream` (если ещё не создан) и запустите отправку событий:

```bash
# 1. Создать топик
docker exec dwh-redpanda rpk topic create orders_stream 2>/dev/null || true

# 2. Запустить генерацию потока с интервалом 0.5 секунды
python3 scripts/stream_producer.py --interval 0.5 | docker exec -i dwh-redpanda rpk topic produce orders_stream
```

### 3. Проверка стриминга (End-to-End)

Для быстрой автоматической проверки используйте готовый скрипт:

```bash
./scripts/verify_streaming.sh
```

Скрипт отправит тестовые события, дождётся их обработки Spark и выведет свежие строки и агрегаты из ClickHouse.

---

## 📊 Доступ к веб-интерфейсам

### 1. Apache Superset
* **URL:** [http://localhost:8088](http://localhost:8088)
* **Логин:** `admin`
* **Пароль:** `admin123`
* **Подключение к ClickHouse в Superset:**
  * Перейдите в **Settings** → **Database Connections** → **+ Database**
  * Выберите **ClickHouse Connect**
  * SQL Alchemy URI:
    ```text
    clickhousedb://admin:admin123@clickhouse:8123/sales
    ```

### 2. RustFS Web Console
* **URL:** [http://localhost:9001](http://localhost:9001)
* **Access Key:** `rustfsadmin`
* **Secret Key:** `rustfsadmin123`
* **S3 API Endpoint:** `http://localhost:9002`

---

## 🔍 SQL-запросы в ClickHouse

Подключение через `curl`:

```bash
# Количество заказов в реальном времени:
curl -u admin:admin123 "http://localhost:8123/" \
  --data-binary "SELECT count() AS total_orders FROM sales.orders_clean"

# Сводка по городам (агрегатная витрина):
curl -u admin:admin123 "http://localhost:8123/" \
  --data-binary "SELECT * FROM sales.v_city_summary FORMAT PrettyCompact"
```

---

## 🛑 Остановка окружения

```bash
# Остановка сервисов
docker compose down

# Остановка с удалением томов данных
docker compose down -v
```
