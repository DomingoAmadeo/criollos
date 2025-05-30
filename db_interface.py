import sqlite3
import pandas as pd
from PyPDF2 import PdfReader


def db_connect():
    # Connect to database
    conn = sqlite3.connect('test/registros_caballos.db')
    # Create cursor
    c = conn.cursor()
    return conn,c

def create_table():
        conn, c = db_connect()
        #Create a Table         DATATYPES: NULL, INTEGER, REAL, TEXT, BLOB
        with conn:
                c.execute('''CREATE TABLE IF NOT EXISTS caballos (
                        SBA TEXT NOT NULL UNIQUE,
                        RP TEXT,
                        Sexo TEXT,
                        Nombre TEXT,
                        Nacimiento TEXT,
                        Pelaje TEXT,
                        Criador TEXT,
                        Propietario TEXT,
                        Padre TEXT,
                        Madre TEXT,
                        PNombre TEXT,
                        MNombre TEXT,
                        RPPadre TEXT,
                        RPMadre TEXT
                        )''')                       
        conn.close()

def insert_row(dict):
        conn, c = db_connect()
        #dictionary format for row insertion
        #'SBA' : TEXT,
        #'RP' : TEXT,
        #'Sexo' : TEXT,
        #'Nombre' : TEXT,
        #'Nacimiento' : TEXT,
        #'Pelaje' : TEXT,
        #'Criador' : TEXT,
        #'Propietario' : TEXT,
        #'Padre' : TEXT,
        #'Madre' : TEXT
        with conn:                
                c.execute(''' INSERT INTO caballos VALUES (:SBA, :RP, :Sexo, :Nombre, :Nacimiento, :Pelaje, :Criador, :Propietario, :Padre, :Madre)''', dict)
        conn.close()

def remove_record(SBA):
        conn, c = db_connect()
        with conn:
                c.execute('DELETE FROM caballos WHERE SBA = :sba', {'sba' : SBA})
        conn.close()        

def xlsx_import(list_of_paths):
        conn, c = db_connect()
        dfs = []

        for path in list_of_paths:
                dfs.append(pd.read_excel(path))                         # Import XLSX files

        df = pd.concat(dfs)                                             # Unify files
        df = df.drop_duplicates(keep='last')                            #Drop dupes

        # Data formatting 
        df['RPPadre'] = df['Padre'].str.extract('RP:\s?(\d+)\s?-', expand= True)
        df['PNombre'] = df['Padre'].str.extract('.+-.+-.+-([0-9a-zA-z\s]+)', expand= True)
        df['Padre'] = df['Padre'].str.extract('SBA.?(\d+).?-?', expand= True)
        df['RPMadre'] = df['Madre'].str.extract('RP:\s?(\d+)\s?-', expand= True)
        df['MNombre'] = df['Madre'].str.extract('.+-.+-.+-([0-9a-zA-z\s]+)', expand= True)
        df['Madre'] = df['Madre'].str.extract('SBA.?(\d+).?-?', expand= True)
        df['Fecha Nacimiento'] = df['Fecha Nacimiento'].dt.strftime('%d-%m-%Y')

        # Handling Male/Female identical ID
        df['Identif./ Nro.'] = df['Identif./ Nro.'].str.extract('(\d+)', expand= True)
        df = df.sort_values(by='Identif./ Nro.', key=lambda col: col.astype(int))                                       # Sort data by ID number before adding text
        df.loc[df['Sexo'] == 'Hembra', 'Identif./ Nro.'] = '0' + df.loc[df['Sexo'] == 'Hembra', 'Identif./ Nro.']       # Add a 0 before Female ID
        
        #Formatting important comlumns for SQL insertion
        df['SBA'] = df['Tipo Registro'] + '-' + df['Identif./ Nro.']
        df = df.rename(columns={"Color": "Pelaje", "Fecha Nacimiento": "Nacimiento", "Prop." : "Propietario"})
        df = df[['SBA'] + ['RP'] + ['Sexo'] + ['Nombre'] + ['Nacimiento'] + ['Pelaje'] + ['Criador'] + ['Propietario'] +
                ['Padre'] + ['Madre'] + ['PNombre'] + ['MNombre'] + ['RPPadre'] + ['RPMadre']]
        
        # Test for finding gender duplicates
        #mask = df['SBA'].duplicated(keep=False)
        #print (mask)
        #print (df[mask])
        #print (df[~mask])


        datatype = {}                           #Creating DT for SQL insertion
        for column in list(df.columns.values):
                datatype[column] = 'TEXT'

        with conn as connection:
                df.to_sql('caballos', con=connection, if_exists='append', index= False, dtype=datatype)
        conn.close()

def pdf_import(file):
        reader = PdfReader(file)
        content = []

        #File parsing and condensing 
        for page in reader.pages:
                for item in page.extract_text().splitlines():
                        content.append(item.strip())

        form_matrix, form_dict = printed_pdf(content)

        return form_matrix

def printed_pdf(content):
        def SBA_matching(content):
                for item in content:
                        if item.endswith('SBA:'):
                                return item

        def construct_progenitor_object(sex, name, info):
                #Separating grouped data
                info = info.split('|')
                id = info[1]

                info = info[2].split(' ', 1)
                #hair = info[1]

                info = info[0].split(':')
                tag = info[1]

                progenitor_object = {
                        sex : name,
                        #'Pelaje' : hair,
                        'RP' : tag,
                        'SBA' : id
                }
                return progenitor_object

        #Matching content for data
        id_str = SBA_matching(content)
        id_prefix = id_str.strip().split(" ")[0]

        name = content.index('Nombre del Producto:') + 1              
        id = content.index(id_str) + 1
        sex = content.index('SEXO:') + 1
        birth = content.index('Fecha de Nacimiento:') + 2
        hair = birth - 3
        tag = content.index('Tatuaje:') + 1
        establishment = content.index('Criador:') + 1
        owner = content.index('Propietario:') + 1

        # Handling Male/Female identical ID
        sex_str = content[sex]
        id_str = content[id]
        if len(sex_str) > 5 and not id_str.startswith('0'):
                id_str = '0' + id_str
        
        # Matrix replication for data visualization
        horse_from_pdf = [{
                        'Nombre' : content[name],
                        'SBA' : id_prefix + '-' + id_str
                        },
                        {
                        'Sexo' : sex_str,
                        'Pelaje' : content[hair],
                        'Nacimiento' : content[birth].replace('/', '-'),
                        'RP' : content[tag]
                        },
                        {
                        'Criador' : content[establishment],
                        'Propietario' : content[owner]
                        }]

        #Parent matching by reconstructing horse object
        horse_full_format = '{}|{}|{}|{}'.format(id_prefix, content[id], horse_from_pdf[1]['RP'], horse_from_pdf[1]['Pelaje'])
        father_name = content[content.index(horse_full_format) - 7]
        father_info = content[content.index(horse_full_format) - 6]
        mother_name = content[content.index(horse_full_format) - 5]
        mother_info = content[content.index(horse_full_format) - 4]

        father_object = construct_progenitor_object('Padre', father_name, father_info)
        mother_object = construct_progenitor_object('Madre', mother_name, mother_info)

        form_matrix = [*horse_from_pdf, father_object, mother_object] # Matrix format replicated
                
        form_dict = {}
        for d in horse_from_pdf:
                form_dict.update(d)
        form_dict['Padre'] = father_object['SBA']
        form_dict['Madre'] = mother_object['SBA']

        return form_matrix,form_dict

def prepared_query(string_query, values):
        conn, c = db_connect()
        request = pd.read_sql_query(string_query, conn, params=values)
        conn.close()
        return request

def combobox_query(string):
        conn, c = db_connect()        
        c.row_factory = lambda cursor, row: row[0]

        if string == 'Prefijo':
                request = c.execute('''SELECT name FROM(
                                SELECT SUBSTR(Nombre, 1, INSTR(Nombre, ' ') - 1) AS name, COUNT(*) AS unique_count FROM caballos
                                WHERE Nombre IS NOT NULL
                                GROUP BY SUBSTR(Nombre, 1, INSTR(Nombre, ' ') - 1)
                                ORDER BY Nombre ASC
                                )WHERE unique_count > 1''').fetchall() 
        else:                        
                request = c.execute(f'''SELECT DISTINCT {string} FROM caballos
                                        WHERE {string} IS NOT NULL
                                        ORDER BY {string} ASC''').fetchall()
        if string == 'Criador' or string == 'Propietario':
                request.sort(key= lambda item: int(item))
        conn.close()
        return request

def prog_query(id):
        conn, c = db_connect()
        query_string = 'SELECT * FROM caballos WHERE CAST(SUBSTR(SBA, INSTR(SBA, "-") + 1) AS INTEGER) = ?'
        request = pd.read_sql_query(query_string, conn, params=(id,))
        conn.close()
        return request

create_table()

example = ['test/xlsx/0-40k.xlsx', 'test/xlsx/40-65.xlsx', 'test/xlsx/65+.xlsx']
#xlsx_import(example)