import json
import datetime
import tkinter as tk
import zipfile
from pathlib import Path
from shutil import copyfile, rmtree
from tkinter import filedialog, messagebox, ttk



class Config:

    def __init__(self, f, defaultconfig):
        self.Path = Path.joinpath(Path.cwd(), f)

        if Path.is_file(self.Path):
            with open(self.Path, 'r', encoding='utf-8') as f:
                self.Data = json.load(f)
        else:
            self.Data = defaultconfig
            self.save_config()

    def save_config(self):
        with open(self.Path, 'w', encoding='utf-8') as f:
            json.dump(self.Data, f, indent=4)


class SnowSave:

    def __init__(self, root):

        # Load configs
        self.config_app = Config('config.json', {"save_dir": None, })
        self.config_bot = Config('bot.json', {})

        # Setup main window
        root.title("Snow Save")

        s = ttk.Style()
        s.configure('Large.TButton', font='helvetica 18', padding=5)
        mainframe = ttk.Frame(root, padding="3 3 12 12",
                              borderwidth=2, relief='raised')
        mainframe.grid(column=0, row=0, sticky='news')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.button_ids = []

        btn_import = ttk.Button(
            mainframe, text="Import Save", command=self.import_save, style='Large.TButton')
        btn_import.grid(column=0, row=0)
        self.button_ids.append(btn_import)

        btn_export = ttk.Button(
            mainframe, text="Export Save", command=self.export_save, style='Large.TButton')
        btn_export.grid(column=1, row=0)
        self.button_ids.append(btn_export)

        btn_manual_import = ttk.Button(
            mainframe, text="Manual Import", command=self.manual_import)
        btn_manual_import.grid(column=0, row=1)
        self.button_ids.append(btn_manual_import)

        btn_manual_export = ttk.Button(
            mainframe, text="Manual Export", command=self.manual_export)
        btn_manual_export.grid(column=1, row=1)
        self.button_ids.append(btn_manual_export)

        self.progress = ttk.Progressbar(
            mainframe, length=300, mode='determinate')
        self.progress.grid(column=0, row=2, columnspan=2, sticky='we')

        mainframe.rowconfigure(0, weight=3)
        mainframe.rowconfigure(1, weight=1)
        mainframe.rowconfigure(2, weight=1)
        mainframe.columnconfigure(0, weight=1)
        mainframe.columnconfigure(1, weight=1)

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def select_slot_dialog(self, data, message):
        selected_slot = None

        def dismiss(arg):
            nonlocal selected_slot
            selected_slot = arg
            dlg.grab_release()
            dlg.destroy()

        def format_data(slot):
            try:
                trucks = ""
                for t in data[slot]['ownedTrucks'].keys():
                    trucks += t.replace('_', ' ') + "\n"
                return "Rank: {}\nMoney: {}\nOwned Trucks:\n{}".format(data[slot]['rank'], data[slot]['money'], trucks)
            except:
                return ""

        dlg = tk.Toplevel(root)
        dlg.title = message
        b = ttk.Button(dlg, text="Slot 1", command=lambda: dismiss(
            1), style='Large.TButton')
        b.state(['disabled'] if not data['CompleteSave'] else ['!disabled'])
        b.grid(column=0, row=0, sticky='news')
        b = ttk.Button(dlg, text="Slot 2", command=lambda: dismiss(
            2), style='Large.TButton')
        b.state(['disabled'] if not data['CompleteSave1'] else ['!disabled'])
        b.grid(column=1, row=0, sticky='news')
        b = ttk.Button(dlg, text="Slot 3", command=lambda: dismiss(
            3), style='Large.TButton')
        b.state(['disabled'] if not data['CompleteSave2'] else ['!disabled'])
        b.grid(column=2, row=0, sticky='news')
        b = ttk.Button(dlg, text="Slot 4", command=lambda: dismiss(
            4), style='Large.TButton')
        b.state(['disabled'] if not data['CompleteSave3'] else ['!disabled'])
        b.grid(column=3, row=0, sticky='news')

        ttk.Label(dlg, text=format_data('CompleteSave')
                  ).grid(column=0, row=1, sticky='n')
        ttk.Label(dlg, text=format_data('CompleteSave1')
                  ).grid(column=1, row=1, sticky='n')
        ttk.Label(dlg, text=format_data('CompleteSave2')
                  ).grid(column=2, row=1, sticky='n')
        ttk.Label(dlg, text=format_data('CompleteSave3')
                  ).grid(column=3, row=1, sticky='n')

        dlg.columnconfigure(0, weight=2)
        dlg.columnconfigure(1, weight=2)
        dlg.columnconfigure(2, weight=2)
        dlg.columnconfigure(3, weight=2)

        dlg.rowconfigure(0, weight=4)
        dlg.rowconfigure(1, weight=1)

        for child in dlg.winfo_children():
            child.grid_configure(padx=10, pady=10)

        dlg.protocol("WM_DELETE_WINDOW", lambda: dismiss(-1))
        dlg.transient(root)
        dlg.wait_visibility()
        dlg.grab_set()
        dlg.wait_window()

        return selected_slot

    def disable_buttons(self):
        for b in self.button_ids:
            b.state(['disabled'])

    def enable_buttons(self):
        for b in self.button_ids:
            b.state(['!disabled'])

    def get_local_save_path(self):
        if not self.config_app.Data['save_dir']:
            local_p = Path.joinpath(
                Path.home(), "Documents", "My Games", "SnowRunner")
            if not Path.is_dir(local_p):  # Check default path
                messagebox.showwarning(
                    message="Cannot find save folder. Please browse to your SnowRunner folder.", title="Folder not found")
                dir = filedialog.askdirectory()
                if not dir:
                    return None  # Exit
                local_p = dir
            else:
                r = messagebox.askyesno(message="Found save folder at {}".format(
                    local_p), detail="Is this correct?", title="Found save folder")
                if not r:
                    dir = filedialog.askdirectory()
                    if not dir:
                        return None
                    local_p = dir

            self.config_app.Data['save_dir'] = str(local_p)
            self.config_app.save_config()

        return Path.joinpath(Path(self.config_app.Data['save_dir']), "base", "storage")

    def import_save(self):
        return

    def manual_import(self):
        try:
            self.disable_buttons()
            import_path = filedialog.askopenfilename(filetypes=[("Zip Files", ".zip")], title="Select zip to import")
            if import_path == '':
                raise ValueError("Cancelled by user")
            self.__import_files(Path(import_path))
            messagebox.showinfo(
                message="Import sucessful.")
        except ValueError as e:
            messagebox.showerror(message=format(e))        
        finally:
            self.enable_buttons()

    def __import_files(self, p):
        import_path = Path.joinpath(Path.cwd(), "import")
        if not Path.exists(import_path):
            Path.mkdir(import_path)

        temp_path = Path.joinpath(Path.cwd(), p.stem)
        if Path.exists(temp_path):
            rmtree(temp_path)
        Path.mkdir(temp_path)

        with zipfile.ZipFile(p, mode='r') as archive:
            archive.extractall(temp_path)

        save_path = self.get_local_save_path()
        if save_path == None:
            raise ValueError("Cancelled by user")
        
        save_users = [x for x in save_path.iterdir() if x.is_dir()
                                           and not 'backup' in x.name]
        if not len(save_users):
            raise ValueError("No saves found.")
        elif len(save_users) > 1:
            # TODO: Make selection window
            raise ValueError("Multiple save folders found.")

        save_path = save_users[0]

        data = self.__get_slot_data(save_path)
        r = self.select_slot_dialog(data, "Select Slot to import to")
        if r == -1:
            raise ValueError("Cancelled by user")
        if r == 1:
            import_slot_name = "CompleteSave"
        elif r == 2:
            import_slot_name = "CompleteSave1"
        elif r == 3:
            import_slot_name = "CompleteSave2"
        elif r == 4:
            import_slot_name = "CompleteSave3"
        
        #Merge save data
        import_save_file = [f for f in temp_path.iterdir() if f.is_file() and 'CompleteSave' in f.stem][0]
        local_save_file = [f for f in save_path.iterdir() if f.is_file() and import_slot_name == f.stem][0]

        with open(import_save_file) as f:
            text = f.read()
            end_char = text[-1]
            import_json = json.loads(text[:-1])
        
        with open(local_save_file) as f:
            text = f.read()
            local_json = json.loads(text[:-1])
        keys = ['gameDifficultyMode', 'metricSystem', 'saveId', 'isHardMode', 'gameStat', 'gameStatByRegion', 'trackedObjective']
        for i in keys:
            import_json[import_save_file.stem]['SslValue'][i] = local_json[local_save_file.stem]['SslValue'][i]
        
        for k, v in import_json[import_save_file.stem]['SslValue']['garagesData'].items():
            if k in local_json[local_save_file.stem]['SslValue']['garagesData'].keys(): # Garage exists in both saves
                import_json[import_save_file.stem]['SslValue']['garagesData'][k] = local_json[local_save_file.stem]['SslValue']['garagesData'][k]
            else: # Garage not in local
                default = dict(
                    selectedSlot="garage_interior_slot_1",
                    slotsDatas=dict(
                        garage_interior_slot_1=dict(
                            garageSlotZoneId="garage_interior_slot_1",
                            truckDesc=None
                        ),
                        garage_interior_slot_2=dict(
                            garageSlotZoneId="garage_interior_slot_2",
                            truckDesc=None
                        ),
                        garage_interior_slot_3=dict(
                            garageSlotZoneId="garage_interior_slot_3",
                            truckDesc=None
                        ),
                        garage_interior_slot_4=dict(
                            garageSlotZoneId="garage_interior_slot_4",
                            truckDesc=None
                        ),
                        garage_interior_slot_5=dict(
                            garageSlotZoneId="garage_interior_slot_5",
                            truckDesc=None
                        ),
                        garage_interior_slot_6=dict(
                            garageSlotZoneId="garage_interior_slot_6",
                            truckDesc=None
                        ),      
                    )
                )
                import_json[import_save_file.stem]['SslValue']['garagesData'][k] = default
        
        # Copy persistent data
        for k, v in local_json[local_save_file.stem]['SslValue']['persistentProfileData'].items():
            if k != "discoveredTrucks" or "discoveredUpgrades" or "unlockeditemNames" or "knownRegions":
                import_json[import_save_file.stem]['SslValue']['persistentProfileData'][k] = v
            else: # merge
                for i, val in local_json[local_save_file.stem]['SslValue']['persistentProfileData'][k].items():
                    if val and not import_json[import_save_file.stem]['SslValue']['persistentProfileData'][k][i]:
                        import_json[import_save_file.stem]['Sslvalue']['persistentProfileData'][k][i] = val
        
        import_json[local_save_file.stem] = import_json.pop(import_save_file.stem)
        
        #Rename all levels
        import_slot = import_save_file.stem.removeprefix("CompleteSave")
        local_slot = local_save_file.stem.removeprefix("CompleteSave")

        if import_slot != local_slot:
            if import_slot == '': #Just add slot
                for f in temp_path.iterdir():
                    if not "achievement" in f.name or not "CompleteSave" in f.name:
                        f.replace(Path.joinpath(temp_path, local_slot + "_" + f.name))
            elif local_slot == '': #Just trim slot
                for f in temp_path.iterdir():
                    if not "achievement" in f.name and not "CompleteSave" in f.name:
                        f.replace(Path.joinpath(temp_path, f.name[2:]))
            else: #Change slot
                for f in temp_path.iterdir():
                    if not "achievement" in f.name or not "CompleteSave" in f.name:
                        f.replace(Path.joinpath(temp_path, local_slot + f.name[1:]))


        #Remove import save file
        import_save_file.unlink()

        new_import_save_file = Path.joinpath(import_save_file.parent, local_save_file.name)

        #Write save
        with open(new_import_save_file, 'w') as f:
            json.dump(import_json, f)
            f.write(end_char)



        #Backup original save
        self.__backup(save_path)

        #Copy everything
        for f in temp_path.iterdir():
            f.replace(Path.joinpath(save_path, f.name))

    def export_save(self):
        return

    def manual_export(self):
        try:
            self.disable_buttons()
            save_path = self.get_local_save_path()
            if save_path == None:
                raise ValueError("Cancelled by user")
            r = self.__save_files(save_path)
            messagebox.showinfo(
                message="Export sucessful.\n File saved at {}".format(r))
        except ValueError as e:
            messagebox.showerror(message=format(e))
        finally:
            self.enable_buttons()

    def __get_slot_data(self, save_path):
        # Choose save slot
        slot_files = [f for f in save_path.iterdir() if f.is_file()
                                                   and 'CompleteSave' in f.name]

        save_slot_name = ""
        data = {"CompleteSave": {}, "CompleteSave1": {},
                "CompleteSave2": {}, "CompleteSave3": {}}
        for f in slot_files:
            with open(f, 'r') as file:
                text = file.read()
                save_data = json.loads(text[:-1])
                key = f.stem
                try:
                    data[key]['ownedTrucks'] = save_data[key]['SslValue']['persistentProfileData']['ownedTrucks']                    
                except:
                    data[key]['ownedTrucks'] = []

                try:
                    data[key]['money'] = save_data[key]['SslValue']['persistentProfileData']['money']
                except:
                    data[key]['money'] = 0
                try:
                    data[key]['rank'] = save_data[key]['SslValue']['persistentProfileData']['rank']
                except:
                    data[key]['rank'] = 0
        return data

    def __backup(self, save_path):
        backup_path = Path.joinpath(Path.cwd(), "backup")
        if not Path.exists(backup_path):
            Path.mkdir(backup_path)

        zip_file = Path.joinpath(backup_path, "backup_" + str(datetime.datetime.now()) + ".zip")
        with zipfile.ZipFile(zip_file, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            for f in save_path.iterdir():
                archive.write(f, arcname=f.name)

    def __save_files(self, p):
        save_users = [x for x in p.iterdir() if x.is_dir()
                                           and not 'backup' in x.name]
        if not len(save_users):
            raise ValueError("No saves found.")
        elif len(save_users) > 1:
            # TODO: Make selection window
            raise ValueError("Multiple save folders found.")

        save_path = save_users[0]
        slot_files = [f for f in save_path.iterdir() if f.is_file() and 'CompleteSave' in f.name]
        if len(slot_files) > 1:
            data = self.__get_slot_data(save_path)
            r = self.select_slot_dialog(data, "Select Slot to export")
            if r == -1:
                raise ValueError("Cancelled by user")
            if r == 1:
                save_slot_name = "CompleteSave"
            elif r == 2:
                save_slot_name = "CompleteSave1"
            elif r == 3:
                save_slot_name = "CompleteSave2"
            elif r == 4:
                save_slot_name = "CompleteSave3"
        elif len(slot_files) == 1:
            save_slot_name = slot_files[0].stem
        else:
            raise ValueError("No save files found.")

        sid = save_slot_name.removeprefix("CompleteSave")
        files_to_save = []
        for f in save_path.iterdir():
            if f.stem == save_slot_name or 'achievements' in f.name:
                files_to_save.append(f)
            elif 'level' in f.name:
                if sid == "" and not f.name.startswith(('1', '2', '3')):
                    files_to_save.append(f)
                elif sid != "" and f.name.startswith(sid):
                    files_to_save.append(f)

        temp_path = Path.joinpath(Path.cwd(), save_slot_name)
        if Path.exists(temp_path):
            rmtree(temp_path)
        Path.mkdir(temp_path)

        for f in files_to_save:
            copyfile(f, Path.joinpath(temp_path, f.name))

        export_path = Path.joinpath(Path.cwd(), "export")
        if not Path.exists(export_path):
            Path.mkdir(export_path)

        zip_file = Path.joinpath(export_path, save_slot_name + ".zip")
        with zipfile.ZipFile(zip_file, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            for f in temp_path.iterdir():
                archive.write(f, arcname=f.name)

        # clean up
        rmtree(temp_path)
        return zip_file


root = tk.Tk()
SnowSave(root)
root.mainloop()
