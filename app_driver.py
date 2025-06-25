import wx
import wx.grid as gridlib
import db
from datetime import datetime

class DriverWindow(wx.Frame):
    def __init__(self, parent, title, user):
        super(DriverWindow, self).__init__(parent, title=title, size=(900, 600))
        
        self.user = user
        self.parcels = []
        self.current_invoice_type = 'delivery'
        
        self.init_ui()
        self.load_invoices()
        
    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Панель выбора типа накладной
        invoice_type_box = wx.StaticBox(panel, label="Тип накладной")
        invoice_type_sizer = wx.StaticBoxSizer(invoice_type_box, wx.HORIZONTAL)
        
        self.rb_delivery = wx.RadioButton(panel, label="Доставка", style=wx.RB_GROUP)
        self.rb_return = wx.RadioButton(panel, label="Возврат")
        self.rb_delivery.SetValue(True)
        
        invoice_type_sizer.Add(self.rb_delivery, flag=wx.ALL, border=5)
        invoice_type_sizer.Add(self.rb_return, flag=wx.ALL, border=5)
        
        self.rb_delivery.Bind(wx.EVT_RADIOBUTTON, self.on_invoice_type_change)
        self.rb_return.Bind(wx.EVT_RADIOBUTTON, self.on_invoice_type_change)
        
        # Поле фильтрации по дате
        filter_box = wx.StaticBox(panel, label="Фильтр")
        filter_sizer = wx.StaticBoxSizer(filter_box, wx.HORIZONTAL)
        
        filter_sizer.Add(wx.StaticText(panel, label="Дата:"), flag=wx.ALIGN_CENTER|wx.ALL, border=5)
        self.date_picker = wx.DatePickerCtrl(panel, style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY)
        filter_sizer.Add(self.date_picker, flag=wx.ALL, border=5)
        
        btn_filter = wx.Button(panel, label="Применить фильтр")
        filter_sizer.Add(btn_filter, flag=wx.ALL, border=5)
        btn_filter.Bind(wx.EVT_BUTTON, self.on_filter)
        
        # Таблица накладных
        self.invoice_grid = gridlib.Grid(panel)
        self.invoice_grid.CreateGrid(0, 3)
        self.invoice_grid.SetColLabelValue(0, "Номер")
        self.invoice_grid.SetColLabelValue(1, "Дата")
        self.invoice_grid.SetColLabelValue(2, "Кол-во посылок")
        self.invoice_grid.SetColSize(0, 150)
        self.invoice_grid.SetColSize(1, 150)
        self.invoice_grid.SetColSize(2, 100)
        self.invoice_grid.DisableDragRowSize()
        
        # Кнопки
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_print = wx.Button(panel, label="Печать")
        self.btn_view = wx.Button(panel, label="Просмотр")
        self.btn_add_parcels = wx.Button(panel, label="Добавить посылки")
        
        btn_box.Add(self.btn_print, flag=wx.ALL, border=5)
        btn_box.Add(self.btn_view, flag=wx.ALL, border=5)
        btn_box.Add(self.btn_add_parcels, flag=wx.ALL, border=5)
        
        # Бинды
        self.btn_print.Bind(wx.EVT_BUTTON, self.on_print)
        self.btn_view.Bind(wx.EVT_BUTTON, self.on_view)
        self.btn_add_parcels.Bind(wx.EVT_BUTTON, self.on_add_parcels)
        self.invoice_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_view)
        
        # Сборка интерфейса
        vbox.Add(invoice_type_sizer, flag=wx.EXPAND|wx.ALL, border=5)
        vbox.Add(filter_sizer, flag=wx.EXPAND|wx.ALL, border=5)
        vbox.Add(self.invoice_grid, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        vbox.Add(btn_box, flag=wx.ALIGN_CENTER|wx.ALL, border=5)
        
        panel.SetSizer(vbox)
        
    def on_invoice_type_change(self, event):
        self.current_invoice_type = 'delivery' if self.rb_delivery.GetValue() else 'return'
        self.load_invoices()
        
    def on_filter(self, event):
        self.load_invoices()
        
    def load_invoices(self):
        date = self.date_picker.GetValue()
        date_str = date.FormatISODate()
        
        invoices = db.get_invoices_by_type_and_date(
            self.current_invoice_type, 
            date_str
        )
        
        self.invoice_grid.ClearGrid()
        if self.invoice_grid.GetNumberRows() > 0:
            self.invoice_grid.DeleteRows(0, self.invoice_grid.GetNumberRows())
            
        for invoice in invoices:
            row = self.invoice_grid.GetNumberRows()
            self.invoice_grid.AppendRows(1)
            self.invoice_grid.SetCellValue(row, 0, invoice['invoice_number'])
            self.invoice_grid.SetCellValue(row, 1, invoice['creation_date'].strftime('%d.%m.%Y %H:%M'))
            self.invoice_grid.SetCellValue(row, 2, str(invoice['parcel_count']))
            
    def on_print(self, event):
        selected = self.get_selected_invoice()
        if not selected:
            wx.MessageBox("Выберите накладную", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        # Здесь должна быть реализация печати
        wx.MessageBox(f"Печать накладной {selected}", "Информация", wx.OK|wx.ICON_INFORMATION)
        
    def on_view(self, event):
        selected = self.get_selected_invoice()
        if not selected:
            wx.MessageBox("Выберите накладную", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        parcels = db.get_parcels_for_invoice(selected)
        dlg = ParcelListDialog(self, f"Посылки в накладной {selected}", parcels)
        dlg.ShowModal()
        dlg.Destroy()
        
    def on_add_parcels(self, event):
        dlg = AddParcelsDialog(self, self.user)
        if dlg.ShowModal() == wx.ID_OK:
            self.load_invoices()
        dlg.Destroy()
        
    def get_selected_invoice(self):
        row = self.invoice_grid.GetGridCursorRow()
        if row == -1:
            return None
        return self.invoice_grid.GetCellValue(row, 0)

class ParcelListDialog(wx.Dialog):
    def __init__(self, parent, title, parcels):
        super(ParcelListDialog, self).__init__(parent, title=title, size=(600, 400))
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        grid = gridlib.Grid(panel)
        grid.CreateGrid(len(parcels), 4)
        grid.SetColLabelValue(0, "Трек-номер")
        grid.SetColLabelValue(1, "Отправитель")
        grid.SetColLabelValue(2, "Получатель")
        grid.SetColLabelValue(3, "Статус")
        
        for i, parcel in enumerate(parcels):
            grid.SetCellValue(i, 0, parcel['track_number'])
            grid.SetCellValue(i, 1, parcel['sender'])
            grid.SetCellValue(i, 2, parcel['recipient'])
            grid.SetCellValue(i, 3, self.translate_status(parcel['status']))
            
        grid.AutoSizeColumns()
        grid.DisableDragRowSize()
        
        vbox.Add(grid, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        
        btn_ok = wx.Button(panel, wx.ID_OK, "OK")
        vbox.Add(btn_ok, flag=wx.ALIGN_CENTER|wx.ALL, border=5)
        
        panel.SetSizer(vbox)
        
    def translate_status(self, status):
        status_map = {
            'delivered_to_office': 'Доставлена в офис',
            'ready_for_delivery': 'Готова к доставке',
            'delivery_failed': 'Доставка не удалась',
            'delivered': 'Доставлена',
            'error_missing': 'Ошибка: посылка отсутствует'
        }
        return status_map.get(status, status)

class AddParcelsDialog(wx.Dialog):
    def __init__(self, parent, user):
        super(AddParcelsDialog, self).__init__(parent, title="Добавление посылок", size=(700, 500))
        
        self.user = user
        self.parcels = []
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Поля ввода
        input_box = wx.StaticBox(panel, label="Данные посылки")
        input_sizer = wx.StaticBoxSizer(input_box, wx.VERTICAL)
        
        grid = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        
        grid.Add(wx.StaticText(panel, label="Трек-номер:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.tc_track = wx.TextCtrl(panel)
        grid.Add(self.tc_track, flag=wx.EXPAND)
        
        grid.Add(wx.StaticText(panel, label="Отправитель:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.tc_sender = wx.TextCtrl(panel)
        grid.Add(self.tc_sender, flag=wx.EXPAND)
        
        grid.Add(wx.StaticText(panel, label="Получатель:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.tc_recipient = wx.TextCtrl(panel)
        grid.Add(self.tc_recipient, flag=wx.EXPAND)
        
        grid.Add(wx.StaticText(panel, label="Код региона:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.tc_region = wx.TextCtrl(panel, size=(50, -1))
        grid.Add(self.tc_region, flag=wx.EXPAND)
        
        input_sizer.Add(grid, flag=wx.EXPAND|wx.ALL, border=5)
        
        btn_add = wx.Button(panel, label="Добавить в список")
        input_sizer.Add(btn_add, flag=wx.ALIGN_CENTER|wx.ALL, border=5)
        btn_add.Bind(wx.EVT_BUTTON, self.on_add)
        
        # Список добавленных посылок
        self.parcel_list = wx.ListCtrl(panel, style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        self.parcel_list.InsertColumn(0, "Трек-номер", width=150)
        self.parcel_list.InsertColumn(1, "Отправитель", width=200)
        self.parcel_list.InsertColumn(2, "Получатель", width=200)
        
        # Кнопки управления
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        btn_remove = wx.Button(panel, label="Удалить")
        btn_confirm = wx.Button(panel, label="Подтвердить")
        btn_cancel = wx.Button(panel, wx.ID_CANCEL, "Отмена")
        
        btn_box.Add(btn_remove, flag=wx.ALL, border=5)
        btn_box.Add(btn_confirm, flag=wx.ALL, border=5)
        btn_box.Add(btn_cancel, flag=wx.ALL, border=5)
        
        btn_remove.Bind(wx.EVT_BUTTON, self.on_remove)
        btn_confirm.Bind(wx.EVT_BUTTON, self.on_confirm)
        
        # Сборка интерфейса
        vbox.Add(input_sizer, flag=wx.EXPAND|wx.ALL, border=5)
        vbox.Add(self.parcel_list, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        vbox.Add(btn_box, flag=wx.ALIGN_CENTER|wx.ALL, border=5)
        
        panel.SetSizer(vbox)
        
    def on_add(self, event):
        track = self.tc_track.GetValue()
        sender = self.tc_sender.GetValue()
        recipient = self.tc_recipient.GetValue()
        region = self.tc_region.GetValue()
        
        if not all([track, sender, recipient, region]):
            wx.MessageBox("Заполните все поля", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        # Проверка формата трек-номера
        if not track.startswith("RU.") or len(track.split('.')) != 2 or len(track.split('.')[1]) != 9:
            wx.MessageBox("Трек-номер должен быть в формате RU.*********", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        self.parcels.append({
            'track_number': track,
            'sender': sender,
            'recipient': recipient,
            'region_code': region
        })
        
        idx = self.parcel_list.InsertItem(self.parcel_list.GetItemCount(), track)
        self.parcel_list.SetItem(idx, 1, sender)
        self.parcel_list.SetItem(idx, 2, recipient)
        
        # Очистка полей
        self.tc_track.Clear()
        self.tc_sender.Clear()
        self.tc_recipient.Clear()
        self.tc_region.Clear()
        self.tc_track.SetFocus()
        
    def on_remove(self, event):
        selected = self.parcel_list.GetFirstSelected()
        if selected == -1:
            wx.MessageBox("Выберите посылку для удаления", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        self.parcel_list.DeleteItem(selected)
        del self.parcels[selected]
        
    def on_confirm(self, event):
        if not self.parcels:
            wx.MessageBox("Добавьте хотя бы одну посылку", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        try:
            db.add_parcels_to_office(self.parcels, self.user['user_id'])
            wx.MessageBox(f"Успешно добавлено {len(self.parcels)} посылок", "Успех", wx.OK|wx.ICON_INFORMATION)
            self.EndModal(wx.ID_OK)
        except Exception as e:
            wx.MessageBox(f"Ошибка при добавлении посылок: {str(e)}", "Ошибка", wx.OK|wx.ICON_ERROR)
