from tkinter import filedialog
import db_interface as dbi

def update_form(form, matrix):
    #Overlapping widget matrix with data matrix to update fields
    for i, row in enumerate(form):
        segment = matrix[i]
        for key, value in row.items():
            value[1].state(('!readonly',))
            value[1].delete(0, 'end')
            value[1].insert(0, segment[key])
            value[1].state(('readonly',))

def get_form_data(form):
    viewed_animal = {        
        'SBA' : None,
        'RP' : None,
        'Sexo' : None,
        'Nombre' : None,
        'Nacimiento' : None,
        'Pelaje' : None,
        'Criador' : None,
        'Propietario' : None,
        'Padre' : None,
        'Madre' : None
    }
    for i, row in enumerate(form):
        if i < 3:
            for key, value in row.items():
                viewed_animal[key] = value[1].get()
        elif 'Padre' in row:
                viewed_animal['Padre'] = row['SBA'][1].get()
        else:
            viewed_animal['Madre'] = row['SBA'][1].get()
    return viewed_animal

def OpenFiles(form):
    # File selection
    file = filedialog.askopenfilename(title='Elegí archivos .PDF', filetypes=(('Archivos PDF', '*.pdf'),('Todos los archivos', '*.*')))

    form_matrix = dbi.pdf_import(file)
    update_form(form, form_matrix)

def DeleteInstance(form):
    for i, row in enumerate(form):
        for key, value in row.items():
            value[1].state(('!readonly',))
            value[1].delete(0, 'end')
            value[1].state(('readonly',))
    #dbi.remove_record(form[0]['SBA'][1].get())   

def SaveInstance(form):                 ########### Actualizar
    viewed_animal = get_form_data(form)
    dbi.insert_row(viewed_animal)

def open_ancestry(frame, form):
    ntbk = frame.master
    ancestry_frame = ntbk.winfo_children()[3].winfo_children()[0].winfo_children()[0]
    x,y = ancestry_frame.grid_size()
    viewed_animal = get_form_data(form)
    #progenitor = get_progenitor(viewed_animal, 0)
    ancestry_depth =  x//2 + 1
    animal_amount = 2**ancestry_depth


    rnge = range(0, x, 2)
    rev_range = reversed(rnge)
    initial_horse = 2**(rnge[-1]//2)

    for horsePosition in range(0,initial_horse*2):
        widget = get_horse_widget_by_name(frame, horsePosition+1)
        widget['text'] = ''    
    initial_horse_widget = frame.nametowidget(f'.!notebook.!frame4.!canvas.!frame.!label{initial_horse}')
    initial_horse_widget['text'] = viewed_animal['SBA']

    for rev_col in rev_range:
        exponent = rev_col//2
        nextexponent = exponent - 1
        prevexponent = exponent + 1
        for horsePosition in reversed(range(2**exponent, 2**ancestry_depth, 2**prevexponent)):
            widget = get_horse_widget_by_name(frame, horsePosition)
            if horsePosition % 2 != 1:
                currentId = get_id(widget['text'])
                if currentId != '':
                    currentAnimal = get_progenitor(currentId)
                    if not currentAnimal.empty:
                        currentAnimal = currentAnimal.to_dict('records')[0]
                        widget['text'] = f'{currentAnimal["Nombre"]}\n{currentAnimal["SBA"]}|RP:{currentAnimal["RP"]}|{currentAnimal["Pelaje"]}'
                        
                        mother_position = horsePosition + 2**nextexponent
                        mother_widget = get_horse_widget_by_name(frame, mother_position)
                        mother_widget['text'] =  f'{currentAnimal["MNombre"]}\n{currentAnimal["Madre"]}|RP:{currentAnimal["RPMadre"]}'

                        father_position = horsePosition - 2**nextexponent
                        father_widget = get_horse_widget_by_name(frame, father_position)
                        father_widget['text'] = f'{currentAnimal["PNombre"]}\n{currentAnimal["Padre"]}|RP:{currentAnimal["RPPadre"]}'
                else:
                    widget['text'] = 'No hay\ndatos'
            elif len(widget['text']) == 0:
                widget['text'] = 'No hay\ndatos'

def get_horse_widget_by_name(widget, entry_number):
    text = f'label{entry_number}'
    if entry_number == 1:
        text = 'label'
    return widget.nametowidget(f'.!notebook.!frame4.!canvas.!frame.!{text}')

def get_progenitor(animalId):
    animalId = animalId.split('-')[-1]
    return dbi.prog_query(animalId)

def get_id(text):
    text = text.split('\n')[-1]
    return text.split('|')[0]
