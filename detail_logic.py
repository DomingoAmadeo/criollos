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

def SaveInstance(form):                 
    viewed_animal = get_form_data(form)
    dbi.insert_row(viewed_animal)
