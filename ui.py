from tkinter import *

# Window
tkWindow = Tk()
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

tkWindow.mainloop()
