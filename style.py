def entry_readonly_style(app_style):
    fieldbg = app_style.lookup("TEntry", 'fieldbackground',('!readonly','!disabled'))
    disabledfbg = app_style.lookup("TEntry", 'fieldbackground',('!readonly','disabled'))
    app_style.map('TEntry',
            fieldbackground=[('readonly', fieldbg), ('disabled', disabledfbg)])

def combobox_readonly_style(app_style):
    fieldbg = app_style.lookup("TEntry", 'fieldbackground',('!readonly','!disabled'))
    disabledfbg = app_style.lookup("TEntry", 'fieldbackground',('!readonly','disabled'))
    app_style.map('TCombobox',
            fieldbackground=[('readonly', fieldbg), ('disabled', disabledfbg)])

def date_widget(app_style):
    fieldbg = app_style.lookup("TEntry", 'fieldbackground',('!readonly','!disabled'))
    app_style.configure('Date.TFrame', background=fieldbg, borderwidth='1', relief='sunken')
    app_style.configure('Date.TEntry', background=fieldbg, borderwidth='0', relief='flat')
    app_style.configure('Date.TLabel', background=fieldbg, borderwidth='0', relief='flat')

def apply(app_style):
    entry_readonly_style(app_style)
    combobox_readonly_style(app_style)
    date_widget(app_style)