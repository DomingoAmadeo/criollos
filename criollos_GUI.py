import tkinter as tk
from tkinter import ttk
from dateentry_widget import Dateentry
import detail_logic as dl
import table_logic as tl
import criollos_graphic_resources as cgr
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

def populate_table_tab(parent_widget):
    def populate_filter_frame(master_widget):
        # Creating a matrix with dictionaries as rows due to pack() limitations
        # Dictionary structure: 
        # If key is dict its a labelframe with child widgets
        # Value is a list of [Label, Entry/Combobox, length(in characters)] 
        # If the length is 0, it fills the horizontal axis
        # If there is a 4th item in the list, its a combobox instead of an entry widget
        first_row = {
        'SBA(nº)' : {'Desde' : [None, None, 8], 
                    'Hasta' : [None, None, 8]},
        'RP' : {'Desde' : [None, None, 5], 
                'Hasta' : [None, None, 5]},
        'Fecha de nacimiento' : {'Desde' : [None, None, 12, 0], 
                                'Hasta' : [None, None, 12, 0]}}
        second_row = {
        'Sexo' : [None, None, 8, 0],
        'Prefijo' : [None, None, 10, 0],
        'Nombre' : [None, None, 0],
        'Pelaje' : [None, None, 16, 0]}
        third_row = {
        'Criador' : [None, None, 0, 0],
        'Propietario' : [None, None, 0, 0]}
        fourth_row ={
        'Padre' : {'SBA(nº)' : [None, None, 8],
                    'Nombre' : [None, None, 0]},
        'Madre' : {'SBA(nº)' : [None, None, 8],
                    'Nombre' : [None, None, 0]}}
        filter_matrix = [first_row, second_row, third_row, fourth_row]

        # Matrix traversal for widget creation
        for row in filter_matrix:
            row_frame = ttk.Frame(master_widget)                                                            # Row frame
            row_frame.pack(side='top', fill='x', expand=True)
            for key, value in row.items():                                                                  # Using the string key as a name to bind its corresponging widgets
                if len(value) > 3:                                                                          # Combobox creation
                    value[0], value[1] = create_label_widget_pair(row_frame, key, value, 5, ttk.Combobox)
                    value[1]['values'] = [''] + dbi.combobox_query(key)                                     # Filling the dropdown with DB values
                    value[1].state(('readonly',))                                                           # Disabling typing
                elif len(value) > 2:                                                                        # Regular entry creation
                    value[0], value[1] = create_label_widget_pair(row_frame, key, value, 5)
                else:                                                                                       # LabelFrame creation
                    label_frame = ttk.Labelframe(row_frame, text=key)
                    label_frame.pack(side='left', padx= 5, fill='x', expand=True)
                    for key2, value2 in value.items():
                        if len(value2) > 3:                                                                 # Dateentry widget used instead of combobox
                            value2[0], value2[1] = create_label_widget_pair(label_frame, key2, value2, (0,7), Dateentry)
                        elif len(value2) > 2:                                                               # Regular entry creation
                            value2[0], value2[1] = create_label_widget_pair(label_frame, key2, value2, (0,7))
        return filter_matrix
    
    # Virtual df inside a list to allow in-function modification of the df
    in_memory_dataframe = [None]                           

    # Creation of the top fram which contains the fiilters
    table_filters = ttk.Frame(parent_widget)
    filter_frame = populate_filter_frame(table_filters)

    # Query buttons
    query_frame = ttk.Frame(parent_widget)
    query_frame.pack(side='top', fill='x', padx=3, pady=(5,0), expand=True)
    reset_button = ttk.Button(query_frame, text='Remover filtros', width=14, command=lambda: tl.clear_filters(filter_frame))
    reset_button.pack(side='left', fill='x', expand=True, padx=20)
    query_button = ttk.Button(query_frame, text='Mostrar registros', width=14, command=lambda: tl.query_data(filter_frame, in_memory_dataframe, page_var))
    query_button.pack(side='left', fill='x', expand=True, padx=20)

    # Table header and searchbar
    search_frame = ttk.Frame(parent_widget)
    search_frame.pack(side='top', fill='x', expand=True, padx=8, pady=(5,0))
    row_selection_label = ttk.Label(search_frame, text='Cantidad de registros por pagina: ')
    row_selection_label.pack(side='left')
    # Creation of the tkinter variable in charge of tracing the amount of rows in the table
    row_count_var = tk.IntVar(value=10)
    row_count_var.trace_add('write', lambda a,b,c: tl.show_data(records_table, in_memory_dataframe, row_count_var, page_var, last_page_var, currently_var))
    row_selection_cb = ttk.Combobox(search_frame, values= (10, 15, 20, 25), textvariable=row_count_var, width=2, state='readonly')
    row_selection_cb.pack(side='left')
    # To resize themed buttons you have to force propagate their parents size
    btn_frame = ttk.Frame(search_frame, height=19, width=89)
    btn_frame.pack_propagate(False)
    btn_frame.pack(side='left', expand= True, padx=(0,42), pady=(0,1))
    filter_btn = ttk.Button(btn_frame, text= 'Mostrar filtros', padding=(0,0,0,10), command=lambda: tl.manage_filters(table_filters, filter_btn, query_frame))
    filter_btn.pack()
    search_label = ttk.Label(search_frame, text='Buscar: ')
    search_label.pack(side='right')
    # Creation of the tkinter variable in charge of tracing the entry text to be used as a filter of the currently loaded table data
    search_var = tk.StringVar()
    search_var.trace_add('write', lambda a,b,c: tl.table_search(a,b,c, search_var, records_table, in_memory_dataframe, page_var)) 
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side='right', before=search_label)

    # Table widget and configuration
    table_frame = ttk.Frame(parent_widget)
    table_frame.pack(side='top', fill='x', padx=8, expand=True)
    # Header names for each column along with their hardcoded width(pixels) and their aligment determined by the data type (date = center, numbers = east, text = west)
    cols = (('SBA', 63, 'e'), ('RP', 35, 'e'), ('Sexo', 56, 'w'), ('Nombre', 163, 'w'), ('Nacimiento', 67, 'center'),
        ('Pelaje', 110, 'w'), ('Criad.', 38, 'e'), ('Prop.', 38, 'e'), ('Padre', 48, 'e'), ('Madre', 48, 'e'))
    records_table = ttk.Treeview(table_frame, columns=[col[0] for col in cols], show='headings', height=row_count_var.get())
    # Initialize columns and headings of the Treeview widget
    for i, (col, size, alignment) in enumerate(cols):
        records_table.column(col, width=size, anchor=alignment)
        records_table.heading(col, text=col, command=
                    lambda _col = col, _alignment = alignment, _i = i: 
                    tl.sortbyvalue(records_table, in_memory_dataframe, page_var, _col, False, _alignment, _i))    
    records_table.grid(row=1, column=0, columnspan=10)
    records_table.bind('<Double-1>', tl.event_select)

    # Table footer
    table_footer = ttk.Frame(parent_widget)
    table_footer.pack(side='top', fill='x', padx=8, pady=(0,1), expand=True)
    # Creation of the tkinter variable in charge of tracing the text of currently shown rows
    currently_var = tk.StringVar()
    currently_label = ttk.Label(table_footer, textvariable=currently_var)
    currently_label.pack(side='left')
    # Frame for pagination buttons with forced size
    footer_navigation = ttk.Frame(table_footer, height=19, width=151)
    footer_navigation.pack_propagate(False)
    footer_navigation.pack(side='right')
    # Creation of the tkinter variables in charge of tracing the pages
    page_var = tk.IntVar()
    page_var.trace_add('write', lambda a,b,c: tl.show_data(records_table, in_memory_dataframe, row_count_var, page_var, last_page_var, currently_var))
    last_page_var = tk.IntVar()
    last_page_var.trace_add('write', lambda a, b, c: tl.format_page_buttons(footer_navigation, page_var.get(), last_page_var.get()))
    first_button = ttk.Button(footer_navigation, padding=(0,0,0,10), width=6, command= lambda: page_var.set(1), text='Primer')
    left_button = ttk.Button(footer_navigation, padding=(0,0,0,10), width=3, command= lambda: page_var.set(int(left_button['text'])))
    middle_button = ttk.Button(footer_navigation, padding=(0,0,0,10), width=3, command= lambda: page_var.set(int(middle_button['text'])))
    right_button = ttk.Button(footer_navigation, padding=(0,0,0,10), width=3, command= lambda: page_var.set(int(right_button['text'])))
    last_button = ttk.Button(footer_navigation, padding=(0,0,0,10), width=6, command= lambda: page_var.set(last_page_var.get()), text='Ultima')

def populate_ancestry_tab(master):
    def create_ancestry_form(parent):
        #Create the entry boxes for data population
        for i in range(1, 32):
            entry = ttk.Entry(parent)
            if i % 16 == 0:
                entry.grid(column=0, row= i)
            elif i % 8 == 0:
                entry.grid(column=2, row= i)
            elif i % 4 == 0:
                entry.grid(column=4, row= i)
            elif i % 2 == 0:
                entry.grid(column=6, row= i)
            elif i % 2 == 1:
                entry.grid(column=8, row= i)

        # Request image object
        ancestry_brackets = cgr.GUI.ancestry_brackets

        # Populate grid with image object
        for i in range (4):                             # i, reverse_i in zip(range (4), reversed(range(4))):
            column = [1, 3, 5, 7]                       # i * 2 + 1
            amount = [1, 2, 4, 8]                       # math.pow(2, i)
            starting_index = amount[::-1]               # math.pow(2, reverse_i)        amount reversed
            step = [32, 16, 8, 4]                       # 32 / amount
            rowspan = starting_index[i] * 3
            for n_label in range(amount[i]):
                row = n_label * step[i] + starting_index[i]
                tk.Label(parent, image=ancestry_brackets[-1], bd=0)\
                .grid(column=column[i], row= row, rowspan=rowspan, sticky='nw', pady=9) # ancestry_brackets[-1] gets the image intended for this loop
            cgr.GUI.image_subsample(ancestry_brackets, 1, 2)                            # and sets the next one

    ancestry_frame = ttk.Frame(master)
    ancestry_frame.pack(fill='both', expand=True, padx=10, pady=10)
    create_ancestry_form(ancestry_frame)
