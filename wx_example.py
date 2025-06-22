# -*- coding: utf-8 -*-
import wx
import wx.grid
import psycopg2
from psycopg2.extensions import register_type, UNICODE
from app import *

CONN_STR = "host='10.22.31.252' dbname='rpr24' user='sidorenko_t_v' password='c5c62a89'"

# auth_dialog.py
import wx
import hashlib
from app import print_users


class LoginDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="РђРІС‚РѕСЂРёР·Р°С†РёСЏ", size=(300, 200))

        self.InitUI()
        self.Centre()
        # РЈРґР°Р»СЏРµРј ShowModal(), РѕРЅ Р±СѓРґРµС‚ РІС‹Р·РІР°РЅ РїРѕР·Р¶Рµ

    def InitUI(self):
        panel = wx.Panel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)

        login_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.login_ctrl = wx.TextCtrl(panel)
        login_sizer.Add(wx.StaticText(panel, label="Р›РѕРіРёРЅ:"), 0, wx.ALL, 5)
        login_sizer.Add(self.login_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        pwd_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pwd_ctrl = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        pwd_sizer.Add(wx.StaticText(panel, label="РџР°СЂРѕР»СЊ:"), 0, wx.ALL, 5)
        pwd_sizer.Add(self.pwd_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(panel, label="Р’РѕР№С‚Рё")
        cancel_btn = wx.Button(panel, label="РћС‚РјРµРЅР°")

        btn_sizer.Add(ok_btn, 1, wx.ALL | wx.EXPAND, 5)
        btn_sizer.Add(cancel_btn, 1, wx.ALL | wx.EXPAND, 5)

        sizer.Add(login_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(pwd_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)

        ok_btn.Bind(wx.EVT_BUTTON, self.on_login)
        cancel_btn.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CANCEL))

        self.result = None

    def on_login(self, event):
        login = self.login_ctrl.GetValue()
        password = hashlib.sha256(self.pwd_ctrl.GetValue().encode()).hexdigest()

        users = print_users()
        for user in users:
            if user[0] == login and user[1] == password:
                self.result = True
                break

        # Р—Р°РєСЂС‹РІР°РµРј РґРёР°Р»РѕРі РїРѕСЃР»Рµ СѓСЃРїРµС€РЅРѕР№ РїСЂРѕРІРµСЂРєРё
        self.EndModal(wx.ID_OK)

    def get_result(self):
        return self.result


class DatabaseFrame(wx.Frame):
    def __init__(self, parent, id):
        super().__init__(parent, id, 'РЈС‡СЂРµР¶РґРµРЅРёРµ Р“РР‘Р”Р”', size=(1000, 600),
                         style=wx.DEFAULT_FRAME_STYLE)

        # РЎРѕР·РґР°С‘Рј РґРёР°Р»РѕРі Р°РІС‚РѕСЂРёР·Р°С†РёРё
        login_dialog = LoginDialog(self)
        result = login_dialog.ShowModal()  # Р’Р°Р¶РЅРѕ: РёСЃРїРѕР»СЊР·СѓРµРј ShowModal() Р·РґРµСЃСЊ

        if result != wx.ID_OK:
            self.Destroy()
            return

        # РћСЃС‚Р°Р»СЊРЅРѕР№ РєРѕРґ СЃРѕР·РґР°РЅРёСЏ РёРЅС‚РµСЂС„РµР№СЃР°
        self.notebook = wx.Notebook(self)

        # Р’РєР»Р°РґС‹С€Рё РґР»СЏ СЂР°Р·Р»РёС‡РЅС‹С… С‚Р°Р±Р»РёС†
        self.car_panel = self.create_table_panel('РђРІС‚РѕРјРѕР±РёР»Рё', print_car, add_car, update_car, delete_car, 5)
        self.owner_panel = self.create_table_panel('Р’Р»Р°РґРµР»СЊС†С‹ Р°РІС‚РѕРјРѕР±РёР»РµР№', print_owner, add_owner, update_owner, delete_owner, 6)
        self.officer_panel = self.create_table_panel('РЎРѕС‚СЂСѓРґРЅРёРєРё Р“РђР', print_officer, add_officer, update_officer,
                                                     delete_officer, 3)
        self.inspection_panel = self.create_table_panel('РћСЃРјРѕС‚СЂС‹ Р°РІС‚РѕРјРѕР±РёР»РµР№', print_inspection, add_inspection,
                                                        update_inspection, delete_inspection, 4)
        self.user_panel = self.create_table_panel('РџРѕР»СЊР·РѕРІР°С‚РµР»Рё', print_users, add_users, update_users, delete_users, 2)

        # Р”РѕР±Р°РІР»РµРЅРёРµ СЃС‚СЂР°РЅРёС† РІ РІРєР»Р°РґРєРё
        self.notebook.AddPage(self.car_panel, 'РђРІС‚РѕРјРѕР±РёР»Рё')
        self.notebook.AddPage(self.owner_panel, 'Р’Р»Р°РґРµР»СЊС†С‹ Р°РІС‚РѕРјРѕР±РёР»РµР№')
        self.notebook.AddPage(self.officer_panel, 'РЎРѕС‚СЂСѓРґРЅРёРєРё Р“РђР')
        self.notebook.AddPage(self.inspection_panel, 'РћСЃРјРѕС‚СЂС‹ Р°РІС‚РѕРјРѕР±РёР»РµР№')
        self.notebook.AddPage(self.user_panel, 'РџРѕР»СЊР·РѕРІР°С‚РµР»Рё')

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND)
        self.SetSizer(sizer)

        # РЎРѕР·РґР°С‘Рј РІРєР»Р°РґРєСѓ РґР»СЏ РѕС‚С‡С‘С‚РѕРІ
        self.reports_panel = wx.Panel(self.notebook)
        self.reports_grid = wx.grid.Grid(self.reports_panel, -1)
        self.reports_grid.CreateGrid(1000, 5)
        self.reports_grid.SetColLabelValue(0, 'Р”Р°С‚Р°')
        self.reports_grid.SetColLabelValue(1, 'РљРѕР»РёС‡РµСЃС‚РІРѕ РѕСЃРјРѕС‚СЂРѕРІ')
        self.reports_grid.SetColLabelValue(2, 'РРЅСЃРїРµРєС‚РѕСЂ')
        self.reports_grid.SetColLabelValue(3, 'Р РµР·СѓР»СЊС‚Р°С‚')
        self.reports_grid.SetColLabelValue(4, 'РќРѕРјРµСЂ РґРІРёРіР°С‚РµР»СЏ')

        # РљРЅРѕРїРєРё РґР»СЏ РѕС‚С‡С‘С‚РѕРІ
        self.reports_sizer = wx.BoxSizer(wx.VERTICAL)
        self.reports_sizer.Add(self.reports_grid, 1, wx.EXPAND | wx.ALL, 5)

        # РљРЅРѕРїРєРё РґР»СЏ РѕС‚С‡С‘С‚РѕРІ
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.monthly_stats_btn = wx.Button(self.reports_panel, -1, 'РњРµСЃСЏС‡РЅР°СЏ СЃС‚Р°С‚РёСЃС‚РёРєР°')
        self.officer_details_btn = wx.Button(self.reports_panel, -1, 'Р”РµС‚Р°Р»Рё РёРЅСЃРїРµРєС‚РѕСЂР°')
        self.vehicle_history_btn = wx.Button(self.reports_panel, -1, 'РСЃС‚РѕСЂРёСЏ Р°РІС‚РѕРјРѕР±РёР»СЏ')

        btn_sizer.Add(self.monthly_stats_btn, 1, wx.ALL | wx.EXPAND, 5)
        btn_sizer.Add(self.officer_details_btn, 1, wx.ALL | wx.EXPAND, 5)
        btn_sizer.Add(self.vehicle_history_btn, 1, wx.ALL | wx.EXPAND, 5)

        self.reports_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.reports_panel.SetSizer(self.reports_sizer)

        # Р”РѕР±Р°РІР»СЏРµРј РЅРѕРІСѓСЋ РІРєР»Р°РґРєСѓ
        self.notebook.AddPage(self.reports_panel, 'РћС‚С‡С‘С‚С‹')

        # РџСЂРёРІСЏР·С‹РІР°РµРј РѕР±СЂР°Р±РѕС‚С‡РёРєРё СЃРѕР±С‹С‚РёР№
        self.monthly_stats_btn.Bind(wx.EVT_BUTTON, self.on_monthly_stats)
        self.officer_details_btn.Bind(wx.EVT_BUTTON, self.on_officer_details)
        self.vehicle_history_btn.Bind(wx.EVT_BUTTON, self.on_vehicle_history)

        self.Show()

    def on_monthly_stats(self, event):
        dialog = wx.TextEntryDialog(self, 'Р’РІРµРґРёС‚Рµ РіРѕРґ Рё РјРµСЃСЏС† (YYYY-MM):', 'РњРµСЃСЏС‡РЅР°СЏ СЃС‚Р°С‚РёСЃС‚РёРєР°')
        if dialog.ShowModal() == wx.ID_OK:
            date_str = dialog.GetValue()
            try:
                year = int(date_str[:4])
                month = int(date_str[5:])
                stats, officers, _ = get_monthly_inspection_stats(year, month)

                self.reports_grid.ClearGrid()
                for i, (date, count) in enumerate(stats):
                    self.reports_grid.SetCellValue(i, 0, str(date))
                    self.reports_grid.SetCellValue(i, 1, str(count))

                self.reports_grid.AutoSizeColumns()
            except ValueError:
                wx.MessageBox('РќРµРІРµСЂРЅС‹Р№ С„РѕСЂРјР°С‚ РґР°С‚С‹', 'РћС€РёР±РєР°', wx.OK | wx.ICON_ERROR)
        dialog.Destroy()

    def on_officer_details(self, event):
        dialog = wx.TextEntryDialog(self, 'Р’РІРµРґРёС‚Рµ РґР°С‚Сѓ (YYYY-MM-DD):',
                                    'Р”РµС‚Р°Р»Рё РёРЅСЃРїРµРєС‚РѕСЂР°')
        if dialog.ShowModal() == wx.ID_OK:
            try:
                date_str = dialog.GetValue()
                date = date_str.strip()

                inspections = get_officer_inspection_details(date)
                self.reports_grid.ClearGrid()

                for i, (name, title, eng_num, result) in enumerate(inspections):
                    self.reports_grid.SetCellValue(i, 0, date)
                    self.reports_grid.SetCellValue(i, 2, f"{name} ({title})")
                    self.reports_grid.SetCellValue(i, 3, result)
                    self.reports_grid.SetCellValue(i, 4, eng_num)

                self.reports_grid.AutoSizeColumns()
            except ValueError:
                wx.MessageBox('РќРµРІРµСЂРЅС‹Р№ С„РѕСЂРјР°С‚ РІРІРѕРґР°', 'РћС€РёР±РєР°', wx.OK | wx.ICON_ERROR)
        dialog.Destroy()

    def on_vehicle_history(self, event):
        dialog = wx.TextEntryDialog(self, 'Р’РІРµРґРёС‚Рµ РЅРѕРјРµСЂ РґРІРёРіР°С‚РµР»СЏ:', 'РСЃС‚РѕСЂРёСЏ Р°РІС‚РѕРјРѕР±РёР»СЏ')
        if dialog.ShowModal() == wx.ID_OK:
            engine_num = dialog.GetValue().strip()

            history = get_vehicle_inspection_history(engine_num)
            self.reports_grid.ClearGrid()

            for i, (eng_num, date, result) in enumerate(history):
                self.reports_grid.SetCellValue(i, 0, str(date))
                self.reports_grid.SetCellValue(i, 4, eng_num)
                self.reports_grid.SetCellValue(i, 3, result)

            self.reports_grid.AutoSizeColumns()
        dialog.Destroy()
    def create_table_panel(self, title, print_func, add_func, update_func, delete_func, num_cols):
        # РЎРѕР·РґР°РЅРёРµ РїР°РЅРµР»Рё РґР»СЏ РєР°Р¶РґРѕР№ С‚Р°Р±Р»РёС†С‹
        panel = wx.Panel(self.notebook)

        # РЎРѕР·РґР°РµРј РѕС‚РґРµР»СЊРЅСѓСЋ СЃРµС‚РєСѓ РґР»СЏ РєР°Р¶РґРѕР№ РїР°РЅРµР»Рё
        grid = wx.grid.Grid(panel, -1)
        grid.CreateGrid(1000, num_cols)  # РЈСЃС‚Р°РЅР°РІР»РёРІР°РµРј РєРѕР»РёС‡РµСЃС‚РІРѕ РєРѕР»РѕРЅРѕРє

        # РЈСЃС‚Р°РЅРѕРІРєР° Р·Р°РіРѕР»РѕРІРєРѕРІ
        headers = {
            'РђРІС‚РѕРјРѕР±РёР»Рё': ['Р“РѕСЃРЅРѕРјРµСЂ', 'РќРѕРјРµСЂ РґРІРёРіР°С‚РµР»СЏ', 'Р¦РІРµС‚', 'РњР°СЂРєР°', 'РќРѕРјРµСЂ С‚РµС…РЅРёС‡РµСЃРєРѕРіРѕ РїР°СЃРїРѕСЂС‚Р°'],
            'Р’Р»Р°РґРµР»СЊС†С‹ Р°РІС‚РѕРјРѕР±РёР»РµР№': ['РќРѕРјРµСЂ РІРѕРґРёС‚РµР»СЊСЃРєРѕРіРѕ СѓРґРѕСЃС‚РѕРІРµСЂРµРЅРёСЏ', 'Р¤РРћ', 'РђРґСЂРµСЃ', 'Р”Р°С‚Р° СЂРѕР¶РґРµРЅРёСЏ', 'РџРѕР»', 'Р“РѕСЃРЅРѕРјРµСЂ'],
            'РЎРѕС‚СЂСѓРґРЅРёРєРё Р“РђР': ['Р¤РРћ', 'Р”РѕР»Р¶РЅРѕСЃС‚СЊ', 'Р—РІР°РЅРёРµ'],
            'РћСЃРјРѕС‚СЂС‹ Р°РІС‚РѕРјРѕР±РёР»РµР№': ['Р”Р°С‚Р°', 'Р РµР·СѓР»СЊС‚Р°С‚', 'РРјСЏ СЃРѕС‚СЂСѓРґРЅРёРєР° Р“РђР', 'РќРѕРјРµСЂ РґРІРёРіР°С‚РµР»СЏ'],
            'РџРѕР»СЊР·РѕРІР°С‚РµР»Рё': ['Р›РѕРіРёРЅ', 'РџР°СЂРѕР»СЊ']
        }

        for col, header in enumerate(headers[title]):
            grid.SetColLabelValue(col, header)

        # РљРЅРѕРїРєРё
        load_button = wx.Button(panel, -1, 'РџРѕРєР°Р·Р°С‚СЊ РґР°РЅРЅС‹Рµ')
        add_button = wx.Button(panel, -1, 'Р”РѕР±Р°РІРёС‚СЊ')
        update_button = wx.Button(panel, -1, 'РР·РјРµРЅРёС‚СЊ')
        delete_button = wx.Button(panel, -1, 'РЈРґР°Р»РёС‚СЊ')

        # РџСЂРёРІСЏР·РєР° СЃРѕР±С‹С‚РёР№ СЃ СЃРѕС…СЂР°РЅРµРЅРёРµРј СЃСЃС‹Р»РєРё РЅР° РєРѕРЅРєСЂРµС‚РЅСѓСЋ СЃРµС‚РєСѓ
        load_button.Bind(wx.EVT_BUTTON, lambda event: self.on_load(event, grid, print_func))
        add_button.Bind(wx.EVT_BUTTON, lambda event: self.on_add(event, grid, add_func, num_cols))
        update_button.Bind(wx.EVT_BUTTON, lambda event: self.on_update(event, grid, update_func, num_cols))
        delete_button.Bind(wx.EVT_BUTTON, lambda event: self.on_delete(event, grid, delete_func))

        # РЎРёСЃС‚РµРјР° РєРѕРјРїРѕРЅРѕРІРєРё
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(load_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(add_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer.Add(update_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer.Add(delete_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        panel.SetSizer(sizer)
        return panel

    def on_load(self, event, grid, print_func):
        data = print_func()
        grid.ClearGrid()
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                grid.SetCellValue(i, j, str(value))

    def on_add(self, event, grid, add_func, num_cols):
        current_row = grid.GetGridCursorRow()
        if current_row < 0:
            return

        values = []
        for col in range(num_cols):
            value = grid.GetCellValue(current_row, col)
            values.append(value)

        add_func(*values)

    def on_update(self, event, grid, update_func, num_cols):
        current_row = grid.GetGridCursorRow()
        if current_row < 0:
            return

        values = []
        for col in range(num_cols):
            value = grid.GetCellValue(current_row, col)
            values.append(value)

        update_func(*values)

    def on_delete(self, event, grid, delete_func):
        identifier = grid.GetCellValue(grid.GetGridCursorRow(), 0)
        delete_func(identifier)


if __name__ == '__main__':
    app = wx.App()

    frame = DatabaseFrame(parent=None, id=-1)

    frame.Show()

    app.MainLoop()
