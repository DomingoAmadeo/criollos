import tkinter as tk
from tkinter import ttk
import detail_logic as dl
import db_interface as dbi

def create_label_widget_pair(parent_frame, pair_name, pair_list, pady, method = ttk.Entry):
    # Creation of the label widget + user widget pair, pady depends on the parent frame
    pair_list[0] = ttk.Label(parent_frame, text= pair_name + ' : ')
    pair_list[0].pack(side='left', padx=(5,0), pady=pady)
    pair_list[1] = method(parent_frame)
    if pair_list[2] != 0:                                           # If length then width = length
        pair_list[1]['width'] = pair_list[2]
        pair_list[1].pack(side='left', padx=(0,5), pady=pady)
    else:                                                           # Else, it fills the horizontal axis
        pair_list[1].pack(side='left', padx=(0,5), pady=pady, fill='x', expand=True)
    return pair_list[0], pair_list[1]                               # Returns the pair for assigning

def populate_detailed_tab(frame):
    def create_form(parent):
        # .pack() method doesn't support grid placement, i'm creating a matrix to bypass that
        first_row = {
        'Nombre' : [None, None, 0],
        'SBA' : [None, None, 10]
        }
        second_row = {
        'Sexo' : [None, None, 9],
        'Pelaje' : [None, None, 0],
        'Nacimiento' : [None, None, 11],
        'RP' : [None, None, 6]
        }
        third_row = {
        'Criador' : [None, None, 0],
        'Propietario' : [None, None, 0]
        }
        fourth_row = {
        'Padre' : [None, None, 0],
        'RP' : [None, None, 6],
        'SBA' : [None, None, 10]
        }
        fifth_row = {
        'Madre' : [None, None, 0],
        'RP' : [None, None, 6],
        'SBA' : [None, None, 10]
        }
        widget_holder = [first_row, second_row, third_row, fourth_row, fifth_row]   # Matrix for grid placement

        for row in widget_holder:
            new_frame = ttk.Frame(parent)                                       # Frame for row packing
            new_frame.pack(fill='x', padx=5, pady=5)
            first = True
            for key, value in row.items():
                value[0], value[1] = create_label_widget_pair(new_frame, key, value, 5)
                if first:
                    first = False
                    value[0]['width'] = 9                                       # First entry box of each row alignment
                if key == 'Nacimiento':
                        value[1]['justify'] = 'center'                          # DoB is centered
                value[1].state(('readonly',))
        return widget_holder

    form_frame = ttk.Frame(frame)
    form_frame.pack(side='top', fill='x', expand=True)

    form_children = create_form(form_frame)           # PDF widget visualization gets tracked

    file_button = ttk.Button(frame, text= 'Abrir', command= lambda: dl.OpenFiles(form_children))
    file_button.pack(side='left', pady=(0,10), expand=True)

    save_button = ttk.Button(frame, text= 'Guardar', command= lambda: dl.SaveInstance(form_children))
    save_button.pack(side='left', pady=(0,10), expand=True)

    clear_button = ttk.Button(frame, text= 'Borrar', command= lambda: dl.DeleteInstance(form_children))
    clear_button.pack(side='left', pady=(0,10), expand=True)

