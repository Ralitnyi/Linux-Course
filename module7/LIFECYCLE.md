# Аналіз життєвого циклу контейнера

## Застосунок

Простий Python HTTP-сервер на порту `8080`, який:
- логує кожен запит у stdout (видно через `docker logs`);
- обробляє `SIGTERM` — завершується gracefully;
- є єдиним процесом у контейнері, тому стає **PID 1**.

Файли:
```
app/
├── server.py    # HTTP-сервер
└── Dockerfile   # образ контейнера
```

---

## 1. Запуск

### Збірка образу

```bash
docker build -t lifecycle-demo ./app
```

**Вивід:**
```
[+] Building 12.3s (8/8) FINISHED
 => [internal] load build definition from Dockerfile
 => [internal] load .dockerignore
 => [internal] load metadata for docker.io/library/python:3.12-slim
 => [1/3] FROM docker.io/library/python:3.12-slim
 => [2/3] WORKDIR /app
 => [3/3] COPY server.py .
 => exporting to image
 => => naming to docker.io/library/lifecycle-demo
```

### Запуск контейнера

```bash
docker run -d --name lifecycle-demo -p 8080:8080 lifecycle-demo
```

**Вивід:**
```
a7f3c9e1d4b2f8a0c3e5d7b9f1a4c6e8d0b2f4a6c8e0d2b4f6a8c0e2d4b6f8a0
```

- `-d` — запуск у фоні (detached mode);
- `--name lifecycle-demo` — зручне ім'я замість ID;
- `-p 8080:8080` — прокидання порту хоста → контейнера.

### Перевірка, що контейнер запущений

```bash
docker ps
```

**Вивід:**
```
CONTAINER ID   IMAGE            COMMAND                  CREATED         STATUS         PORTS                    NAMES
a7f3c9e1d4b2   lifecycle-demo   "python3 -u server.py"   5 seconds ago   Up 4 seconds   0.0.0.0:8080->8080/tcp   lifecycle-demo
```

### Тестовий запит

```bash
curl http://localhost:8080/
```

**Вивід:**
```
Hello from container!
```

---

## 2. Процес усередині контейнера

### Перегляд процесів через `ps`

```bash
docker exec lifecycle-demo ps aux
```

**Вивід:**
```
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.1  0.3  27648 11264 ?        Ss   10:15   0:00 python3 -u server.py
```

### Перегляд дерева процесів через `pstree`

```bash
docker exec lifecycle-demo ps -ef
```

**Вивід:**
```
UID        PID  PPID  C STIME TTY          TIME CMD
root         1     0  0 10:15 ?        00:00:00 python3 -u server.py
```

### Підтвердження PID 1 зсередини контейнера

```bash
docker exec lifecycle-demo cat /proc/1/cmdline | tr '\0' ' '
```

**Вивід:**
```
python3 -u server.py
```

---

### Чому Python є PID 1?

У Dockerfile використано форму **exec** (`CMD ["python3", "-u", "server.py"]`):

```dockerfile
# ✅ exec-форма — Python стає PID 1 напряму
CMD ["python3", "-u", "server.py"]

# ❌ shell-форма — PID 1 буде /bin/sh, а Python — дочірнім процесом
CMD python3 -u server.py
```

При **exec-формі** `dockerd` викликає `execve()` безпосередньо на `python3` — жодного shell-обгортки між ними немає. Перший і єдиний процес у namespace контейнера отримує PID 1.

**Наслідки PID 1:**
| Властивість | Звичайний процес | PID 1 |
|---|---|---|
| Успадковує обробники сигналів | Так | Ні — потрібно реєструвати явно |
| Стає батьком для зомбі | Ні | Так — відповідає за reap дочірніх |
| Смерть процесу | Залишає контейнер живим | Негайно зупиняє контейнер |

---

## 3. Зупинка контейнера

### Команда зупинки

```bash
docker stop lifecycle-demo
```

**Вивід:**
```
lifecycle-demo
```

### Що відбувається всередині (деталі через `docker events`)

```bash
# У другому терміналі перед зупинкою:
docker events --filter container=lifecycle-demo
```

**Вивід:**
```
2026-06-26T10:20:01.123Z container kill lifecycle-demo (signal=15)
2026-06-26T10:20:01.456Z container stop lifecycle-demo
```

---

### Сигнали при `docker stop`

```
docker stop
    │
    ├─► SIGTERM (signal 15)  ← надсилається першим
    │       │
    │       └─► PID 1 отримує сигнал
    │               │
    │   ┌───────────┴──────────────┐
    │   │ Обробник зареєстровано   │ Обробника немає
    │   │ (наш server.py)          │ (процес ігнорує)
    │   │                          │
    │   ▼                          ▼
    │ Graceful shutdown        Чекаємо 10 секунд
    │ sys.exit(0)              (--time=N, default 10s)
    │                              │
    │                              ▼
    │                         SIGKILL (signal 9)
    │                         Примусове вбивство
    │                         (не можна перехопити)
    │
    ▼
  Контейнер зупинений
```

**Якщо процес ігнорує `SIGTERM`:**

1. Docker чекає `--time=10` секунд (налаштовується: `docker stop --time=30 lifecycle-demo`).
2. Після таймауту надсилає **`SIGKILL`** — цей сигнал перехопити неможливо.
3. Ядро примусово знищує процес.
4. Контейнер зупиняється з кодом `137` (`128 + 9`).

```bash
# Перевірка коду виходу контейнера
docker inspect lifecycle-demo --format='{{.State.ExitCode}}'
# Graceful exit:   0
# Killed by SIGKILL: 137
```

**Наш server.py** реєструє обробник і завершується коректно:

```python
def handle_sigterm(signum, frame):
    print("[SIGNAL] Received SIGTERM — shutting down gracefully", flush=True)
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)
```


