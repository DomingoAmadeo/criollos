import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PyPDF2 import PdfReader


def create_form(parent):

    # .pack() method doesn't support grid placement, i'm creating a matrix to bypass that
    first_row = {
    'Nombre' : [None, None],
    'SBA' : [None, None, 10]
    }
    second_row = {
    'Sexo' : [None, None, 9],
    'Pelaje' : [None, None],
    'Nacimiento' : [None, None, 11],
    'RP' : [None, None, 6]
    }
    third_row = {
    'Criador' : [None, None],
    'Propietario' : [None, None]
    }
    fourth_row = {
    'Padre' : [None, None],
    'RP' : [None, None, 6],
    'SBA' : [None, None, 10]
    }
    fifth_row = {
    'Madre' : [None, None],
    'RP' : [None, None, 6],
    'SBA' : [None, None, 10]
    }
    widget_holder = [first_row, second_row, third_row, fourth_row, fifth_row]   # Matrix for grid placement

    for row in widget_holder:
        new_frame = ttk.Frame(parent)                                       # Frame for row packing
        new_frame.pack(fill='x', padx=5, pady=5)
        for index, (key, value) in enumerate(row.items()):                  # Label-Entry pairs assigned to the key with the label text string
            value[0] = ttk.Label(new_frame, text= key + ' : ')                  
            if index == 0:
                value[0]['width'] = 9                                       # First entry box of each row alignment
            value[0].pack(side='left', padx= (5,0), pady=5)
            value[1] = ttk.Entry(new_frame)
            value[1].state(('readonly',))
            if len(value) == 3:                                             # Using a hardcoded third value included in some of the lists
                value[1]['width'] = value[2]                                # to assign width
                value[1]['justify'] = 'right'                               # Numbers are justified right
                if key == 'Sexo':
                    value[1]['justify'] = 'left'                            # Text left
                elif key == 'Nacimiento':
                    value[1]['justify'] = 'center'                          # DoB is centered
                value[1].pack(side='left', padx= (0,5), pady=5)
            else:
                value[1].pack(side='left', expand= 1, fill='x', padx= (0,5), pady=5)    # Entries with long strings auto expand
    return widget_holder

def OpenFiles(form):
    # File selection
    file = filedialog.askopenfilename(title='Elegí archivos .PDF', filetypes=(('Archivos PDF', '*.pdf'),('Todos los archivos', '*.*')))
    reader = PdfReader(file)
    content = []

    #File parsing and simplifying 
    for page in reader.pages:
        for item in page.extract_text().splitlines():
            content.append(item.strip())

    #Content matching for data
    name = content.index('Nombre del Producto:') + 1
    id = content.index('D SBA:') + 1
    sex = content.index('SEXO:') + 1
    birth = content.index('Fecha de Nacimiento:') + 2
    hair = birth - 3
    tag = content.index('Tatuaje:') + 1
    establishment = content.index('Criador:') + 1
    owner = content.index('Propietario:') + 1

    # Matrix replication and data insertion
    viewed_horse = [{
        'Nombre' : content[name],
        'SBA' : content[id]
        },
        {
        'Sexo' : content[sex],
        'Pelaje' : content[hair],
        'Nacimiento' : content[birth],
        'RP' : content[tag]
        },
        {
        'Criador' : content[establishment],
        'Propietario' : content[owner]
        }]

    regex = 'D|{}|{}|{}'.format(viewed_horse[0]['SBA'], viewed_horse[1]['RP'], viewed_horse[1]['Pelaje'])
    father_name = content[content.index(regex) - 7]
    father_info = content[content.index(regex) - 6]
    mother_name = content[content.index(regex) - 5]
    mother_info = content[content.index(regex) - 4]

    father_object = construct_progenitor_object('Padre', father_name, father_info)
    mother_object = construct_progenitor_object('Madre', mother_name, mother_info)

    form_matrix = [*viewed_horse, father_object, mother_object] # Matrix format replicated

    update_form(form, form_matrix)

def construct_progenitor_object(sex, name, info):
    #Separating grouped data
    info = info.split('|')
    id = info[1]

    info = info[2].split(' ', 1)
    hair = info[1]

    info = info[0].split(':')
    tag = info[1]

    progenitor_object = {
        sex : name,
        #'Pelaje' : hair,
        'RP' : tag,
        'SBA' : id
    }
    return progenitor_object

def update_form(form, matrix):
    #Overlapping widget matrix with data matrix to update fields
    for i, row in enumerate(form):
        segment = matrix[i]
        for key, value in row.items():
            value[1].state(('!readonly',))
            value[1].delete(0, 'end')
            value[1].insert(0, segment[key])
            value[1].state(('readonly',))


root = tk.Tk()
app_style = ttk.Style()
app_style.theme_use('default')          # alt clam classic default
fieldbg = app_style.lookup("TEntry", 'fieldbackground',('!readonly','!disabled'))
disabledfbg = app_style.lookup("TEntry", 'fieldbackground',('!readonly','disabled'))
app_style.map('TEntry',
    fieldbackground=[('readonly', fieldbg), ('disabled', disabledfbg)])

root.geometry('600x231')
root.title('Criollos')
#root.iconbitmap()
#root.resizable(False, False)
root.option_add('*tearOff', 'false')


frame = ttk.Frame(root)
frame.pack(fill='both')

form = create_form(frame)           # PDF widget visualization gets tracked

file_button = ttk.Button(frame, text= 'Abrir', command= lambda: OpenFiles(form))
file_button.pack(side='top', pady=(0,10))


root.mainloop()