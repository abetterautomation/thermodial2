########################################
#                                      #
# Raspberry Pi Thermometer Dial 2      #
# Written by Ryan Eggers               #
# Abetter Automation Technologies      #
# www.abetterautomation.com            #
# Licensed under The Unlicense         #
#                                      #
########################################

"""Dial display for output of DS18B20 temperature sensor on a Raspberry Pi"""

import os
import glob
import time
import Tkinter
import tkMessageBox

import viewidget

TITLE = 'Thermometer Dial'
VERSION = '2.0'
UNITS = ['degF', 'degC']
MODPROBE_GPIO = 'modprobe w1-gpio'
MODPROBE_THERM = 'modprobe w1-therm'
BASE_DIRECTORY = '/sys/bus/w1/devices/'


def _read_temp():
    f = open(device_folder + '/w1_slave', 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    temp_c = None
    temp_f = None
    if device_folder:
        lines = _read_temp()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = _read_temp()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_f, temp_c


def make_dial(master, unit):
    if unit == UNITS[0]:  # degF
        min = 60
        max = 220
        scale = 20
        semiscale = 10
    else:  # degC
        min = 0
        max = 100
        scale = 10
        semiscale = 0
    dial = viewidget.Dial(master, unit=unit, min=min, max=max,
                          majorscale=scale, semimajorscale=semiscale)
    return dial


def make_window():
    window = Tkinter.Tk()
    window.title(TITLE)

    # Add Menu
    window.menu = Tkinter.Menu(window)
    window.config(menu=window.menu)
    #  file menu
    window.menu_file = Tkinter.Menu(window.menu, tearoff=0)
    window.menu.add_cascade(label="File", menu=window.menu_file)
    window.menu_file.add_command(label="Change Sensor", command=select_sensor)
    window.menu_file.add_separator()
    window.menu_file.add_command(label="Exit", command=window.quit)
    #  about menu
    window.menu_about = Tkinter.Menu(window.menu, tearoff=0)
    window.menu.add_cascade(label="About", menu=window.menu_about)
    window.menu_about.add_command(label=TITLE, command=about)

    # Add main frame
    window.frame = Tkinter.Frame(window, relief='ridge', borderwidth=2)
    window.frame.pack(fill='both', expand=1)
    # Add Dial and unit scale
    window.dial = make_dial(window.frame, UNITS[0])
    window.dial.pack(expand=1, fill='x', side=Tkinter.LEFT)
    window.unit_frame = Tkinter.Frame(window.frame)
    window.unit_frame.pack(side=Tkinter.RIGHT)
    window.unit_scale = Tkinter.Scale(window.unit_frame, from_=0, to=1, width=20, command=change_unit, showvalue=False)
    window.unit_scale.grid(row=0, column=0, rowspan=2)
    degree_sign = viewidget.Dial.DEGREE
    window.degF_label = Tkinter.Label(window.unit_frame, anchor='n', text=degree_sign + 'F')
    window.degF_label.grid(row=0, column=1, sticky='ns')
    window.degC_label = Tkinter.Label(window.unit_frame, anchor='s', text=degree_sign + 'C')
    window.degC_label.grid(row=1, column=1, sticky='ns')
    # Add label
    if device_folder:
        text = device_folder
    else:
        text = 'No Sensor Found'
    window.device_label = Tkinter.Label(window.frame, text=text)
    window.device_label.pack(side=Tkinter.TOP)
    return window


def update_dial():
    unit_index = test_window.unit_scale.get()
    temp = read_temp()[int(unit_index)]
    test_window.dial.set_value(temp)


def loop_update_dial():
    update_dial()
    test_window.after(1000, loop_update_dial)


def change_unit(unit_index):
    unit = UNITS[int(unit_index)]
    test_window.dial.destroy()
    test_window.dial = make_dial(test_window.frame, unit)
    test_window.dial.pack(side=Tkinter.LEFT)
    update_dial()


def select_sensor():
    sensor_select = Tkinter.Toplevel()
    sensor_select.transient(test_window)
    sensor_select.title('Change Sensor')
    sensor_select.geometry("+%d+%d" % (test_window.winfo_rootx() + 50, test_window.winfo_rooty() + 100))
    sensor_select.grab_set()
    close = lambda event=None: (test_window.focus_set(), sensor_select.destroy())
    sensor_select.protocol("WM_DELETE_WINDOW", close)
    listbox = Tkinter.Listbox(sensor_select, height=len(device_folders) + 1, width=35)
    for device in device_folders:
        i = device_folders.index(device)
        listbox.insert(i, device)
    listbox.pack(fill='x', expand=1)
    button_frame = Tkinter.Frame(sensor_select)
    button_frame.pack(fill='y')
    select = lambda event=None: (change_sensor(listbox.curselection()), close())
    select_button = Tkinter.Button(button_frame, text='Select', command=select)
    select_button.grid(row=0, column=0)
    cancel_button = Tkinter.Button(button_frame, text='Cancel', command=close)
    cancel_button.grid(row=0, column=1)
    sensor_select.bind('<Return>', select)
    sensor_select.bind('<Escape>', close)
    sensor_select.focus_set()
    sensor_select.wait_window(sensor_select)


def change_sensor(selection):
    global device_folder
    try:
        index = selection[0]
    except IndexError:
        pass
    else:
        device_folder = device_folders[index]
        test_window.device_label.config(text=device_folder)
        update_dial()


def about():
    message = 'By Abetter Automation'
    tkMessageBox.showinfo('About ' + TITLE, 'Version ' + VERSION + '\n' + message)


if __name__ == '__main__':
    os.system(MODPROBE_GPIO)
    os.system(MODPROBE_THERM)
    device_folders = glob.glob(BASE_DIRECTORY + '28*')
    try:
        device_folder = device_folders[0]
    except IndexError:
        device_folder = None

    # create the graphical interface
    test_window = make_window()
    loop_update_dial()
    test_window.focus_set()
    test_window.mainloop()
