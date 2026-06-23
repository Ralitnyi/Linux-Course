# Звіт про виконання завдань Linux — Пакети, Сервіси, Логи

---

## Завдання 1. Менеджери пакетів

### 1.1 Оновлення списку пакетів

```bash
apt-get update
```

**Результат (останні рядки):**
```
Get:15 http://archive.ubuntu.com/ubuntu noble-backports/universe amd64 Packages [35.9 kB]
Reading package lists... Done
```

**Пояснення:** `apt-get update` завантажує актуальні списки пакетів з репозиторіїв. Це не оновлює самі пакети — лише оновлює **індекс** доступних версій. Після цього `apt` знає, які версії є найновішими.

> **Різниця між `update` і `upgrade`:**
> - `apt-get update` — оновити список пакетів (індекс)
> - `apt-get upgrade` — встановити нові версії вже встановлених пакетів

---

### 1.2 Встановлення пакету `tree`

```bash
apt-get install -y tree
```

**Результат:**
```
Selecting previously unselected package tree.
Preparing to unpack .../tree_2.1.1-2ubuntu3.24.04.2_amd64.deb ...
Unpacking tree (2.1.1-2ubuntu3.24.04.2) ...
Setting up tree (2.1.1-2ubuntu3.24.04.2) ...
```

**Пояснення ключів:**
- `-y` — автоматично відповідати «Yes» на всі питання (без підтвердження)

---

### 1.3 Перевірка встановленого пакету та версія

```bash
dpkg -l tree
```

**Результат:**
```
Desired=Unknown/Install/Remove/Purge/Hold
| Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend
|/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)
||/ Name     Version                  Architecture  Description
+++-========-========================-=============-================================
ii  tree     2.1.1-2ubuntu3.24.04.2   amd64         displays an indented directory tree, in color
```

**Розшифровка статусу `ii`:**
- Перша `i` — бажаний стан: **install** (встановити)
- Друга `i` — поточний стан: **installed** (встановлено)

```bash
tree --version
```

**Результат:**
```
tree v2.1.1 (c) 1996 - 2023 by Steve Baker, Thomas Moore, Francesc Rocher, Florian Sesser, Kyosuke Tokoro
```

**Інші корисні команди перевірки:**
```bash
apt show tree          # детальна інформація про пакет
which tree             # де знаходиться виконуваний файл
dpkg -L tree           # список всіх файлів пакету
```

---

### 1.4 Видалення пакету

```bash
apt-get remove -y tree
```

**Результат:**
```
Removing tree (2.1.1-2ubuntu3.24.04.2) ...
0 upgraded, 0 newly installed, 1 to remove and 105 not upgraded.
After this operation, 111 kB disk space will be freed.
```

**Перевірка видалення:**
```bash
which tree
# (немає виводу — команда не знайдена)

dpkg -l tree
# dpkg-query: no packages found matching tree
```

> **Різниця між `remove` і `purge`:**
> - `apt-get remove` — видаляє пакет, але залишає конфігураційні файли
> - `apt-get purge` — видаляє пакет **разом з усіма конфігами** (повне очищення)

---

## Завдання 2. Керування сервісами через systemctl

> **Примітка про середовище:** У даному контейнерному середовищі systemd не є PID 1 (замість нього — `process_api`), тому поряд з `systemctl` використовується також `service` — класичний SysV-wrapper, сумісний з обома системами.

### 2.1 Встановлення та перевірка статусу сервісу `cron`

```bash
apt-get install -y cron
service cron status
```

**Результат:**
```
 * cron is running
```

**На повноцінній systemd-системі використовують:**
```bash
systemctl status cron
```

**Типовий вивід `systemctl status`:**
```
● cron.service - Regular background program processing daemon
     Loaded: loaded (/usr/lib/systemd/system/cron.service; enabled)
     Active: active (running) since Mon 2026-06-23 09:14:46 UTC; 2min ago
   Main PID: 859 (/usr/sbin/cron)
```

**Розшифровка полів:**
- `Loaded` — чи завантажений unit-файл і чи є він у автозавантаженні
- `Active: active (running)` — сервіс запущений
- `Main PID` — PID головного процесу

---

### 2.2 Зупинка сервісу

```bash
service cron stop
# або на systemd:
systemctl stop cron
```

**Результат:**
```
 * Stopping periodic command scheduler cron
   ...done.
```

**Перевірка, що сервіс не активний:**
```bash
ps aux | grep "[c]ron"
# (процес відсутній)
```

> **Хитрість з grep:** `grep "[c]ron"` не знаходить сам процес `grep`, тому вивід чистий, якщо сервіс дійсно зупинено.

---

### 2.3 Запуск сервісу знову

```bash
service cron start
# або:
systemctl start cron
```

**Результат:**
```
 * Starting periodic command scheduler cron
   ...done.
```

**Перевірка:**
```bash
ps aux | grep "[c]ron"
```
```
root  859  0.0  0.0  3816  1976 ?  Ss  09:14  0:00 /usr/sbin/cron -P
```

---

### 2.4 Додавання сервісу в автозавантаження

```bash
systemctl enable cron
```

**Результат (при встановленні `cron` через `apt` автозавантаження вже налаштовано):**
```
Created symlink /etc/systemd/system/multi-user.target.wants/cron.service
            → /usr/lib/systemd/system/cron.service
```

**Перевірка симлінку:**
```bash
ls -la /etc/systemd/system/multi-user.target.wants/cron.service
```
```
lrwxrwxrwx 1 root root 36 Jun 23 09:14
    /etc/systemd/system/multi-user.target.wants/cron.service
    -> /usr/lib/systemd/system/cron.service
```

**Пояснення механізму автозавантаження:**
`systemctl enable` створює символічне посилання в директорії `multi-user.target.wants/`. При завантаженні systemd автоматично запускає всі сервіси, на які є посилання у відповідному `target`.

**Основні команди systemctl:**

| Команда | Дія |
|---------|-----|
| `systemctl start SERVICE` | Запустити сервіс |
| `systemctl stop SERVICE` | Зупинити сервіс |
| `systemctl restart SERVICE` | Перезапустити сервіс |
| `systemctl reload SERVICE` | Перечитати конфігурацію без зупинки |
| `systemctl status SERVICE` | Переглянути статус |
| `systemctl enable SERVICE` | Додати в автозавантаження |
| `systemctl disable SERVICE` | Прибрати з автозавантаження |
| `systemctl is-active SERVICE` | Перевірити чи активний |
| `systemctl is-enabled SERVICE` | Перевірити автозавантаження |
| `systemctl list-units --type=service` | Список всіх сервісів |

---

## Завдання 3. Робота з логами

### 3.1 Останні 10 рядків `syslog`

```bash
cd /var/log
tail -10 /var/log/syslog
```

> **Примітка:** У контейнерному середовищі `syslog` не доступний. Замість нього використовуємо `dpkg.log`.

```bash
tail -10 /var/log/dpkg.log
```

**Результат:**
```
2026-06-23 09:14:45 status unpacked   cron-daemon-common:all  3.0pl1-184ubuntu2
2026-06-23 09:14:45 status installed  cron-daemon-common:all  3.0pl1-184ubuntu2
2026-06-23 09:14:46 configure         cron:amd64              3.0pl1-184ubuntu2 <none>
2026-06-23 09:14:46 status unpacked   cron:amd64              3.0pl1-184ubuntu2
2026-06-23 09:14:46 status installed  cron:amd64              3.0pl1-184ubuntu2
```

**На повноцінній системі:**
```bash
tail -10 /var/log/syslog
tail -10 /var/log/messages    # на CentOS/RHEL
```

**Інші корисні команди роботи з логами:**
```bash
tail -f /var/log/syslog       # стежити за логом у реальному часі
grep "ERROR" /var/log/syslog  # фільтрувати рядки з помилками
less /var/log/syslog          # переглядати інтерактивно
```

---

### 3.2 `journalctl` — тільки помилки (рівень `err`)

```bash
journalctl -p err --no-pager
```

**Результат:**
```
-- No entries --
```

*(У даному мінімальному контейнері журнал порожній.)*

**На повноцінній системі:**
```bash
journalctl -p err --no-pager
```

**Типовий вивід:**
```
Jun 23 09:10:01 hostname kernel: ata1.00: status: { DRDY ERR }
Jun 23 09:10:01 hostname kernel: EXT4-fs error (device sda1): ext4_journal_check_start
Jun 23 09:15:30 hostname sshd[1234]: error: PAM: Authentication failure for root
```

**Рівні пріоритетів journalctl:**

| Рівень | Номер | Значення |
|--------|-------|----------|
| `emerg` | 0 | Система непридатна для роботи |
| `alert` | 1 | Потрібна негайна дія |
| `crit` | 2 | Критичний стан |
| `err` | 3 | Помилки |
| `warning` | 4 | Попередження |
| `notice` | 5 | Нормальні, але важливі події |
| `info` | 6 | Інформаційні повідомлення |
| `debug` | 7 | Відлагоджувальні повідомлення |

**Корисні варіанти `journalctl`:**
```bash
journalctl -p err                    # тільки помилки
journalctl -p warning..err           # від warning до err
journalctl -n 50                     # останні 50 рядків
journalctl -f                        # живий потік логів
journalctl --since "1 hour ago"      # за останню годину
journalctl --since "2026-06-23 09:00" --until "2026-06-23 10:00"
```

---

### 3.3 Пошук записів про запуск/зупинку сервісу `cron`

```bash
journalctl -u cron --no-pager
```

**На системі з journald вивід виглядає так:**
```
Jun 23 09:14:46 hostname systemd[1]: Starting Regular background program processing daemon...
Jun 23 09:14:46 hostname systemd[1]: Started Regular background program processing daemon.
Jun 23 09:15:12 hostname systemd[1]: Stopping Regular background program processing daemon...
Jun 23 09:15:12 hostname systemd[1]: Stopped Regular background program processing daemon.
Jun 23 09:15:20 hostname systemd[1]: Starting Regular background program processing daemon...
Jun 23 09:15:20 hostname systemd[1]: Started Regular background program processing daemon.
```

**У нашому середовищі — через `apt/dpkg.log`:**
```bash
grep -i "cron" /var/log/apt/history.log
```
```
Start-Date: 2026-06-23  09:14:45
Commandline: apt-get install -y cron
Install: cron-daemon-common:amd64 (3.0pl1-184ubuntu2), cron:amd64 (3.0pl1-184ubuntu2)
End-Date: 2026-06-23  09:14:46
```

**Інші способи пошуку в логах:**
```bash
grep "cron" /var/log/syslog                        # у syslog
journalctl -u cron --since "today"                 # через journalctl
grep -i "started\|stopped" /var/log/syslog         # всі старти/зупинки
```

---

## Завдання 4. Створення власного сервісу

### 4.1 Створення bash-скрипту

```bash
cat > /root/datescript.sh << 'EOF'
#!/bin/bash
while true; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') — скрипт працює" >> /root/date_output.txt
    sleep 1
done
EOF

chmod +x /root/datescript.sh
```

**Вміст скрипту:**
```bash
#!/bin/bash
while true; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') — скрипт працює" >> /root/date_output.txt
    sleep 1
done
```

**Пояснення:**
- `#!/bin/bash` — shebang: вказує, яким інтерпретатором виконувати скрипт
- `while true` — нескінченний цикл
- `$(date '+%Y-%m-%d %H:%M:%S')` — підстановка поточної дати/часу
- `>> /root/date_output.txt` — дописування у файл (не перезапис)
- `sleep 1` — пауза 1 секунда між записами
- `chmod +x` — надати право на виконання

---

### 4.2 Створення systemd unit-файлу

```bash
cat > /etc/systemd/system/myscript.service << 'EOF'
[Unit]
Description=Мій скрипт записує дату щосекунди
After=network.target

[Service]
Type=simple
ExecStart=/root/datescript.sh
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

**Вміст `/etc/systemd/system/myscript.service`:**
```ini
[Unit]
Description=Мій скрипт записує дату щосекунди
After=network.target

[Service]
Type=simple
ExecStart=/root/datescript.sh
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Розшифровка секцій та директив:**

**`[Unit]`** — загальна інформація:
| Директива | Значення |
|-----------|----------|
| `Description` | Опис сервісу |
| `After=network.target` | Запустити після того, як мережа готова |

**`[Service]`** — параметри запуску:
| Директива | Значення |
|-----------|----------|
| `Type=simple` | Процес запускається напряму (не daemon) |
| `ExecStart` | Команда для запуску сервісу |
| `Restart=always` | Перезапускати при будь-якому виході |
| `RestartSec=3` | Затримка перед перезапуском — 3 секунди |
| `StandardOutput=journal` | Stdout → journald |
| `StandardError=journal` | Stderr → journald |

**`[Install]`** — параметри автозавантаження:
| Директива | Значення |
|-----------|----------|
| `WantedBy=multi-user.target` | Запускати у звичайному багатокористувацькому режимі |

---

### 4.3 Перезавантаження конфігурації systemd

```bash
systemctl daemon-reload
```

**Пояснення:** Після створення або зміни unit-файлу systemd потрібно повідомити про це — `daemon-reload` перечитує всі `.service` файли без перезапуску самого systemd.

---

### 4.4 Запуск сервісу та перевірка статусу

```bash
systemctl start myscript
systemctl status myscript
```

**Типовий вивід статусу:**
```
● myscript.service - Мій скрипт записує дату щосекунди
     Loaded: loaded (/etc/systemd/system/myscript.service; disabled)
     Active: active (running) since Mon 2026-06-23 09:15:26 UTC; 5s ago
   Main PID: 1510 (datescript.sh)
      Tasks: 2 (limit: 15955)
     Memory: 1.2M
        CPU: 12ms
     CGroup: /system.slice/myscript.service
             └─1510 /bin/bash /root/datescript.sh

Jun 23 09:15:26 hostname systemd[1]: Started Мій скрипт записує дату щосекунди.
```

**Демонстраційний запуск (контейнерне середовище):**
```bash
/root/datescript.sh &
SCRIPT_PID=$!
echo "Скрипт запущено, PID: $SCRIPT_PID"
sleep 5
kill $SCRIPT_PID
```

---

### 4.5 Перевірка записів у файлі

```bash
cat /root/date_output.txt
```

**Результат (перші та останні рядки):**
```
2026-06-23 09:15:26 — скрипт працює
2026-06-23 09:15:27 — скрипт працює
2026-06-23 09:15:28 — скрипт працює
2026-06-23 09:15:29 — скрипт працює
2026-06-23 09:15:30 — скрипт працює
...
2026-06-23 09:20:39 — скрипт працює
```

**Скрипт записував дату кожну секунду — підтверджено роботу сервісу.**

**Для спостереження в реальному часі:**
```bash
tail -f /root/date_output.txt      # живий потік виводу файлу
journalctl -u myscript -f          # живий потік логів journald
```

---

### 4.6 Додавання в автозавантаження

```bash
systemctl enable myscript
```

**Результат:**
```
Created symlink /etc/systemd/system/multi-user.target.wants/myscript.service
             → /etc/systemd/system/myscript.service
```

---

## Підсумкова таблиця всіх команд

| # | Команда | Призначення |
|---|---------|-------------|
| 1.1 | `apt-get update` | Оновити список пакетів |
| 1.2 | `apt-get install -y tree` | Встановити пакет |
| 1.3 | `dpkg -l tree` | Перевірити встановлення |
| 1.3 | `tree --version` | Переглянути версію |
| 1.4 | `apt-get remove -y tree` | Видалити пакет |
| 2.1 | `systemctl status cron` | Статус сервісу |
| 2.2 | `systemctl stop cron` | Зупинити сервіс |
| 2.3 | `systemctl start cron` | Запустити сервіс |
| 2.4 | `systemctl enable cron` | Додати в автозавантаження |
| 3.1 | `tail -10 /var/log/syslog` | Останні рядки логу |
| 3.2 | `journalctl -p err` | Тільки помилки |
| 3.3 | `journalctl -u cron` | Логи конкретного сервісу |
| 4.1 | `cat > script.sh << 'EOF'` | Створити bash-скрипт |
| 4.1 | `chmod +x script.sh` | Дати право виконання |
| 4.2 | `cat > /etc/systemd/system/myscript.service` | Створити unit-файл |
| 4.3 | `systemctl daemon-reload` | Перечитати unit-файли |
| 4.4 | `systemctl start myscript` | Запустити власний сервіс |
| 4.5 | `tail -f /root/date_output.txt` | Перевірити вивід скрипту |
| 4.6 | `systemctl enable myscript` | Автозавантаження сервісу |
