import tkinter as tk
from tkinter import *
from tkinter import ttk
import json
from pathlib import Path
import io
from contextlib import redirect_stdout
import threading
from assign_referrals import assign_referrals
from ReferralManager import ReferralManager

class ReferralManagerToolkit:

    def __init__(self):
        self.run_app()

    def read_settings(self):
        with open(Path(__file__).with_name('settings.json')) as f:
            try:
                settings = json.load(f)
            except:
                settings = dict()
                settings['username'] = ''
                settings['password'] = ''
                settings['sec_email'] = ''
                settings['mission_id'] = 0
            

        self.username = StringVar(value=settings['username'])
        self.password = StringVar(value=settings['password'])
        self.sec_email = StringVar(value=settings['sec_email'])
        self.mission_id = StringVar(value=settings['mission_id'])

    def save_settings(self):
        with open(Path(__file__).with_name('settings.json'), 'w') as f:
            settings = {
                'username': self.username.get(),
                'password': self.password.get(),
                'sec_email': self.sec_email.get(),
                'mission_id': self.mission_id.get()
            }
            f.write(json.dumps(settings))
            f.flush()
    
    def assign_referrals(self):
        output = io.StringIO()
        with redirect_stdout(output):
            thread = threading.Thread(assign_referrals(ReferralManager(self.username.get(), self.password.get(), self.sec_email.get(), int(self.mission_id.get()))))
            thread.start()
            while thread.is_alive():
                self.output_text_box.insert(END, output.getvalue())
            
    
    def run_app(self):
        # root window
        root = tk.Tk()
        root.geometry('600x400')
        root.title('Ferramentas do Gerenciador de Referências')

        self.read_settings()

        # create a notebook
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", pady=10, expand=True)

        # create frames
        designate_referrals_frame = ttk.Frame(notebook)
        ttk.Button(designate_referrals_frame, text='Começa', command=self.assign_referrals).pack(expand=True)
        label_frame = ttk.Labelframe(designate_referrals_frame, text='Output')
        scrollbar = ttk.Scrollbar(label_frame)
        scrollbar.pack(side=RIGHT, fill="both")
        self.output_text_box = Text(label_frame)
        self.output_text_box.pack(side=LEFT, fill="both", expand=True)
        self.output_text_box.config(yscrollcommand=scrollbar.set)
        label_frame.pack(fill="both", expand=True)

        self.output_text_box.config(state='disabled')


        frame2 = ttk.Frame(notebook)

        settings_frame = ttk.Frame(notebook)
        form_frame = ttk.Frame(settings_frame)

        username_entry = ttk.Entry(form_frame, width=40, textvariable=self.username)
        username_entry.grid(column=2, row=1, padx=10)
        ttk.Label(form_frame, text="Usário (churchofjesuschrist.org):").grid(column=1, row=1, sticky=W)

        password_entry = ttk.Entry(form_frame, width=40, textvariable=self.password)
        password_entry.grid(column=2, row=2, padx=10)
        ttk.Label(form_frame, text="Senha (churchofjesuschrist.org):").grid(column=1, row=2, sticky=W)

        sec_email_entry = ttk.Entry(form_frame, width=40, textvariable=self.sec_email)
        sec_email_entry.grid(column=2, row=3, padx=10)
        ttk.Label(form_frame, text="Email Missionário (Sec de Mídia):").grid(column=1, row=3, sticky=W)

        mission_id_entry = ttk.Entry(form_frame, width=10, textvariable=self.mission_id)
        mission_id_entry.grid(column=2, row=4, sticky=W, padx=10)
        ttk.Label(form_frame, text="ID da Missão:").grid(column=1, row=4, sticky=W)

        submit_button = ttk.Button(form_frame, text="Salvar", command=self.save_settings)
        submit_button.grid(column=2, row=5, sticky=E)

        form_frame.pack(expand=True)


        designate_referrals_frame.pack(fill='both', expand=True)
        frame2.pack(fill='both', expand=True)
        settings_frame.pack(fill='both', expand=True)

        # add frames to notebook

        notebook.add(designate_referrals_frame, text='Designar Referências')
        notebook.add(frame2, text='Parar de Ensinar')
        notebook.add(settings_frame, text='Configurações')

        root.mainloop()

    

ReferralManagerToolkit()