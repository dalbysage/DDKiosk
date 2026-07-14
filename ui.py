from tkinter import *

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

        #Button
        button = Button(tkWindow, text="Close Window", command=tkWindow.destroy) 
        button.grid()

######################################
# Main Loop
######################################
if __name__ == "__main__":
    tkWindow = Tk()
    app = KioskApp(tkWindow)
    tkWindow.mainloop()
