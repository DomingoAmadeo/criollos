from tkinter import ttk

class Dateentry(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master, style='Date.TFrame')

        vcmd = (self.register(self.onValidate), '%i', '%S', '%W')

        self.day = ttk.Entry(self, width=2, validate="key", validatecommand=vcmd, style='Date.TEntry')
        self.slash_1 = ttk.Label(self, text='/', style='Date.TLabel')
        self.month = ttk.Entry(self, width=2, validate="key", validatecommand=vcmd, style='Date.TEntry')
        self.slash_2 = ttk.Label(self, text='/', style='Date.TLabel')
        self.year = ttk.Entry(self, width=4, validate="key", validatecommand=vcmd, style='Date.TEntry')

        self.entries = []
        for child in self.winfo_children():
            child.pack(side='left', padx=1,pady=1)
            if child.winfo_class() == 'TEntry':
                self.entries.append(child)

    def onValidate(self, i, S, W):
        if S.isdecimal():
            current_entry = self.nametowidget(W)
            next_index = self.entries.index(current_entry) + 1
            next_entry = self.entries[next_index] if next_index < len(self.entries) else None
            if current_entry['width'] == int(i) + 1 and next_entry is not None:
                next_entry.focus()
            return True
        else:
            return False

    def get(self):
        data = ''
        for entry in self.entries:
            val = entry.get()
            if val:
                data = val + data
            else:
                data =  '0' * entry['width'] + data
        if data == '00000000':
            data = ''
        return data

    def delete(self, start, finish):
        for entry in self.entries:
            entry.delete(start, finish)