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
        lover = self._get_value(values, chara.lover)
        label = ttk.Label(self, text=RM.res('relation'))
        self._relation = tk.StringVar(value=lover)
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
        koikatu = self._get_value(values, chara.koikatu)
        label = ttk.Label(self, text=RM.res('club'))
        self._koikatu = tk.StringVar(value=koikatu)
        combobox = ttk.Combobox(self, values=values,
                                textvariable=self._koikatu, state='readonly')
        label.grid(row=row, column=0, sticky='E')
        combobox.grid(row=row, column=1, sticky='W')

        values = RM.res('dates')
        date = self._get_value(values, chara.date)
        label = ttk.Label(self, text=RM.res('date'))
        self._date = tk.StringVar(value=date)
        combobox = ttk.Combobox(self, values=values,
                                textvariable=self._date, state='readonly')
        label.grid(row=row, column=2, sticky='E')
        combobox.grid(row=row, column=3, sticky='W')

        self._ac = {}
        row = 3
        label, cb = self._make_ac(chara, 'mune')
        label.grid(row=row, column=0, sticky='E')
        cb.grid(row=row, column=1, sticky='W')

        label, cb = self._make_ac(chara, 'kokan')
        label.grid(row=row, column=2, sticky='E')
        cb.grid(row=row, column=3, sticky='W')

        row = 4
        label, cb = self._make_ac(chara, 'anal')
        label.grid(row=row, column=0, sticky='E')
        cb.grid(row=row, column=1, sticky='W')

        label, cb = self._make_ac(chara, 'siri')
        label.grid(row=row, column=2, sticky='E')
        cb.grid(row=row, column=3, sticky='W')

        row = 5
        label, cb = self._make_ac(chara, 'tikubi')
        label.grid(row=row, column=0, sticky='E')
        cb.grid(row=row, column=1, sticky='W')

        label, cb = self._make_ac(chara, 'kokan_piston')
        label.grid(row=row, column=2, sticky='E')
        cb.grid(row=row, column=3, sticky='W')

        row = 6
        label, cb = self._make_ac(chara, 'anal_piston')
        label.grid(row=row, column=0, sticky='E')
        cb.grid(row=row, column=1, sticky='W')

        label, cb = self._make_ac(chara, 'houshi')
        label.grid(row=row, column=2, sticky='E')
        cb.grid(row=row, column=3, sticky='W')


    def _make_ac(self, chara, name):
        values = RM.res('ac')
        label = ttk.Label(self, text=RM.res(name))
        i = chara.get_ac(name)
        value = self._get_value(values, i)
        self._ac[name] = tk.StringVar(value=value)
        combobox = ttk.Combobox(self, values=values,
                                textvariable=self._ac[name], state='readonly')
        return (label, combobox)

    def _get_value(self, values, index):
        return values[index] if len(values) > index else values[0]


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

    def ac(self, name):
        values = RM.res('ac')
        return values.index(self._ac[name].get())
