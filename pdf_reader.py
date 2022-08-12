import tkinter as tk
from tkinter import ttk
import criollos_GUI as cGUI
import style


root = tk.Tk()

root.geometry('500x350')
root.title('Criollos')
#root.iconbitmap()
root.resizable(False, False)
root.option_add('*tearOff', 'false')

app_style = ttk.Style()
app_style.theme_use('default')          # alt clam classic default
style.apply(app_style)                  # Apply style modifications

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

root.update_idletasks()

root.mainloop()