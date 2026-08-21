# 🔓 PDF Password Breaker

<p align="center">
  <b>Dictionary-based PDF password recovery tool</b><br>
  <i>Sözlük tabanlı PDF parola kurtarma aracı</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-38bdf8?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/GUI-PyQt6-22d3ee" alt="PyQt6">
  <img src="https://img.shields.io/badge/Multiprocessing-Parallel-10b981" alt="Parallel">
  <img src="https://img.shields.io/badge/Lang-EN%20%7C%20TR-f1f5f9" alt="Language">
</p>

---

## 🌐 Language / Dil

- [🇬🇧 English](#-english)
- [🇹🇷 Türkçe](#-türkçe)

---

## 🇬🇧 English

A modern, animated **PyQt6** desktop application that recovers a **forgotten PDF password** using a wordlist (dictionary attack). It runs the attempts across **multiple CPU cores in parallel** so it is fast without freezing or maxing out your machine.

> ⚠️ **Legal notice:** Use this tool **only** on PDF files you own or are explicitly authorized to test. Recovering passwords for files you do not have rights to is illegal.

### ✨ Features

- **Parallel cracking** — attempts are split across CPU cores using `multiprocessing`, giving several times the speed of a single-threaded tool.
- **Adjustable speed** — a slider lets you choose how many cores to use, balancing *speed ↔ quietness*. The physical core count is detected automatically and set as the recommended default.
- **Two engines** — uses `pikepdf` (fast, C-based) when available, and falls back to `pypdf` automatically.
- **Smart variations** — each word is tried as-is, lowercase, UPPERCASE and Capitalized.
- **Live log & progress bar** — shows the password currently being tried and overall progress.
- **Instant Stop** — cancels running worker processes immediately.
- **Bilingual UI (EN / TR)** — switch languages on the fly with the top-right buttons.
- **Modern animated UI** — glowing action button, rotating spinner, color-shifting title, gradient progress bar, and an animated *Developer* page.

### 📦 Requirements

- Python 3.8+
- [PyQt6](https://pypi.org/project/PyQt6/)
- [pikepdf](https://pypi.org/project/pikepdf/) *(recommended — much faster)* or [pypdf](https://pypi.org/project/pypdf/)
- [psutil](https://pypi.org/project/psutil/) *(optional — for physical core detection)*

### 🚀 Installation

```bash
pip install PyQt6 pikepdf psutil
```

### ▶️ Usage

```bash
python pdf_breaker_gui.py
```

1. Click **Select PDF File** and choose the locked PDF.
2. Click **Select Wordlist** and choose a `.txt` file (one password per line).
3. Set the **Speed** slider (cores) to your liking.
4. Press **START ATTACK**.
5. If a match is found, the password appears at the bottom in green.

### ⚡ Performance tips

- Install **pikepdf** for a dramatic speed boost over pypdf.
- For very large wordlists, push the core slider higher; for background use, keep it low.
- The speedup from multiprocessing is biggest on lists with thousands+ of words.

---

## 🇹🇷 Türkçe

Unutulmuş bir **PDF parolasını**, bir kelime listesi (sözlük saldırısı) kullanarak kurtaran modern ve animasyonlu bir **PyQt6** masaüstü uygulamasıdır. Denemeleri **birden fazla CPU çekirdeğinde paralel** çalıştırır; böylece makineyi kilitlemeden ve boğmadan hızlıdır.

> ⚠️ **Yasal uyarı:** Bu aracı **yalnızca** size ait olan veya test etme izniniz bulunan PDF dosyalarında kullanın. Hakkınız olmayan dosyaların parolasını kırmak yasa dışıdır.

### ✨ Özellikler

- **Paralel kırma** — denemeler `multiprocessing` ile CPU çekirdeklerine bölünür; tek çekirdekli bir araca göre kat kat hızlıdır.
- **Ayarlanabilir hız** — bir kaydırıcı ile kaç çekirdek kullanılacağını seçersin; *hız ↔ sessizlik* dengesini kurarsın. Fiziksel çekirdek sayısı otomatik algılanıp önerilen varsayılan olarak ayarlanır.
- **İki motor** — mümkünse `pikepdf` (hızlı, C tabanlı), yoksa otomatik olarak `pypdf` kullanılır.
- **Akıllı varyasyonlar** — her kelime; olduğu gibi, küçük harf, BÜYÜK HARF ve Baş Harfi Büyük olarak denenir.
- **Canlı log & ilerleme çubuğu** — o an denenen parolayı ve genel ilerlemeyi gösterir.
- **Anında Durdur** — çalışan işlemci süreçlerini hemen iptal eder.
- **İki dilli arayüz (EN / TR)** — sağ üstteki butonlarla dili anında değiştir.
- **Modern animasyonlu arayüz** — parlayan saldırı butonu, dönen spinner, renk değiştiren başlık, gradyanlı ilerleme çubuğu ve animasyonlu *Geliştirici* sayfası.

### 📦 Gereksinimler

- Python 3.8+
- [PyQt6](https://pypi.org/project/PyQt6/)
- [pikepdf](https://pypi.org/project/pikepdf/) *(önerilir — çok daha hızlı)* veya [pypdf](https://pypi.org/project/pypdf/)
- [psutil](https://pypi.org/project/psutil/) *(isteğe bağlı — fiziksel çekirdek tespiti için)*

### 🚀 Kurulum

```bash
pip install PyQt6 pikepdf psutil
```

### ▶️ Kullanım

```bash
python pdf_breaker_gui.py
```

1. **PDF Dosyası Seç**'e tıkla ve kilitli PDF'i seç.
2. **Sözlük Seç**'e tıkla ve bir `.txt` dosyası seç (her satırda bir parola).
3. **Hız** kaydırıcısını (çekirdek) istediğin gibi ayarla.
4. **SALDIRIYI BAŞLAT**'a bas.
5. Eşleşme bulunursa parola, altta yeşil renkte görünür.

### ⚡ Performans ipuçları

- pypdf'e göre büyük hız artışı için **pikepdf** kur.
- Çok büyük sözlüklerde çekirdek kaydırıcısını yukarı çek; arka planda kullanırken düşük tut.
- Multiprocessing'in kazancı, binlerce+ kelimelik listelerde en yüksektir.

---

## 👨‍💻 Developer / Geliştirici

**By espin0**

- 📧 Gmail: `kayhankafali@gmail.com`
- 🐙 GitHub: [github.com/espincom](https://github.com/espincom)

Uygulama içindeki **Geliştirici / Developer** sekmesinden de iletişime geçebilirsiniz. /
You can also reach out from the **Developer** tab inside the app.

---

<p align="center"><i>Made with ⚡ and PyQt6</i></p>
