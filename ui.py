from tkinter import *

# Define UI Constants
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

#########################################
# Helper Functions
#########################################

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

#########################################
# Main Application
#########################################
class KioskApp:
    def __init__(self, tkWindow: Tk):
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

        self._build_ui()
        #self.show_phone_screen()

#################################
#  DEBUG 
#################################

# Bind escape key to destroy window for safety during debugging.

        def close_win(event=None):
            tkWindow.destroy()

        tkWindow.bind('<Escape>', close_win)

# Extra Safety kill kiosk after 5s for testing
        #tkWindow.after(15000, tkWindow.destroy)

#################################
#  END DEBUG 
#################################

    def _build_ui(self):
        """Build all widgets once; show/hide screens by reconfiguring them."""
        tkWindow = self.tkWindow

        # Title
        self.lbl_title = Label(tkWindow, text="***Title***", font=FONT_TITLE, bg=BG, fg=BTN_FG)
        self.lbl_title.place(x=0, y=50, width=480)

        # Hint
        self.lbl_hint = Label(tkWindow, text="***Hint***", font=FONT_HINT, bg=BG, fg=HINT_FG)
        self.lbl_hint.place(x=0, y=90, width=480)

        # Display field
        self.lbl_display = Label(tkWindow, text="", font=FONT_DIGIT, bg=DISPLAY_BG, fg=DISPLAY_FG, relief="flat", anchor="center")
        self.lbl_display.place(x=MARGIN, y=130, width=400, height=70)

        # Message line (feedback below display)
        self.lbl_msg = Label(tkWindow, text="***Feedback***", font=FONT_MSG, bg=BG, fg=MSG_ERR_FG)
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

            frame = Frame(tkWindow, bg=border)
            frame.place(x=x, y=y, width=BTN_W, height=BTN_H)
            btn = Label(frame, text=text, font=font,
                           bg=bg, fg=fg, relief="flat", cursor="hand2")
            btn.place(x=1, y=1, width=BTN_W - 2, height=BTN_H - 2)


######################################
# Main Loop
######################################
if __name__ == "__main__":
    tkWindow = Tk()
    app = KioskApp(tkWindow)
    tkWindow.mainloop()
