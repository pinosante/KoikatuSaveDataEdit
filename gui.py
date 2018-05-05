#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import io
import codecs
import shutil
import sys
import traceback
from pathlib import Path

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename

from PIL import Image, ImageTk

from scframe import VerticalScrolledFrame
from character import KoikatuCharacter
from save_data import KoikatuSaveData

class Resource:
    resource = {}

    @staticmethod
    def load(filename):
        with codecs.open(filename, 'r', 'utf-8') as jsonfile:
             Resource.resource = json.load(jsonfile)

    @staticmethod
    def res(key):
        return Resource.resource[key] if key in Resource.resource else key

RM = Resource


class PropertyPanel(ttk.Frame):

    def __init__(self, parent, character, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.character = character

        label1 = ttk.Label(self, text=RM.res('lastname'))
        self._lastname = tk.StringVar(value=character.lastname)
        entry1 = ttk.Entry(self, textvariable=self._lastname)
        label1.grid(row=0, column=0, sticky='E', columnspan=1)
        entry1.grid(row=0, column=1, sticky='W', columnspan=1)

        label2 = ttk.Label(self, text=RM.res('firstname'))
        self._firstname = tk.StringVar(value=character.firstname)
        entry2 = ttk.Entry(self, textvariable=self._firstname)
        label2.grid(row=0, column=2, sticky='E', columnspan=1)
        entry2.grid(row=0, column=3, sticky='W', columnspan=1)

        label3 = ttk.Label(self, text=RM.res('nickname'))
        self._nickname = tk.StringVar(value=character.nickname)
        entry3 = ttk.Entry(self, textvariable=self._nickname)
        label3.grid(row=1, column=0, sticky='E', columnspan=1)
        entry3.grid(row=1, column=1, sticky='W', columnspan=1)

        values = (RM.res('male'), RM.res('female'))
        label4 = ttk.Label(self, text=RM.res('sex'))
        self._sex = tk.StringVar(value=values[character.sex])
        entry4 = ttk.Combobox(self, values=values,
                              textvariable=self._sex, state='readonly')
        label4.grid(row=1, column=2, sticky="E", columnspan=1)
        entry4.grid(row=1, column=3, sticky="W", columnspan=1)

        # answer
        self._answers = {}
        frame = ttk.LabelFrame(self, text=RM.res('answer'))
        for i, name in enumerate(character.answers.keys()):
            self._answers[name] = self._make_boolean_prop(frame,
                                                          RM.res(name),
                                                          character.answers[name], i, 5)
        frame.grid(row=2, column=0, columnspan=4, sticky='W')

        # denail
        self._denials = {}
        frame = ttk.LabelFrame(self, text=RM.res('denial'))
        for i, name in enumerate(character.denials.keys()):
            self._denials[name] = self._make_boolean_prop(frame,
                                                          RM.res(name),
                                                          character.denials[name], i, 5)
        frame.grid(row=3, column=0, columnspan=4, sticky='W')

        # attribute
        self._attributes = {}
        frame = ttk.LabelFrame(self, text=RM.res('attribute'))
        for i, name in enumerate(character.attributes.keys()):
            self._attributes[name] = self._make_boolean_prop(frame,
                                                             RM.res(name),
                                                             character.attributes[name], i, 5)
        frame.grid(row=4, column=0, columnspan=4, sticky='W')


    @property
    def firstname(self):
        return self._firstname.get()

    @property
    def lastname(self):
        return self._lastname.get()

    @property
    def nickname(self):
        return self._nickname.get()

    @property
    def sex(self):
        return [res('male'), res('female')].find(self.sex.get())

    @property
    def answers(self):
        return {key:self._answers[key].get() for key in self._answers}

    @property
    def denials(self):
        return {key:self._denials[key].get() for key in self._denials}

    @property
    def attributes(self):
        return {key:self._attributes[key].get() for key in self._attributes}

    def update_character(self, character):
        self._firstname.set(character.firstname)
        self._lastname.set(character.lastname)
        self._nickname.set(character.nickname)

        for key in self._answers:
            self._answers[key].set(character.answers[key])

        for key in self._denials:
            self._denials[key].set(character.denials[key])

        for key in self._attributes:
            self._attributes[key].set(character.attributes[key])


    def _make_boolean_prop(self, frame, name, value, i, cols):
        var = tk.BooleanVar()
        checkbox = ttk.Checkbutton(frame, text=name, variable=var)
        var.set(value)
        row = i // cols
        col = i % cols
        checkbox.grid(row=row, column=col, sticky='W')
        return var



class CharacterPanel(ttk.Frame):
    def __init__(self, app, parent, character, *args, **kwargs):
        super().__init__(parent,
                         relief='ridge',
                         *args, **kwargs)
        self.app = app
        self.parent = parent
        self._character = character
        self.dirty = False

        png = Image.open(io.BytesIO(character.png))
        self.image = ImageTk.PhotoImage(png)

        self.photo = tk.Label(self,
                              image=self.image,
                              width=self.image.width(),
                              height=self.image.height())
        self.photo.grid(row=0, column=0, rowspan=3, padx=2, pady=2)

        self.property_panel = PropertyPanel(self, character)
        self.property_panel.grid(row=0, column=1, rowspan=2, padx=2, pady=2)

        self._load_btn = ttk.Button(self,
                                    text='Load Character Card',
                                    command=self._open_dialog)
        self._load_btn.grid(row=2, column=1, sticky='W')


    @property
    def character(self):
        chara = self._character
        panel = self.property_panel
        if chara.firstname != panel.firstname:
            chara.firstname = panel.firstname
            self.dirty = True
        if chara.lastname != panel.lastname:
            chara.lastname = panel.lastname
            self.dirty = True
        if chara.nickname != panel.nickname:
            chara.nickname = panel.nickname
            self.dirty = True
        if chara.answers != self.property_panel.answers:
            chara.answers = self.property_panel.answers
            self.dirty = True
        if chara.denials != self.property_panel.denials:
            chara.denials = self.property_panel.denials
            self.dirty = True
        if chara.attributes != self.property_panel.attributes:
            chara.attributes = self.property_panel.attributes
            self.dirty = True
        return chara

    def _update_character(self, character):
        self._character.custom = character.custom
        self._character.coordinates = character.coordinates
        self._character.parameter = character.parameter
        self._character.status = character.status
        self._character.png_length = character.png_length
        self._character.png = character.png
        self.dirty = True

        png = Image.open(io.BytesIO(character.png))
        self.image = ImageTk.PhotoImage(png)
        self.photo.config(image=self.image)

        self.property_panel.update_character(self._character)

    def _open_dialog(self):
        name = askopenfilename(filetype=[("koikatu card", "*.png")],
                               initialdir=self.app.card_dir)
        if name is not None:
            with open(name, 'rb') as infile:
                chara = KoikatuCharacter(infile, True)
                self._update_character(chara)
        else:
            self.quit()


class App:
    def __init__(self, root, filename, out_filename):
        self.root = root
        self.filename = filename
        self.out_filename = out_filename
        self.save_data = KoikatuSaveData(filename)
        self.card_dir = Path.cwd()

        style = ttk.Style()
        style.configure('.', padding='2 4 2 4')

        width = 680
        height = 320 * 3 + 12
        self.root.geometry(f'{width}x{height}')

        frame = VerticalScrolledFrame(self.root)
        self.panels = []
        for chara in self.save_data.characters:
            panel = CharacterPanel(self, frame.interior, chara)
            panel.pack()
            self.panels.append(panel)
        frame.grid(row=0, column=0)

        btn_frame = ttk.Frame(self.root)
        save_btn = ttk.Button(btn_frame, text='Save & Quit', command=self.save_and_quit)
        quit_btn = ttk.Button(btn_frame, text='Quit', command=self.quit)
        quit_btn.pack(side='right', pady=2)
        save_btn.pack(side='right', pady=2)
        btn_frame.grid(row=1, column=0, pady=2, sticky='E')

        def _configure(event):
            h = 320 * 3 - 20
            frame.canvas.config(height=h)

        self.root.bind('<Configure>', _configure)


    def save(self):
        for i, panel in enumerate(self.panels):
            chara = panel.character
            if panel.dirty:
                self.save_data.replace(i, chara)
        
        if self.filename == self.out_filename:
            # create backup
            path = Path(self.filename).resolve()
            backup = path.parent / (path.stem + '.old.dat')
            shutil.copy(self.filename, backup)
        
        self.save_data.save(self.out_filename)


    def save_and_quit(self, *args):
        self.save()
        self.root.destroy()

    def quit(self, *args):
        self.root.destroy()


    def run(self):
        self.root.mainloop()



def main():
    default_resource = Path(sys.argv[0]).parent / 'resources_ja.json'

    parser = argparse.ArgumentParser()
    parser.add_argument('save_data',
                        help='koikatu save data')
    parser.add_argument('-o', dest='output',
                        help='output file')
    parser.add_argument('-r',
                        dest='resources',
                        default=default_resource,
                        help='resource file name')

    root = tk.Tk()
    root.title('Koikatu Save data editor')

    if len(sys.argv) > 1:
        args = parser.parse_args()
        save_data = args.save_data

        if args.output is not None:
            out_filename = args.output
        else:
            out_filename = args.output
        resources = args.resources
    else:
        save_data = askopenfilename(filetype=[("koikatu save data", "*.dat")],
                                    initialdir=Path.cwd())
        if save_data is None:
            sys.exit(-1)

        out_filename = save_data
        resources = default_resource

    Resource.load(resources)

    App(root, save_data, out_filename).run()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        print('push Enter key')
        input()
