import sys
import os
import math
import multiprocessing as mp
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTextEdit, QFrame, QProgressBar,
    QGraphicsDropShadowEffect, QSlider, QTabWidget
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QThread, QObject, pyqtSlot, QPropertyAnimation,
    QEasingCurve, pyqtProperty, QTimer, QRectF, QPointF, QUrl
)
from PyQt6.QtGui import (
    QColor, QPainter, QPen, QFont, QBrush, QLinearGradient, QRadialGradient,
    QPainterPath, QDesktopServices
)

# ---------------------------------------------------------------------------
# Renk paleti
# ---------------------------------------------------------------------------
C_BG = "#0b1120"
C_ACCENT = "#38bdf8"
C_ACCENT_2 = "#22d3ee"
C_MUTED = "#64748b"
C_TEXT = "#f1f5f9"

# ---------------------------------------------------------------------------
# i18n  (English / Turkce)
# ---------------------------------------------------------------------------
LANG = "tr"

STRINGS = {
    "app_title":        ("PDF Password Breaker", "PDF Şifre Kırıcı"),
    "header":           ("PDF Password Breaker", "PDF Şifre Kırıcı"),
    "subtitle":         ("Dictionary-based PDF password recovery tool",
                         "Sözlük tabanlı PDF parola kurtarma aracı"),

    "tab_main":         ("Breaker", "Kırıcı"),
    "tab_about":        ("Developer", "Geliştirici"),

    "lang_tip_en":      ("Switch to English", "İngilizceye geç"),
    "lang_tip_tr":      ("Türkçeye geç", "Türkçeye geç"),

    "pdf_none":         ("PDF: Not selected", "PDF: Seçilmedi"),
    "pdf_sel":          ("PDF: %s", "PDF: %s"),
    "word_none":        ("Wordlist: Not selected", "Sözlük: Seçilmedi"),
    "word_sel":         ("Wordlist: %s", "Sözlük: %s"),
    "btn_pick_pdf":     ("Select PDF File", "PDF Dosyası Seç"),
    "btn_pick_word":    ("Select Wordlist", "Sözlük Seç"),

    "cpu_info":         ("Processor detected: %d physical / %d logical cores",
                         "İşlemci algılandı: %d fiziksel / %d mantıksal çekirdek"),
    "speed":            ("Speed: %d / %d cores%s", "Hız: %d / %d çekirdek%s"),
    "sp_max":           ("  (maximum - machine may strain)",
                         "  (maksimum - makine zorlanabilir)"),
    "sp_hyper":         ("  (high - hyperthreading)", "  (yüksek - hyperthreading)"),
    "sp_reco":          ("  (recommended - most efficient)",
                         "  (önerilen - en verimli)"),
    "sp_quiet":         ("  (quietest - single core)", "  (en sessiz - tek çekirdek)"),
    "sp_balanced":      ("  (balanced)", "  (dengeli)"),

    "btn_attack":       ("START ATTACK", "SALDIRIYI BAŞLAT"),
    "btn_stop":         ("STOP", "DURDUR"),

    "st_ready":         ("Status: Ready", "Durum: Hazır"),
    "st_running":       ("Attack in progress...", "Saldırı sürüyor..."),
    "st_stopping":      ("Stopping attack...", "Saldırı durduruluyor..."),
    "st_stopped":       ("Stopped.", "Durduruldu."),
    "st_found":         ("PASSWORD FOUND: %s", "ŞİFRE BULUNDU: %s"),
    "st_notfound":      ("Done: Password not found.", "Bitti: Şifre bulunamadı."),
    "st_error":         ("Error: %s", "Hata: %s"),
    "err_no_files":     ("Error: No files selected!", "Hata: Dosyalar seçilmedi!"),

    "sys_engine":       ("[System] %s | %d parallel processes | %d candidates",
                         "[Sistem] %s | %d paralel işlemci | %d aday"),
    "eng_pike":         ("pikepdf (FAST)", "pikepdf (HIZLI)"),
    "eng_pypdf":        ("pypdf (NORMAL)", "pypdf (NORMAL)"),
    "log_trying":       ("Trying: %s   [%d/%d]", "Deneniyor: %s   [%d/%d]"),

    "err_no_engine":    ("pikepdf or pypdf is not installed! (pip install pikepdf)",
                         "pikepdf veya pypdf kurulu değil! (pip install pikepdf)"),
    "err_no_wordlist":  ("Wordlist file not found!", "Sözlük dosyası bulunamadı!"),
    "err_empty":        ("Wordlist is empty!", "Sözlük boş!"),
    "err_critical":     ("Critical Error: %s", "Kritik Hata: %s"),

    "dlg_pick_pdf":     ("Select PDF", "PDF Seç"),
    "dlg_pick_word":    ("Select Wordlist", "Sözlük Seç"),

    # about
    "ab_message":       ("For bugs and feedback, please get in touch by mail.",
                         "Hata ve geri bildirimleriniz için lütfen mail yoluyla "
                         "iletişime geçin."),
    "ab_by":            ("By espin0", "By espin0"),
    "ab_mail_label":    ("Gmail", "Gmail"),
    "ab_github_label":  ("GitHub", "GitHub"),
    "ab_mail_hint":     ("Click to compose an e-mail", "Tıklayınca mail penceresi açılır"),
    "ab_github_hint":   ("Click to open in your browser", "Tıklayınca tarayıcıda açılır"),
    "ab_copied":        ("Copied to clipboard", "Panoya kopyalandı"),
}


def tr(key, *args):
    pair = STRINGS.get(key)
    if pair is None:
        return key
    text = pair[1] if LANG == "tr" else pair[0]
    if args:
        try:
            return text % args
        except (TypeError, ValueError):
            return text
    return text


def set_language(code):
    global LANG
    LANG = "tr" if code == "tr" else "en"


def current_language():
    return LANG


# ---------------------------------------------------------------------------
# Kutuphane kontrolu
# ---------------------------------------------------------------------------
PIKE_AVAILABLE = False
PYPDF_AVAILABLE = False
PdfReader = None

try:
    import pikepdf
    PIKE_AVAILABLE = True
except ImportError:
    pass

try:
    from pypdf import PdfReader as _PdfReader
    PdfReader = _PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    pass

ENGINE_OK = PIKE_AVAILABLE or PYPDF_AVAILABLE


def detect_cpu():
    """(logical, physical) cekirdek sayisi. psutil varsa fizikseli de ogrenir."""
    logical = os.cpu_count() or 2
    physical = None
    try:
        import psutil
        physical = psutil.cpu_count(logical=False)
    except Exception:
        physical = None
    if not physical:
        physical = logical
    return logical, physical


def _expand(word):
    """Yaygin varyasyonlari uret."""
    return list(dict.fromkeys([word, word.lower(), word.upper(), word.capitalize()]))


def _crack_chunk(args):
    """Ayri process'te calisir: (bulunan_veya_None, denenen_adet, ornek_sifre) doner."""
    pdf_path, candidates, use_pike = args
    found = None
    if use_pike:
        import pikepdf
        for pw in candidates:
            try:
                with pikepdf.open(pdf_path, password=pw):
                    found = pw
                    break
            except Exception:
                continue
    else:
        from pypdf import PdfReader as _R
        reader = _R(pdf_path)
        for pw in candidates:
            try:
                if reader.decrypt(pw) > 0:
                    found = pw
                    break
            except Exception:
                continue
    sample = candidates[-1] if candidates else ""
    return (found, len(candidates), sample)


# ---------------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------------
class CrackerWorker(QObject):
    finished = pyqtSignal(str)
    failed = pyqtSignal()
    stopped = pyqtSignal()
    progress = pyqtSignal(str)
    tick = pyqtSignal(int, int)
    error = pyqtSignal(str)

    def __init__(self, pdf_path, wordlist_path, workers=None):
        super().__init__()
        self.pdf_path = pdf_path
        self.wordlist_path = wordlist_path
        self.workers = workers
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        try:
            if not ENGINE_OK:
                self.error.emit(tr("err_no_engine"))
                return

            if not os.path.exists(self.wordlist_path):
                self.error.emit(tr("err_no_wordlist"))
                return

            with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                words = [line.strip() for line in f if line.strip()]

            if not words:
                self.error.emit(tr("err_empty"))
                return

            candidates = list(dict.fromkeys(c for w in words for c in _expand(w)))
            total = len(candidates)

            cores = os.cpu_count() or 2
            if self.workers:
                workers = max(1, min(self.workers, cores))
            else:
                workers = max(1, cores - 1)

            engine = tr("eng_pike") if PIKE_AVAILABLE else tr("eng_pypdf")
            self.progress.emit(tr("sys_engine", engine, workers, total))

            chunk_size = max(10, min(200, (total // (workers * 8)) or 1))
            tasks = [(self.pdf_path, candidates[i:i + chunk_size], PIKE_AVAILABLE)
                     for i in range(0, total, chunk_size)]

            done = 0
            pool = mp.Pool(processes=workers)
            try:
                for found, n, sample in pool.imap_unordered(_crack_chunk, tasks):
                    if not self._is_running:
                        pool.terminate()
                        pool.join()
                        self.stopped.emit()
                        return

                    done += n
                    self.tick.emit(min(done, total), total)
                    self.progress.emit(tr("log_trying", sample, min(done, total), total))

                    if found is not None:
                        pool.terminate()
                        pool.join()
                        self.finished.emit(found)
                        return

                pool.close()
                pool.join()
            finally:
                try:
                    pool.terminate()
                except Exception:
                    pass

            self.failed.emit()

        except Exception as e:
            try:
                self.error.emit(tr("err_critical", str(e)))
            except RuntimeError:
                pass


# ---------------------------------------------------------------------------
# Spinner
# ---------------------------------------------------------------------------
class Spinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(28, 28)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._active = False

    def start(self):
        self._active = True
        self._timer.start(30)
        self.update()

    def stop(self):
        self._active = False
        self._timer.stop()
        self.update()

    def _rotate(self):
        self._angle = (self._angle + 12) % 360
        self.update()

    def paintEvent(self, event):
        if not self._active:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(4, 4, 20, 20)
        for i in range(12):
            alpha = int(255 * (i + 1) / 12)
            pen = QPen(QColor(56, 189, 248, alpha), 3)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.save()
            p.translate(rect.center())
            p.rotate(self._angle + i * 30)
            p.drawLine(0, 6, 0, 9)
            p.restore()


# ---------------------------------------------------------------------------
# Glow buton
# ---------------------------------------------------------------------------
class GlowButton(QPushButton):
    def __init__(self, text, glow_color=QColor(239, 68, 68), parent=None):
        super().__init__(text, parent)
        self._glow = QGraphicsDropShadowEffect(self)
        self._glow.setColor(glow_color)
        self._glow.setOffset(0, 0)
        self._glow.setBlurRadius(15)
        self.setGraphicsEffect(self._glow)

        self._anim = QPropertyAnimation(self, b"glowRadius")
        self._anim.setStartValue(10)
        self._anim.setEndValue(40)
        self._anim.setDuration(900)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._anim.setLoopCount(-1)

    def getGlowRadius(self):
        return self._glow.blurRadius()

    def setGlowRadius(self, r):
        self._glow.setBlurRadius(r)

    glowRadius = pyqtProperty(float, getGlowRadius, setGlowRadius)

    def pulse(self, on=True):
        if on:
            self._anim.start()
        else:
            self._anim.stop()
            self._glow.setBlurRadius(15)


# ---------------------------------------------------------------------------
# ContactCard (about sayfasi icin)
# ---------------------------------------------------------------------------
class ContactCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, glyph, title, value, accent, parent=None):
        super().__init__(parent)
        self.glyph, self.value, self.accent = glyph, value, QColor(accent)
        self.title_text = title
        self.hint_text = ""
        self._glow = 0.0
        self.setFixedHeight(76)
        self.setMinimumWidth(320)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent; border: none;")
        self._anim = QPropertyAnimation(self, b"glow", self)
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def getGlow(self):
        return self._glow

    def setGlow(self, v):
        self._glow = float(v)
        self.update()

    glow = pyqtProperty(float, fget=getGlow, fset=setGlow)

    def set_texts(self, title, hint):
        self.title_text, self.hint_text = title, hint
        self.update()

    def enterEvent(self, e):
        self._anim.stop(); self._anim.setEndValue(1.0); self._anim.start()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._anim.stop(); self._anim.setEndValue(0.0); self._anim.start()
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(e)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        g = self._glow
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)

        bg = QLinearGradient(r.topLeft(), r.bottomRight())
        bg.setColorAt(0.0, QColor(32, 38, 52).lighter(100 + int(12 * g)))
        bg.setColorAt(1.0, QColor(24, 29, 40).lighter(100 + int(10 * g)))
        path = QPainterPath()
        path.addRoundedRect(r, 14, 14)
        p.fillPath(path, QBrush(bg))

        pen = QPen(QColor(self.accent.red(), self.accent.green(), self.accent.blue(),
                          int(60 + 165 * g)), 1 + g)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(r, 14, 14)

        ic = QRectF(r.left() + 14, r.center().y() - 20, 40, 40)
        icg = QLinearGradient(ic.topLeft(), ic.bottomRight())
        icg.setColorAt(0.0, self.accent.lighter(115))
        icg.setColorAt(1.0, self.accent.darker(130))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(icg))
        p.drawEllipse(ic)
        f = QFont()
        f.setPointSize(11 if len(self.glyph) > 1 else 14)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QPen(QColor("white")))
        p.drawText(ic, Qt.AlignmentFlag.AlignCenter, self.glyph)

        tx = ic.right() + 16
        f2 = QFont(); f2.setPointSize(8); f2.setBold(True)
        p.setFont(f2)
        p.setPen(QPen(QColor(C_MUTED)))
        p.drawText(QRectF(tx, r.top() + 14, r.width() - tx, 14),
                   Qt.AlignmentFlag.AlignVCenter, self.title_text.upper())
        f3 = QFont(); f3.setPointSize(11); f3.setBold(True)
        p.setFont(f3)
        p.setPen(QPen(QColor(C_TEXT)))
        p.drawText(QRectF(tx, r.top() + 29, r.width() - tx - 12, 20),
                   Qt.AlignmentFlag.AlignVCenter, self.value)
        if self.hint_text:
            f4 = QFont(); f4.setPointSize(8)
            p.setFont(f4)
            p.setPen(QPen(QColor(139, 147, 167, int(120 + 135 * g))))
            p.drawText(QRectF(tx, r.top() + 48, r.width() - tx - 12, 16),
                       Qt.AlignmentFlag.AlignVCenter, self.hint_text)

        p.setPen(QPen(QColor(255, 255, 255, int(40 + 150 * g)), 2))
        ax = r.right() - 22 + 4 * g
        ay = r.center().y()
        p.drawLine(QPointF(ax - 4, ay - 5), QPointF(ax + 1, ay))
        p.drawLine(QPointF(ax + 1, ay), QPointF(ax - 4, ay + 5))


# ---------------------------------------------------------------------------
# About (Gelistirici) sayfasi -- animasyonlu arka plan
# ---------------------------------------------------------------------------
class AboutPage(QWidget):
    MAIL = "kayhankafali@gmail.com"
    MAIL_SHOWN = "@kayhankafali"
    GITHUB = "https://github.com/espincom"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 24, 40, 22)
        lay.setSpacing(0)
        lay.addStretch(1)

        self.logo = QLabel("🔓")
        self.logo.setFixedSize(76, 76)
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 %s, stop:1 %s);"
            "border-radius: 22px; color: white; font-size: 34px; font-weight: 800;"
            % (C_ACCENT, C_ACCENT_2))
        lay.addWidget(self.logo, 0, Qt.AlignmentFlag.AlignHCenter)
        lay.addSpacing(16)

        self.title = QLabel("PDF Password Breaker")
        self.title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.title.setStyleSheet("font-size: 28px; font-weight: 800; letter-spacing: 1px;")
        lay.addWidget(self.title)
        lay.addSpacing(4)

        self.sub = QLabel("")
        self.sub.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.sub.setStyleSheet("color:%s; font-size: 12px;" % C_MUTED)
        lay.addWidget(self.sub)
        lay.addSpacing(20)

        self.message = QLabel("")
        self.message.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.message.setWordWrap(True)
        self.message.setStyleSheet("font-size: 14px; color:%s;" % C_TEXT)
        lay.addWidget(self.message)
        lay.addSpacing(16)

        self.by = QLabel("By espin0")
        self.by.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.by.setFixedHeight(30)
        self.by.setStyleSheet(
            "color: white; font-size: 12px; font-weight: 700; padding: 0 18px;"
            "border-radius: 15px;"
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 %s, stop:1 %s);"
            % (C_ACCENT, C_ACCENT_2))
        lay.addWidget(self.by, 0, Qt.AlignmentFlag.AlignHCenter)
        lay.addSpacing(22)

        holder = QHBoxLayout()
        holder.addStretch(1)
        inner = QVBoxLayout()
        inner.setSpacing(12)
        self.mail_card = ContactCard("✉", "Gmail", self.MAIL_SHOWN, C_ACCENT)
        self.mail_card.setToolTip(self.MAIL)
        self.mail_card.clicked.connect(self._open_mail)
        self.git_card = ContactCard("</>", "GitHub", "github.com/espincom", C_ACCENT_2)
        self.git_card.setToolTip(self.GITHUB)
        self.git_card.clicked.connect(self._open_github)
        inner.addWidget(self.mail_card)
        inner.addWidget(self.git_card)
        holder.addLayout(inner)
        holder.addStretch(1)
        lay.addLayout(holder)

        lay.addSpacing(16)
        self.foot = QLabel("")
        self.foot.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.foot.setStyleSheet("color:%s; font-size: 11px;" % C_MUTED)
        lay.addWidget(self.foot)
        lay.addStretch(2)

        self.retranslate()

    def retranslate(self):
        self.sub.setText(tr("subtitle"))
        self.message.setText(tr("ab_message"))
        self.by.setText(tr("ab_by"))
        self.mail_card.set_texts(tr("ab_mail_label"), tr("ab_mail_hint"))
        self.git_card.set_texts(tr("ab_github_label"), tr("ab_github_hint"))
        self.foot.setText("")

    def _tick(self):
        self._phase = (self._phase + 0.004) % 1.0
        self.update()

    def _open_mail(self):
        QApplication.clipboard().setText(self.MAIL)
        QDesktopServices.openUrl(QUrl("mailto:" + self.MAIL))
        self._flash(tr("ab_copied"))

    def _open_github(self):
        QDesktopServices.openUrl(QUrl(self.GITHUB))

    def _flash(self, text):
        self.foot.setText(text)
        QTimer.singleShot(2200, lambda: self.foot.setText(""))

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect())
        p.fillRect(r, QColor(C_BG))

        ph = self._phase * 2 * math.pi
        for i, color in enumerate((QColor(C_ACCENT), QColor(C_ACCENT_2))):
            cx = r.center().x() + math.cos(ph + i * 2.1) * r.width() * 0.26
            cy = r.center().y() + math.sin(ph * 1.3 + i * 1.7) * r.height() * 0.28
            rad = min(r.width(), r.height()) * (0.55 + 0.05 * math.sin(ph + i))
            grad = QRadialGradient(QPointF(cx, cy), rad)
            c = QColor(color); c.setAlpha(46)
            grad.setColorAt(0.0, c)
            c2 = QColor(color); c2.setAlpha(0)
            grad.setColorAt(1.0, c2)
            p.fillRect(r, QBrush(grad))

        p.setPen(QPen(QColor(255, 255, 255, 8), 1))
        step = 32
        x = int(r.left())
        while x < r.right():
            p.drawLine(x, int(r.top()), x, int(r.bottom()))
            x += step
        y = int(r.top())
        while y < r.bottom():
            p.drawLine(int(r.left()), y, int(r.right()), y)
            y += step


# ---------------------------------------------------------------------------
# Ana pencere
# ---------------------------------------------------------------------------
class PDFBreakerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(740, 700)
        self.pdf_path = ""
        self.wordlist_path = ""
        self.worker_thread = None
        self.worker = None
        self._hue = 190

        self.init_ui()
        self.apply_styles()
        self._start_header_animation()
        self.retranslate()

    # ---------------- UI ----------------
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # --- ust bar: dil butonlari ---
        topbar = QHBoxLayout()
        topbar.setContentsMargins(16, 10, 16, 0)
        topbar.addStretch()
        self.btn_en = QPushButton("EN")
        self.btn_tr = QPushButton("TR")
        for b, code in ((self.btn_en, "en"), (self.btn_tr, "tr")):
            b.setObjectName("langBtn")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedSize(42, 26)
            b.clicked.connect(lambda _, c=code: self.change_language(c))
            topbar.addWidget(b)
        root.addLayout(topbar)

        # --- sekmeler ---
        self.tabs = QTabWidget()
        self.tabs.setObjectName("tabs")
        root.addWidget(self.tabs)

        self.tabs.addTab(self._build_main_tab(), "")
        self.about_page = AboutPage()
        self.tabs.addTab(self.about_page, "")

    def _build_main_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(14)

        self.header = QLabel()
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setObjectName("header")
        layout.addWidget(self.header)

        self.subtitle = QLabel()
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setObjectName("subtitle")
        layout.addWidget(self.subtitle)

        # kart
        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setSpacing(10)
        cl.setContentsMargins(18, 18, 18, 18)

        self.pdf_label = QLabel()
        self.pdf_label.setObjectName("fileLabel")
        self.btn_pdf = QPushButton()
        self.btn_pdf.setObjectName("selectBtn")
        self.btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pdf.clicked.connect(self.select_pdf)

        self.word_label = QLabel()
        self.word_label.setObjectName("fileLabel")
        self.btn_word = QPushButton()
        self.btn_word.setObjectName("selectBtn")
        self.btn_word.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_word.clicked.connect(self.select_wordlist)

        cl.addWidget(self.pdf_label)
        cl.addWidget(self.btn_pdf)
        cl.addWidget(self.word_label)
        cl.addWidget(self.btn_word)

        # cekirdek ayari
        self._max_cores, self._physical_cores = detect_cpu()
        default_cores = max(1, min(self._physical_cores, self._max_cores))

        self.cpu_info = QLabel()
        self.cpu_info.setObjectName("cpuInfo")
        self.core_label = QLabel()
        self.core_label.setObjectName("fileLabel")
        self.core_slider = QSlider(Qt.Orientation.Horizontal)
        self.core_slider.setObjectName("coreSlider")
        self.core_slider.setMinimum(1)
        self.core_slider.setMaximum(self._max_cores)
        self.core_slider.setValue(default_cores)
        self.core_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.core_slider.valueChanged.connect(self._update_core_label)

        cl.addWidget(self.cpu_info)
        cl.addWidget(self.core_label)
        cl.addWidget(self.core_slider)
        layout.addWidget(card)

        # aksiyon butonlari
        bl = QHBoxLayout()
        bl.setSpacing(12)
        self.btn_attack = GlowButton("", QColor(239, 68, 68))
        self.btn_attack.setObjectName("attackBtn")
        self.btn_attack.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_attack.clicked.connect(self.start_attack)

        self.btn_stop = QPushButton()
        self.btn_stop.setObjectName("stopBtn")
        self.btn_stop.setEnabled(False)
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.clicked.connect(self.stop_attack)

        bl.addWidget(self.btn_attack)
        bl.addWidget(self.btn_stop)
        layout.addLayout(bl)

        # ilerleme
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress")
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setObjectName("log")
        layout.addWidget(self.log)

        # durum
        status_row = QHBoxLayout()
        status_row.setSpacing(8)
        status_row.addStretch()
        self.spinner = Spinner()
        status_row.addWidget(self.spinner)
        self.status = QLabel()
        self.status.setObjectName("status")
        status_row.addWidget(self.status)
        status_row.addStretch()
        layout.addLayout(status_row)

        return page

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0b1120; }
            QWidget { color: #f1f5f9; font-size: 14px; }

            #tabs::pane { border: none; background: #0b1120; }
            QTabBar::tab {
                background: #131c31; color: #94a3b8;
                padding: 8px 22px; margin-right: 4px;
                border-top-left-radius: 8px; border-top-right-radius: 8px;
                font-weight: 700;
            }
            QTabBar::tab:selected { background: #1e293b; color: #38bdf8; }
            QTabBar::tab:hover { color: #e2e8f0; }

            #langBtn {
                background: #131c31; color: #94a3b8; border: 1px solid #1e293b;
                border-radius: 6px; font-weight: 700; font-size: 12px;
            }
            #langBtn:hover { border: 1px solid #38bdf8; color: #e2e8f0; }
            #langBtn:checked {
                background: #38bdf8; color: #0b1120; border: 1px solid #38bdf8;
            }

            #header { font-size: 30px; font-weight: 800; color: #38bdf8; letter-spacing: 1px; }
            #subtitle { color: #64748b; font-size: 13px; }

            #card { background-color: #131c31; border: 1px solid #1e293b; border-radius: 14px; }
            #fileLabel { color: #cbd5e1; font-size: 13px; padding: 4px 2px; }
            #cpuInfo { color: #38bdf8; font-size: 12px; font-weight: 600; padding: 6px 2px 0 2px; }

            #selectBtn {
                background-color: #1e293b; color: #e2e8f0;
                border: 1px solid #334155; border-radius: 8px;
                padding: 9px; font-weight: 600;
            }
            #selectBtn:hover { background-color: #334155; border: 1px solid #38bdf8; }
            #selectBtn:pressed { background-color: #0f172a; }

            #attackBtn {
                background-color: #ef4444; color: white; border: none;
                border-radius: 10px; min-height: 48px; font-size: 16px; font-weight: 800;
            }
            #attackBtn:hover { background-color: #f05252; }
            #attackBtn:pressed { background-color: #dc2626; }
            #attackBtn:disabled { background-color: #3f2222; color: #7f5555; }

            #stopBtn {
                background-color: #334155; color: white; border: none;
                border-radius: 10px; min-height: 48px; font-size: 16px; font-weight: 700;
            }
            #stopBtn:hover { background-color: #475569; }
            #stopBtn:disabled { background-color: #1e293b; color: #475569; }

            #progress {
                border: 1px solid #1e293b; border-radius: 8px;
                background-color: #0f172a; height: 22px;
                text-align: center; color: #e2e8f0; font-weight: 600;
            }
            #progress::chunk {
                border-radius: 7px;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0ea5e9, stop:0.5 #38bdf8, stop:1 #22d3ee);
            }

            #log {
                background-color: #020617; color: #10b981;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px; border: 1px solid #1e293b; border-radius: 10px; padding: 8px;
            }
            #status { font-size: 15px; color: #94a3b8; font-weight: 600; }

            #coreSlider::groove:horizontal { height: 6px; border-radius: 3px; background: #0f172a; }
            #coreSlider::sub-page:horizontal {
                border-radius: 3px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0ea5e9, stop:1 #22d3ee);
            }
            #coreSlider::handle:horizontal {
                width: 16px; margin: -6px 0; border-radius: 8px;
                background: #38bdf8; border: 2px solid #e0f2fe;
            }
            #coreSlider::handle:horizontal:hover { background: #7dd3fc; }
        """)

        card = self.findChild(QFrame, "card")
        if card:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setColor(QColor(0, 0, 0, 160))
            shadow.setBlurRadius(30)
            shadow.setOffset(0, 6)
            card.setGraphicsEffect(shadow)

    # ---------------- dil ----------------
    def change_language(self, code):
        set_language(code)
        self.retranslate()

    def retranslate(self):
        self.setWindowTitle(tr("app_title"))
        self.btn_en.setChecked(current_language() == "en")
        self.btn_tr.setChecked(current_language() == "tr")
        self.btn_en.setToolTip(tr("lang_tip_en"))
        self.btn_tr.setToolTip(tr("lang_tip_tr"))

        self.tabs.setTabText(0, tr("tab_main"))
        self.tabs.setTabText(1, tr("tab_about"))

        self.header.setText(tr("header"))
        self.subtitle.setText(tr("subtitle"))
        self.btn_pdf.setText(tr("btn_pick_pdf"))
        self.btn_word.setText(tr("btn_pick_word"))
        self.btn_attack.setText(tr("btn_attack"))
        self.btn_stop.setText(tr("btn_stop"))

        # dosya etiketleri (secili ise ismi koru)
        if self.pdf_path:
            self.pdf_label.setText(tr("pdf_sel", os.path.basename(self.pdf_path)))
        else:
            self.pdf_label.setText(tr("pdf_none"))
        if self.wordlist_path:
            self.word_label.setText(tr("word_sel", os.path.basename(self.wordlist_path)))
        else:
            self.word_label.setText(tr("word_none"))

        self.cpu_info.setText(tr("cpu_info", self._physical_cores, self._max_cores))
        self._update_core_label(self.core_slider.value())

        if not self.worker:  # sadece bosta iken durumu sifirla
            self.status.setText(tr("st_ready"))

        self.about_page.retranslate()

    # ---------------- cekirdek etiketi ----------------
    def _update_core_label(self, val):
        if val >= self._max_cores:
            note = tr("sp_max")
        elif val > self._physical_cores:
            note = tr("sp_hyper")
        elif val == self._physical_cores:
            note = tr("sp_reco")
        elif val == 1:
            note = tr("sp_quiet")
        else:
            note = tr("sp_balanced")
        self.core_label.setText(tr("speed", val, self._max_cores, note))

    # ---------------- baslik animasyonu ----------------
    def _start_header_animation(self):
        self._header_timer = QTimer(self)
        self._header_timer.timeout.connect(self._animate_header)
        self._header_timer.start(60)

    def _animate_header(self):
        self._hue = (self._hue + 2) % 360
        c = QColor.fromHsv(self._hue, 170, 255)
        self.header.setStyleSheet(
            f"#header {{ font-size: 30px; font-weight: 800; letter-spacing: 1px; color: {c.name()}; }}"
        )

    # ---------------- dosya secimi ----------------
    def select_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, tr("dlg_pick_pdf"), "", "PDF (*.pdf)")
        if path:
            self.pdf_path = path
            self.pdf_label.setText(tr("pdf_sel", os.path.basename(path)))

    def select_wordlist(self):
        path, _ = QFileDialog.getOpenFileName(self, tr("dlg_pick_word"), "", "Text (*.txt)")
        if path:
            self.wordlist_path = path
            self.word_label.setText(tr("word_sel", os.path.basename(path)))

    # ---------------- saldiri ----------------
    def start_attack(self):
        if not self.pdf_path or not self.wordlist_path:
            self.status.setText(tr("err_no_files"))
            self.status.setStyleSheet("#status { color: #ef4444; font-weight: 600; }")
            return

        self.btn_attack.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.core_slider.setEnabled(False)
        self.log.clear()
        self.progress_bar.setValue(0)
        self.status.setText(tr("st_running"))
        self.status.setStyleSheet("#status { color: #fbbf24; font-weight: 600; }")
        self.spinner.start()
        self.btn_attack.pulse(False)

        self.worker_thread = QThread()
        self.worker = CrackerWorker(self.pdf_path, self.wordlist_path, self.core_slider.value())
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_log)
        self.worker.tick.connect(self.update_progress)
        self.worker.finished.connect(self.on_success)
        self.worker.failed.connect(self.on_failed)
        self.worker.stopped.connect(self.on_stopped)
        self.worker.error.connect(self.on_error)

        for sig in (self.worker.finished, self.worker.failed,
                    self.worker.stopped, self.worker.error):
            sig.connect(self.worker_thread.quit)

        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.finished.connect(self._clear_refs)

        self.worker_thread.start()

    def _clear_refs(self):
        self.worker = None
        self.worker_thread = None

    def stop_attack(self):
        if self.worker:
            self.worker.stop()
            self.status.setText(tr("st_stopping"))
            self.status.setStyleSheet("#status { color: #f97316; font-weight: 600; }")

    @pyqtSlot(int, int)
    def update_progress(self, current, total):
        pct = int(current * 100 / total) if total else 0
        self.progress_bar.setValue(pct)
        self.progress_bar.setFormat(f"{current}/{total}  (%{pct})")

    @pyqtSlot(str)
    def update_log(self, msg):
        self.log.append(msg)
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    @pyqtSlot(str)
    def on_success(self, pwd):
        self.progress_bar.setValue(100)
        self.status.setText(tr("st_found", pwd))
        self.status.setStyleSheet("#status { color: #22c55e; font-weight: 800; font-size: 19px; }")
        self.cleanup_ui()

    @pyqtSlot()
    def on_failed(self):
        self.status.setText(tr("st_notfound"))
        self.status.setStyleSheet("#status { color: #ef4444; font-weight: 600; }")
        self.cleanup_ui()

    @pyqtSlot()
    def on_stopped(self):
        self.status.setText(tr("st_stopped"))
        self.status.setStyleSheet("#status { color: #94a3b8; font-weight: 600; }")
        self.cleanup_ui()

    @pyqtSlot(str)
    def on_error(self, err):
        self.status.setText(tr("st_error", err))
        self.status.setStyleSheet("#status { color: #ef4444; font-weight: 600; }")
        self.cleanup_ui()

    def cleanup_ui(self):
        self.btn_attack.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.core_slider.setEnabled(True)
        self.spinner.stop()
        self.btn_attack.pulse(True)


if __name__ == "__main__":
    mp.freeze_support()
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = PDFBreakerApp()
    window.show()
    window.btn_attack.pulse(True)
    sys.exit(app.exec())
