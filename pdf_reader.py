import tkinter as tk
from tkinter import ttk
import criollos_GUI as cGUI
import criollos_graphic_resources as cgr
import style
from table_logic import selector_query


root = tk.Tk()

root.geometry('500x350')
root.title('Criollos')
#root.iconbitmap()
root.resizable(False, False)
root.option_add('*tearOff', 'false')

app_style = ttk.Style()
app_style.theme_use('default')          # alt clam classic default
style.apply(app_style)                  # Apply style modifications
cgr.GUI()                               # Initialize graphic resources

# Create tab division
def window_size_manager(event : tk.Event):
    # Notebook and size
    ntbk = event.widget
    ntbk_width = ntbk.winfo_reqwidth() - max([x.winfo_reqwidth() for x in ntbk.winfo_children()])
    ntbk_height = ntbk.winfo_reqheight() - max([x.winfo_reqheight() for x in ntbk.winfo_children()])
    # Current tab through name
    tab_name = ntbk.select()
    tab = ntbk.nametowidget(tab_name)
    # Resize app with tab + notebook size
    ntbk.winfo_toplevel().geometry(f'{tab.winfo_reqwidth() + ntbk_width}x{tab.winfo_reqheight() + ntbk_height}')
notebook_widget = ttk.Notebook(root, takefocus=False)
notebook_widget.pack(fill='both', expand=True)
notebook_widget.bind('<<NotebookTabChanged>>', window_size_manager)

# Home Tab
home_tab = ttk.Frame(notebook_widget)
home_tab.pack(fill='both', expand=True)
reference_selector = ttk.Combobox(home_tab)
reference_selector['values'] = ['SBA', 'RP', 'Nombre']
reference_selector.insert(0, 'Seleccione una opcion')
reference_selector.state(('readonly',))
reference_selector.pack(padx=(50,0), pady=75, side='left', expand=True)
entry_selector = ttk.Entry(home_tab)
entry_selector.pack(padx=10, pady=75, side='left', expand=True)
button_selector = ttk.Button(home_tab, text='Buscar', command= lambda: selector_query(reference_selector.get(), entry_selector.get(), root))
button_selector.pack(padx=(0,50), pady=75,  side='left', expand=True)
notebook_widget.add(home_tab, text= 'Inicio')

# Detailed tab
detailed_tab = ttk.Frame(notebook_widget)
detailed_tab.pack(fill='both', expand=True)
cGUI.populate_detailed_tab(detailed_tab)
notebook_widget.add(detailed_tab, text= 'Vista detallada')

# Table tab
table_tab = ttk.Frame(notebook_widget)
table_tab.pack(fill='both')
cGUI.populate_table_tab(table_tab)
notebook_widget.add(table_tab, text='Registros')

# Ancestry tab
ancestry_tab = ttk.Frame(notebook_widget, height='600', width='1100')
ancestry_tab.pack(expand= True, fill= 'both')
ancestry_tab.pack_propagate(0)
bgcolor = app_style.lookup('TFrame', 'background')
cGUI.populate_ancestry_tab(ancestry_tab, bgcolor)
notebook_widget.add(ancestry_tab, text='Genealógico')

root.update_idletasks()

#notebook_widget.select(1)
#root.bind('<Button-1>', lambda e: print(e.widget))

root.mainloop()