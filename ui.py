import signal
import json
import pathlib
import sys
import ddutils
import tkinter

# ---- Define UI Constants -------------------------------------
BG          = "#ffffff"
BTN_BG      = "#f5f5f5"
BTN_FG      = "#111111"
BTN_BORDER  = "#cccccc"
DEL_BG      = "#fff0f0"
DEL_FG      = "#cc2222"
DEL_BORDER  = "#ddaaaa"
ENT_BG      = "#e8f4e8"
ENT_FG      = "#226622"
ENT_BORDER  = "#88cc88"
DISPLAY_BG  = "#f0f0f0"
DISPLAY_FG  = "#111111"
HINT_FG     = "#444444"
MSG_OK_FG   = "#226622"
MSG_ERR_FG  = "#cc2222"
PRESS_BG    = "#dddddd"     # flash colour on tap

FONT_TITLE  = ("sans-serif", 24, "bold")
FONT_HINT   = ("sans-serif", 15)
FONT_DIGIT  = ("Courier", 22, "bold")
FONT_KEY    = ("sans-serif", 28)
FONT_ACTION = ("sans-serif", 16, "bold")
FONT_MSG    = ("sans-serif", 14)

TIMEOUT_MS  = 30_000        # 30 s idle reset
BTN_H       = 110           # button height px
BTN_W       = 120           # button width px
GAP         = 20            # gap between buttons
MARGIN      = 40            # left/right margin

# ---- Configuration -------------------------------------------
CONFIG_FILE = pathlib.Path(__file__).parent / "kiosk.cfg"

def request_reload(signum, frame):
    global _reload_requested
    _reload_requested = True

def reload_log_level():
    global _reload_requested
    if _reload_requested:
        _reload_requested = False
        try:
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
            new_level = cfg.get("LOG_LEVEL", "WARNING")
            logger.setLevel(new_level)
            logger.warning(f"Log level reloaded to {new_level}")
        except (FileNotFoundError, PermissionError, json.JSONDecodeError) as e:
            logger.error(f"SIGHUP reload failed, keeping current level: {e}")
    tkWindow.after(1000, reload_log_level)

def parse_config_file():
    try:
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
    except FileNotFoundError:
        print(f"CRITICAL: Config file not found: {CONFIG_FILE}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"CRITICAL: Permission denied reading config file: {CONFIG_FILE}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"CRITICAL: Config file is corrupt or invalid JSON: {CONFIG_FILE}  — {e}", file=sys.stderr)
        sys.exit(1)

    required_keys = ["MODULE_NAME", "LOG_LEVEL", "LOG_FILE", "URL"]
    missing = [k for k in required_keys if k not in cfg]
    if missing:
        print(f"CRITICAL: Missing required config keys: {missing}", file=sys.stderr)
        sys.exit(1)

    return cfg

# ---- Helper Functions ----------------------------------------
def format_phone(digits: str) -> str:
    """Format up to 10 digit string as (###) ###-####."""
    d = digits[:10]
    if len(d) <= 3:
        return f"({''.join(d) + '_' * (3 - len(d))})" + " ___-____"
    if len(d) <= 6:
        return f"({d[:3]}) {''.join(d[3:]) + '_' * (6 - len(d))}-____"
    return f"({d[:3]}) {d[3:6]}-{''.join(d[6:]) + '_' * (10 - len(d))}"

def mask_pin(digits: str) -> str:
    """Show entered digits as dots, pad remainder with underscores."""
    filled = "●" * len(digits)
    empty  = "_" * (6 - len(digits))
    return f"{filled}{empty}"

# ---- Main Application ----------------------------------------
class KioskApp:
    def __init__(self, tkWindow: tkinter.Tk):
        self.tkWindow = tkWindow
        tkWindow.title('Gate Access')
        width = tkWindow.winfo_screenwidth()
        height = tkWindow.winfo_screenheight()
        tkWindow.geometry(f"{width}x{height}")
        self.tkWindow.attributes("-fullscreen", True)
        self.tkWindow.resizable(False, False)

        # Prevent window manager interaction
        self.tkWindow.overrideredirect(True)

        # Initialize variables
        self.timeout  = None        # after() handle for idle reset
        self.digits   = ""          # current entry buffer
        self.phone    = ""          # confirmed phone from screen 1

        # Bind escape key to destroy window for safety during debugging.
        # Run code with -O flag (python -O exe.py) to strip
        if __debug__:
            def close_win(event=None):
                tkWindow.destroy()
            tkWindow.bind('<Escape>', close_win)

        # Instantiate UI
        self._build_ui()
        self.show_phone_screen()

    def _build_ui(self):
        """Build all widgets once; show/hide screens by reconfiguring them."""
        tkWindow = self.tkWindow

        # Title
        self.lbl_title = tkinter.Label(tkWindow, text="***Title***", font=FONT_TITLE, bg=BG, fg=BTN_FG)
        self.lbl_title.place(x=0, y=50, width=480)

        # Hint
        self.lbl_hint = tkinter.Label(tkWindow, text="***Hint***", font=FONT_HINT, bg=BG, fg=HINT_FG)
        self.lbl_hint.place(x=0, y=90, width=480)

        # Display field
        self.lbl_display = tkinter.Label(tkWindow, text="", font=FONT_DIGIT, bg=DISPLAY_BG, fg=DISPLAY_FG, relief="flat", anchor="center")
        self.lbl_display.place(x=MARGIN, y=130, width=400, height=70)

        # Message line (feedback below display)
        self.lbl_msg = tkinter.Label(tkWindow, text="***Feedback***", font=FONT_MSG, bg=BG, fg=MSG_ERR_FG)
        self.lbl_msg.place(x=0, y=210, width=480)

        # Keypad buttons — build grid, store refs for flash
        self._buttons = {}
        layout = [
            ("1", 0, 0), ("2", 0, 1), ("3", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2),
            ("DEL", 3, 0), ("0", 3, 1), ("ENT", 3, 2),
        ]
        for (label, row, col) in layout:
            x = MARGIN + col * (BTN_W + GAP)
            y = 240 + row * (BTN_H + GAP)
            if label == "DEL":
                bg, fg, border = DEL_BG, DEL_FG, DEL_BORDER
                text, font = "DEL ⌫", FONT_ACTION
            elif label == "ENT":
                bg, fg, border = ENT_BG, ENT_FG, ENT_BORDER
                text, font = "ENT ↵", FONT_ACTION
            else:
                bg, fg, border = BTN_BG, BTN_FG, BTN_BORDER
                text, font = label, FONT_KEY

            frame = tkinter.Frame(tkWindow, bg=border)
            frame.place(x=x, y=y, width=BTN_W, height=BTN_H)
            btn = tkinter.Label(frame, text=text, font=font,
                           bg=bg, fg=fg, relief="flat", cursor="hand2")
            btn.place(x=1, y=1, width=BTN_W - 2, height=BTN_H - 2)

            # bind touch/click
            btn.bind("<ButtonPress-1>",
                     lambda e, l=label, b=btn, ob=bg: self._on_press(l, b, ob))
            self._buttons[label] = (btn, bg)

# ---- Button Interaction --------------------------------------
    def _on_press(self, label: str, btn: tkinter.Label, original_bg: str):
        """Flash button then handle input."""
        btn.config(bg=PRESS_BG)
        self.tkWindow.after(120, lambda: btn.config(bg=original_bg))
        self._reset_timeout()
        self._handle_key(label)

    def _handle_key(self, label: str):
        if label == "DEL":
            self.digits = self.digits[:-1]
        elif label == "ENT":
            self._on_enter()
            return
        else:
            max_len = 10 if self._screen == "phone" else 6
            if len(self.digits) < max_len:
                self.digits += label
        self._update_display()

    def _on_enter(self):
        if self._screen == "phone":
            if len(self.digits) == 10:
                self._verify_user()
            else:
                self._show_msg("Please enter your full 10-digit phone number.", error=True)
        elif self._screen == "pin":
            if len(self.digits) >= 4:
                self._verify_pin()
            else:
                self._show_msg("PIN must be at least 4 digits.", error=True)

# ---- Display Update ------------------------------------------
    def _update_display(self):
        if self._screen == "phone":
            self.lbl_display.config(text=format_phone(self.digits))
        elif self._screen == "pin":
            self.lbl_display.config(text=mask_pin(self.digits))

    def _show_msg(self, text: str, error: bool = True):
        color = MSG_ERR_FG if error else MSG_OK_FG
        self.lbl_msg.config(text=text, fg=color)

    def _clear_msg(self):
        self.lbl_msg.config(text="")

# ---- Idle Timeout --------------------------------------------
    def _reset_timeout(self):
        if self.timeout:
            self.tkWindow.after_cancel(self.timeout)
        self.timeout = self.tkWindow.after(TIMEOUT_MS, self._on_timeout)

    def _on_timeout(self):
        logger.info("Idle timeout — returning to phone screen")
        self.show_phone_screen()

# ---- Screens -------------------------------------------------
    def show_phone_screen(self):
        self._screen  = "phone"
        self.digits   = ""
        self.phone    = ""
        self._clear_msg()
        self.lbl_title.config(text="Welcome")
        self.lbl_hint.config(text="Enter your phone number")
        self.lbl_display.config(text=format_phone(""))
        self._reset_timeout()

# ---- Main Loop -----------------------------------------------
if __name__ == "__main__":
    cfg = parse_config_file()
    logger = ddutils.setup_logging(
        log_file=cfg["LOG_FILE"],
        name=cfg["MODULE_NAME"],
        level=cfg["LOG_LEVEL"],
    )
    logger.info("Config loaded and logging initialized")

    _reload_requested = False
    signal.signal(signal.SIGHUP, request_reload)

    tkWindow = tkinter.Tk()
    app = KioskApp(tkWindow)
    reload_log_level()
    tkWindow.mainloop()

