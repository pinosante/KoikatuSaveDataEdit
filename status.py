import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename

from resource import Resource as RM

class StatusPanel(ttk.Frame):
    def __init__(self, parent, chara, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        row = 0
        label = ttk.Label(self, text=RM.res('feeling'))
        self._feeling = tk.StringVar(value=f'{chara.feeling}')
        entry = ttk.Entry(self, textvariable=self._feeling)
        label.grid(row=row, column=0, sticky='E')
        entry.grid(row=row, column=1, sticky='W')

        values = RM.res('relations')
        label = ttk.Label(self, text=RM.res('relation'))
        self._relation = tk.StringVar(value=values[chara.lover])
        combobox = ttk.Combobox(self, values=values,
                                textvariable=self._relation, state='readonly')
        label.grid(row=row, column=2, sticky='E')
        combobox.grid(row=row, column=3, sticky='W')

        row = 1
        label = ttk.Label(self, text=RM.res('m_love'))
        self._m_love = tk.StringVar(value=f'{chara.m_love}')
        entry = ttk.Entry(self, textvariable=self._m_love)
        label.grid(row=row, column=0, sticky='E')
        entry.grid(row=row, column=1, sticky='W')

        label = ttk.Label(self, text=RM.res('h_count'))
        self._h_count = tk.StringVar(value=f'{chara.h_count}')
        entry = ttk.Entry(self, textvariable=self._h_count)
        label.grid(row=row, column=2, sticky='E')
        entry.grid(row=row, column=3, sticky='W')
        
        row = 2
        values = RM.res('koikatu')
        label = ttk.Label(self, text=RM.res('club'))
        self._koikatu = tk.StringVar(value=values[chara.koikatu])
        combobox = ttk.Combobox(self, values=values,
                                textvariable=self._koikatu, state='readonly')
        label.grid(row=row, column=0, sticky='E')
        combobox.grid(row=row, column=1, sticky='W')


        values = RM.res('dates')
        label = ttk.Label(self, text=RM.res('date'))
        self._date = tk.StringVar(value=values[chara.date])
        combobox = ttk.Combobox(self, values=values,
                                textvariable=self._date, state='readonly')
        label.grid(row=row, column=2, sticky='E')
        combobox.grid(row=row, column=3, sticky='W')

    @property
    def feeling(self):
        return int(self._feeling.get())

    @property
    def m_love(self):
        return int(self._m_love.get())

    @property
    def h_count(self):
        return int(self._h_count.get())

    @property
    def relation(self):
        values = RM.res('relations')
        return values.index(self._relation.get())

    @property
    def koikatu(self):
        values = RM.res('koikatu')
        return values.index(self._koikatu.get())

    @property
    def date(self):
        values = RM.res('dates')
        return values.index(self._date.get())
