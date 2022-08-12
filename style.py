def entry_readonly_style(app_style):
    fieldbg = app_style.lookup("TEntry", 'fieldbackground',('!readonly','!disabled'))
    disabledfbg = app_style.lookup("TEntry", 'fieldbackground',('!readonly','disabled'))
    app_style.map('TEntry',
            fieldbackground=[('readonly', fieldbg), ('disabled', disabledfbg)])

def apply(app_style):
    entry_readonly_style(app_style)
