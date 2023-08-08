from tkinter import *
import json
import wlan_devices

top4 = Toplevel()
top4.title("Save or load settings")
top4.geometry("800x500")
top4.configure(background="black")
exit_btn = Button(top4, text="Exit",fg="white", bg="black",font=("helvetica", 15), command=lambda: top4.destroy()).grid(row = 1, column=1)
load_1 = StringVar("1")
load_2 = StringVar("2")
load_3 = StringVar("3")
load_4 = StringVar("4")
usr_name = ""


def load_settings():
    label_1 = Label(top4, text= "Choose what setup we load?", font=("helvetica", 10), fg="white", bg="black")
    label_1.grid(row=1, column=1)
    load_json = wlan_devices.get_json()
    load_btn1 = Button(top4, text=load_1,fg="white", bg="black",font=("helvetica", 15), command=lambda: top4.destroy()).grid(row = 3, column=1)
    load_btn2 = Button(top4, text=load_2,fg="white", bg="black",font=("helvetica", 15), command=lambda: top4.destroy()).grid(row = 5, column=1)
    load_btn3 = Button(top4, text=load_3,fg="white", bg="black",font=("helvetica", 15), command=lambda: top4.destroy()).grid(row = 7, column=1)
    load_btn4 = Button(top4, text=load_4,fg="white", bg="black",font=("helvetica", 15), command=lambda: top4.destroy()).grid(row = 9, column=1)
    return


def save_settings():
    listbox = Listbox(top4, width=40, height=10, selectmode=MULTIPLE)
    listbox.insert(1, "load_1")
    listbox.insert(2, "load_2")
    listbox.insert(3, "load_3")
    listbox.insert(4, "load_4")
    listbox.grid(row=5, column=1)
    label_2 = Label(top4, text= "Give us name for the saved setup", font=("helvetica", 10), fg="white", bg="black")
    label_2.grid(row=1, column=1)
    entry= Entry(top4, width= 40)
    entry.focus_set()
    entry.grid(row=3, column=1)
    save_btn = Button(top4, text="Save changes",fg="white", bg="black",font=("helvetica", 15), command=lambda: get_user_data(listbox, entry)).grid(row = 12, column=1)
    #string= entry.get() when ok button pressed
    return

def get_user_data(listbox, entry):
    for i in listbox.curselection():
        saveslot = listbox.get(i)
        
        
    name_file= entry.get()
    return

def return_wlan_devices():
    return

top4.mainloop()