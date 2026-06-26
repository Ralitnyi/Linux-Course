# Скрипт бекапу логів — Виконання завдання

## Опис

Bash-скрипт `backup.sh` для резервного копіювання каталогу логів у вигляді стисненого архіву `.tar.gz`. Підтримує захист від паралельного запуску та повну валідацію вхідних даних.

---

## Запуск

```bash
chmod +x backup.sh
./backup.sh /path/to/logs /path/to/backup
```

---

## Структура скрипта

### 1. Перевірка аргументів

Скрипт очікує рівно **2 аргументи** — шляхи до каталогу логів і каталогу бекапів.

```bash
if [ "$#" -ne 2 ]; then
    echo "Usage: ./backup.sh <log_dir> <backup_dir>"
    exit 1
fi
```

Після цього перевіряється, що **обидва шляхи є існуючими каталогами**:

```bash
if [ ! -d "$LOG_DIR" ] || [ ! -d "$BACKUP_DIR" ]; then
    echo "Usage: ./backup.sh <log_dir> <backup_dir>"
    exit 1
fi
```

| Ситуація | Повідомлення | Код виходу |
|---|---|---|
| Кількість аргументів ≠ 2 | `Usage: ./backup.sh <log_dir> <backup_dir>` | `1` |
| Каталог не існує | `Usage: ./backup.sh <log_dir> <backup_dir>` | `1` |

---

### 2. Захист від паралельного запуску

Використовується **lock-файл** `/tmp/backup.lock`. Якщо він існує — скрипт завершується:

```bash
if [ -f "$LOCK_FILE" ]; then
    echo "Backup already running"
    exit 1
fi
```

Lock-файл **автоматично видаляється** при будь-якому завершенні скрипта завдяки `trap`:

```bash
touch "$LOCK_FILE"
trap "rm -f '$LOCK_FILE'" EXIT
```

> `trap ... EXIT` гарантує прибирання lock-файлу навіть при помилці або Ctrl+C.

---

### 3. Створення архіву

Ім'я архіву формується з поточної дати і часу:

```
logs_backup_YYYY-MM-DD_HH-MM.tar.gz
```

```bash
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")
ARCHIVE_NAME="logs_backup_${TIMESTAMP}.tar.gz"
ARCHIVE_PATH="${BACKUP_DIR}/${ARCHIVE_NAME}"

tar -czf "$ARCHIVE_PATH" -C "$LOG_DIR" .
```

Прапор `-C "$LOG_DIR" .` архівує вміст каталогу логів **без зайвого префікса шляху**.

---

### 4. Перевірка результату

```bash
if [ $? -ne 0 ]; then
    echo "Backup failed"
    rm -f "$ARCHIVE_PATH"
    exit 2
fi

echo "Backup created: $(realpath "$ARCHIVE_PATH")"
```

| Ситуація | Повідомлення | Код виходу |
|---|---|---|
| Архівація провалилась | `Backup failed` | `2` |
| Архівація успішна | `Backup created: /full/path/to/archive` | `0` |

При невдачі частково створений архів **видаляється**, щоб не залишати пошкоджених файлів.

---

## Коди завершення

| Код | Значення |
|---|---|
| `0` | Успіх |
| `1` | Помилка аргументів або вже запущено |
| `2` | Помилка архівації |

---

## Best Practices, застосовані у скрипті

- **`set` не використовується навмисно** — замість нього явна перевірка `$?` після `tar`, що дає змогу вивести потрібне повідомлення та прибрати артефакти.
- **`trap EXIT`** — надійне прибирання lock-файлу за будь-якого завершення процесу.
- **Лапки навколо змінних** (`"$1"`, `"$LOG_DIR"`) — захист від шляхів з пробілами.
- **`realpath`** — виводить абсолютний шлях до архіву, зручний для логування.
- **Коментарі у коді** — кожна секція пояснена для швидкого розуміння.
- **Атомарне прибирання** — пошкоджений архів видаляється відразу при помилці.

---

## Приклад роботи

```
$ ./backup.sh /var/log/myapp /backups
Backup created: /backups/logs_backup_2026-06-25_14-30.tar.gz

$ ./backup.sh /var/log/myapp /backups   # одночасний запуск
Backup already running

$ ./backup.sh /nonexistent /backups
Usage: ./backup.sh <log_dir> <backup_dir>
```
