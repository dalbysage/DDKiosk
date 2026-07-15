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

class KioskApp:
    def __init__(self, tkWindow: Tk):
        self.tkWindow = tkWindow
        tkWindow.title('Gate Access')
        width = tkWindow.winfo_screenwidth()
        height = tkWindow.winfo_screenheight()
        tkWindow.geometry(f"{width}x{height}")

        # Feedback
        strFeedback = 'Please Enter your phone number:'
        lblFeedback = Label(tkWindow, text = strFeedback)
        lblFeedback.grid()

        # Button
        button = Button(tkWindow, text="Close Window", command=tkWindow.destroy) 
        button.grid()

        # Prevent window manager interaction
        self.tkWindow.overrideredirect(True)

        # Initialize variables
        self.digits   = ""          # current entry buffer
        self.phone    = ""          # confirmed phone from screen 1

        self._build_ui()

    def _build_ui(self):
        """Build all widgets once; show/hide screens by reconfiguring them."""
        tkWindow = self.tkWindow

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
