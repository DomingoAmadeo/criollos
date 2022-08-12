import db_interface as dbi

def query_data(filters, in_memory_dataframe, page_var):
        # Querying the DB and inverting the resulting DF so the newer items come first
        in_memory_dataframe[0] = create_filtered_query(filters)[::-1]
        # Adding a column to track the state of the current text filter
        in_memory_dataframe[0]['hidden'] = False
        # Setting the page_var to insert the DF into the table
        page_var.set(1)

def create_filtered_query(filters):
    def extract_data(filters):
        placeholder_dict = {}
        # Traversing the widget matrix
        for row in filters:
            for key, value in row.items():
                if isinstance(value, list):
                    placeholder_dict[key] = [value[1].get()]
                elif isinstance(value, dict):
                    values = []
                    for child_value in value.values():
                        values.append(child_value[1].get())
                    placeholder_dict[key] = values
        # Modifying the dictionary keys to match the DBs columns
        placeholder_dict['SBA'] = placeholder_dict.pop('SBA(nº)')
        placeholder_dict['Nacimiento'] = placeholder_dict.pop('Fecha de nacimiento')
        placeholder_dict['PNombre'] = [placeholder_dict['Padre'][1]]
        placeholder_dict['Padre'] = [placeholder_dict['Padre'][0]]
        placeholder_dict['MNombre'] = [placeholder_dict['Madre'][1]]
        placeholder_dict['Madre'] = [placeholder_dict['Madre'][0]]

        # Creating the definitive dictionary with the non empty values
        query_dict = {}
        for key, values in placeholder_dict.items():
            for value in values:
                if value:
                    query_dict[key] = values
        return query_dict

    # Extracting the current filters, if any, from the user input        
    query_dict = extract_data(filters)
    # Use the key/user input pair to create the final query
    return query_db(query_dict)

def query_db(query_dict):
    def get_operator(string, location):
        operators = {
            'SBA' : ['>=', '<=', '='],
            'RP' : ['>=', '<=', '='],
            'Sexo' : ['='],
            'Prefijo' : ['LIKE'],
            'Nombre' : ['LIKE'],
            'Nacimiento' : ['>=', '<='],
            'Pelaje' : ['='],
            'Criador' : ['='],
            'Propietario' : ['='],
            'Padre' : ['='],
            'Madre' : ['='],
            'PNombre' : ['LIKE'],
            'MNombre' : ['LIKE']
        }
        return operators[string][location]

    def get_value(string):
        result = {
            'SBA' : f'CAST(SUBSTR({string}, INSTR({string}, "-") + 1) AS INTEGER)',                             # Number after the "-"
            'RP' : f'CAST(TRIM ({string}, "o") AS INTEGER)',                                                    # Trim the possible "o" before number
            'Nacimiento' : f'CAST(SUBSTR({string},7)||SUBSTR({string},4,2)||SUBSTR({string},1,2) AS INTEGER)'  # Format date into number as sqlite has no datetype
        }
        return result.setdefault(string,string)

    def replace_chars(string : str):
        # Replace common characters that aren't recognized by the DB
        string = string.replace('ñ', '_')
        string = string.replace('Ñ', '_')
        string = string.replace('ü', '_')
        string = string.replace('Ü', '_')
        return string

    def create_query_string(query_dict):
        # Create the query base
        query_string = 'SELECT * FROM caballos'
        # List where the user args will be stored
        params = []
        for key, values in query_dict.items():
            for index, value in enumerate(values):                      # Pairs might be stored in each key, tracking of their index
                if value != '':
                    operator = get_operator(key, index)
                    column_reference = get_value(key)
                    if not params:                                      # First iteration
                        query_string += f' WHERE {column_reference} {operator} ?'
                    else:                                               # Additional iterations
                        query_string += f' AND {column_reference} {operator} ?'
                        
                    if operator == 'LIKE':
                        value = '%' + replace_chars(value) + '%'    # Add wildcard in string matching
                    params.append(value)

        return query_string, params

    query_str, parameters = create_query_string(query_dict)

    return dbi.prepared_query(query_str, parameters)

def clear_filters(filters):
    # Traverse the filter matrix and clear the contents of each user widget
    for row in filters:
        for value in row.values():
            if isinstance(value, list):
                try:
                    value[1].set('')
                except AttributeError:
                    value[1].delete(0,'end')
            elif isinstance(value, dict):
                for child_value in value.values():
                    try:
                        child_value[1].set('')
                    except AttributeError:
                        child_value[1].delete(0,'end')

def show_data(table, in_memory_dataframe, row_count_var, page_var, last_page_var, currently_var):
    
    rcv = row_count_var.get()
    pv = page_var.get()
    # Last item to be showed on the table
    end = rcv*pv
    # First item to be shown
    start = end - rcv
    # Update table height to match row amount
    if table['height'] != rcv:
        table['height'] = rcv
        update_geometry(table)
    # Masking the DF to show the rows not flagged as hidden
    df = in_memory_dataframe[0][~in_memory_dataframe[0]['hidden']]            
    # Delete currently shown items
    for child in table.get_children():
        table.delete(child)
    # Insert rows based on the paginated version of the DF
    for row in df.iloc[start:end].drop(columns=['hidden']).itertuples(index=False, name=None):
        table.insert('', 'end', values=row, iid=row[0])
    
    # Format the footer legend
    showing = rcv - len(table.get_children())
    total = len(df.index)
    last_page_var.set(-(total // - rcv))
    end = end - showing
    format_footer(start, end, total, currently_var)

def format_footer(start, end, total, currently_var):
    # Footer legend
    currently_var.set(f'Mostrando filas del {start + 1} al {end} de {total} registros')

def format_page_buttons(nav_frame, current, last):
    def length_zero(children):
        # No pages no buttons
        for child in children:
            child.pack_forget()

    def length_one(children):
        # Show middle and text buttons disabled
        children[2]['text'] = '1'
        children[0].state(['disabled'])
        children[2].state(['disabled'])
        children[4].state(['disabled'])
        children[1].pack_forget()
        children[3].pack_forget()

    def length_two(children):
        # Show all but the middle button
        children[1]['text'] = '1'
        children[3]['text'] = '2'
        children[2].pack_forget()

    def length_norm(children, current, last):
        # Show all buttons and update the numerical buttons to match the change in pages
        if current == last:
            current -= 1
        elif current == 1:
            current += 1

        children[1]['text'] = str(current - 1)
        children[2]['text'] = str(current)
        children[3]['text'] = str(current + 1)

    children = nav_frame.winfo_children()
    for child in reversed(children):        # Reverse order to align right
        if child.winfo_ismapped():
            child.pack_forget()
        child.pack(side='right')
        if child.state() == ('disabled',):
            child.state(['!disabled'])

    # Disable first and last buttons if fitting
    if current == 1 or current == last:
        if current == 1:
            children[0].state(['disabled'])
        if current == last:
            children[4].state(['disabled'])
    # Scenario selection according to the amount of pages
    if last > 2:
        length_norm(children, current, last)
    else:
        {'0': length_zero, '1': length_one, '2':length_two}[str(last)](children)
    # Disable the current button
    for child in children:
        if child['text'] == str(current):
            child.state(['disabled'])
            break

def table_search(a, b, c, sv, table, in_memory_dataframe, page_var):
    def validate_n_filter(sv, content, in_memory_dataframe, page_var):
        if sv.get() == content:
            # Flag the NON matching rows as hidden
            in_memory_dataframe[0]['hidden'] = in_memory_dataframe[0].iloc[:, :10].apply(
                lambda row: not row.astype('unicode').str.contains(content, case=False, regex= False).any(), axis=1)
            # Update the table
            page_var.set(1)
    # Trace the entry_var for matching data  
    entry_text = sv.get()
    table.after(750, lambda: validate_n_filter(sv, entry_text, in_memory_dataframe, page_var))
   
def sortbyvalue(table, in_memory_dataframe, page_var, col, ascending, datatype, column_index):   
    def sort_key(val, dtype):     
        if val == 'None' or val == None:                
            return None
        if dtype == 'e':                    # Numerical
            if '-' in val:                  # ID
                val = val.split('-')[1]
            if 'o' in val.lower():          # RP
                val = val.lower().strip('o')
            return int(val)
        elif dtype == 'center':             # Date, will be formated as a number YYYYMMDD
            date_list = val.split('-')
            return int(date_list[2] + date_list[1] + date_list[0])
        else:                               # Text
            return val
    # Use the column index to access the DFs column
    column = in_memory_dataframe[0].columns[column_index]
    # Sort the DF depending on the datatype
    in_memory_dataframe[0].sort_values(by=column, ignore_index=True, inplace=True, 
                                    key= lambda col: col.map(lambda value: sort_key(value, datatype)), ascending=ascending)
    # Rebind the header event to match the opposite task
    table.heading(col, command=lambda _col = col: sortbyvalue(table, in_memory_dataframe, page_var, _col, not ascending, datatype, column_index))
    page_var.set(1)

def event_select(event):
    select_item(event.widget)

def select_item(table, selected_horse=False):
    def mimic_matrix(horse_data : list):
        # Replicate matrix format for data input, hardcoded integers are the indexes of the data in the incoming list
        first_row = {
            'Nombre' : 3,
            'SBA' : 0            
        }
        second_row = {
            'Sexo' : 2,
            'Pelaje' : 5,
            'Nacimiento' : 4,
            'RP' : 1
        }
        third_row = {
            'Criador' : 6,
            'Propietario' : 7
        }
        fourth_row = {
            'Padre' : 10,
            'RP' : 12,
            'SBA' : 8
        }
        fifth_row = {
            'Madre' : 11,
            'RP' : 13,
            'SBA' : 9
        }
        matrix = [first_row, second_row, third_row, fourth_row, fifth_row]
        for row in matrix:
            for key, value in row.items():
                row[key] = horse_data[value]
        return matrix

    def fill_form(form, data):
        #Overlapping widget matrix with data matrix to update fields
        for i, frame in enumerate(form):
            text = ''
            segment = data[i]
            for index, child in enumerate(frame.winfo_children()):
                if index % 2 == 0:                                  # Label widget
                    text = child['text'][:-3]                       # Removal of the trailing ' : ' string
                else:                                               # Entry widget
                    child.state(('!readonly',))
                    child.delete(0, 'end')
                    child.insert(0, segment[text])
                    child.state(('readonly',))

    if not selected_horse:
        item = table.selection()
        query_string = 'SELECT * FROM caballos WHERE SBA = ?'
        # Create a list from the data retrieved by passing the ID to the DB
        selected_horse = dbi.prepared_query(query_string, item).values.tolist()[0]

    ntbk = table.winfo_toplevel().winfo_children()[0]
    detail_form_frame = ntbk.winfo_children()[1].winfo_children()[0].winfo_children()

    data_matrix = mimic_matrix(selected_horse)
    ntbk.select(1)
    fill_form(detail_form_frame, data_matrix)

def manage_filters(frame, btn, query_frame):
    # Alternate between visible and hidden frames
    if frame.winfo_ismapped():
        frame.pack_forget()
        btn['text'] = 'Mostrar filtros'
    else:
        frame.pack(side='top', fill='x', padx=5, pady=(5,0), before=query_frame)
        btn['text'] = 'Ocultar filtros'
    update_geometry(frame)

def update_geometry(widget):
    root = widget.winfo_toplevel()
    ntbk = root.winfo_children()[0]
    root.update_idletasks()
    # Pass event to notebook widget to resize the tab
    ntbk.event_generate('<<NotebookTabChanged>>')

def selector_query(selector, input, toplevel):
    if input.isdecimal():
        input = ['', '', input]
    else: 
        input = [input]
    horse_list = query_db({selector : input}).values.tolist()
    print(horse_list)

    table = toplevel.winfo_children()[0].winfo_children()[2].winfo_children()[3].winfo_children()[0]
    for child in table.get_children():
        table.delete(child)
    for horse in horse_list:
        table.insert('', 'end', values=horse, iid=horse[0])
    if len(horse_list) == 1:
        table.selection_set(horse_list[0][0])
        select_item(table, horse_list[0])
    elif len(horse_list) > 1:
        toplevel.winfo_children()[0].select(2)