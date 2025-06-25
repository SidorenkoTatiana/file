import wx
import wx.grid as gridlib
import db
from datetime import datetime, date

class CourierWindow(wx.Frame):
    def __init__(self, parent, title, user):
        super(CourierWindow, self).__init__(parent, title=title, size=(900, 600))
        
        self.user = user
        self.current_parcels = []
        
        self.init_ui()
        self.load_todays_parcels()
        
    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Панель выбора даты
        date_box = wx.StaticBox(panel, label="Дата доставки")
        date_sizer = wx.StaticBoxSizer(date_box, wx.HORIZONTAL)
        
        self.date_picker = wx.DatePickerCtrl(panel, style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY)
        self.date_picker.SetValue(wx.DateTime.Now())
        btn_load = wx.Button(panel, label="Загрузить")
        
        date_sizer.Add(self.date_picker, flag=wx.ALL, border=5)
        date_sizer.Add(btn_load, flag=wx.ALL, border=5)
        
        btn_load.Bind(wx.EVT_BUTTON, self.on_load)
        
        # Таблица посылок
        self.parcel_grid = gridlib.Grid(panel)
        self.parcel_grid.CreateGrid(0, 5)
        self.parcel_grid.SetColLabelValue(0, "Внутренний номер")
        self.parcel_grid.SetColLabelValue(1, "Трек-номер")
        self.parcel_grid.SetColLabelValue(2, "Получатель")
        self.parcel_grid.SetColLabelValue(3, "Адрес")
        self.parcel_grid.SetColLabelValue(4, "Статус")
        
        for i in range(5):
            self.parcel_grid.SetColSize(i, 150)
        
        # Панель действий
        action_box = wx.StaticBox(panel, label="Действия")
        action_sizer = wx.StaticBoxSizer(action_box, wx.HORIZONTAL)
        
        self.btn_delivered = wx.Button(panel, label="Доставлено")
        self.btn_failed = wx.Button(panel, label="Не удалось")
        self.btn_reschedule = wx.Button(panel, label="Перенести")
        self.btn_print = wx.Button(panel, label="Печать")
        
        action_sizer.Add(self.btn_delivered, flag=wx.ALL, border=5)
        action_sizer.Add(self.btn_failed, flag=wx.ALL, border=5)
        action_sizer.Add(self.btn_reschedule, flag=wx.ALL, border=5)
        action_sizer.Add(self.btn_print, flag=wx.ALL, border=5)
        
        # Бинды
        self.btn_delivered.Bind(wx.EVT_BUTTON, self.on_delivered)
        self.btn_failed.Bind(wx.EVT_BUTTON, self.on_failed)
        self.btn_reschedule.Bind(wx.EVT_BUTTON, self.on_reschedule)
        self.btn_print.Bind(wx.EVT_BUTTON, self.on_print)
        self.parcel_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_parcel_details)
        
        # Сборка интерфейса
        vbox.Add(date_sizer, flag=wx.EXPAND|wx.ALL, border=5)
        vbox.Add(self.parcel_grid, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        vbox.Add(action_sizer, flag=wx.EXPAND|wx.ALL, border=5)
        
        panel.SetSizer(vbox)
        
    def load_todays_parcels(self):
        selected_date = self.date_picker.GetValue()
        date_str = selected_date.FormatISODate()
        
        self.current_parcels = db.get_parcels_for_delivery_by_date(date_str, self.user['user_id'])
        
        self.parcel_grid.ClearGrid()
        if self.parcel_grid.GetNumberRows() > 0:
            self.parcel_grid.DeleteRows(0, self.parcel_grid.GetNumberRows())
            
        for parcel in self.current_parcels:
            row = self.parcel_grid.GetNumberRows()
            self.parcel_grid.AppendRows(1)
            self.parcel_grid.SetCellValue(row, 0, parcel['internal_number'])
            self.parcel_grid.SetCellValue(row, 1, parcel['track_number'])
            self.parcel_grid.SetCellValue(row, 2, parcel['recipient'])
            self.parcel_grid.SetCellValue(row, 3, parcel.get('address', '-'))
            self.parcel_grid.SetCellValue(row, 4, self.translate_status(parcel['status']))
    
    def translate_status(self, status):
        status_map = {
            'ready_for_delivery': 'Готова к доставке',
            'in_delivery': 'В доставке',
            'delivery_failed': 'Доставка не удалась',
            'delivered': 'Доставлена'
        }
        return status_map.get(status, status)
    
    def get_selected_parcel(self):
        row = self.parcel_grid.GetGridCursorRow()
        if row == -1 or row >= len(self.current_parcels):
            return None
        return self.current_parcels[row]
    
    def on_load(self, event):
        self.load_todays_parcels()
    
    def on_delivered(self, event):
        parcel = self.get_selected_parcel()
        if not parcel:
            wx.MessageBox("Выберите посылку", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        try:
            db.update_parcel_status(parcel['parcel_id'], 'delivered', self.user['user_id'])
            wx.MessageBox("Посылка отмечена как доставленная", "Успех", wx.OK|wx.ICON_INFORMATION)
            self.load_todays_parcels()
        except Exception as e:
            wx.MessageBox(f"Ошибка при обновлении статуса: {str(e)}", "Ошибка", wx.OK|wx.ICON_ERROR)
    
    def on_failed(self, event):
        parcel = self.get_selected_parcel()
        if not parcel:
            wx.MessageBox("Выберите посылку", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        try:
            # Проверяем, была ли уже неудачная попытка
            if parcel['status'] == 'delivery_failed':
                db.update_parcel_delivery_date(parcel['parcel_id'], datetime.now(), self.user['user_id'])
            
            db.update_parcel_status(parcel['parcel_id'], 'delivery_failed', self.user['user_id'])
            wx.MessageBox("Посылка отмечена как не доставленная", "Успех", wx.OK|wx.ICON_INFORMATION)
            self.load_todays_parcels()
        except Exception as e:
            wx.MessageBox(f"Ошибка при обновлении статуса: {str(e)}", "Ошибка", wx.OK|wx.ICON_ERROR)
    
    def on_reschedule(self, event):
        parcel = self.get_selected_parcel()
        if not parcel:
            wx.MessageBox("Выберите посылку", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        dlg = RescheduleDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            new_date = dlg.get_date()
            try:
                db.reschedule_parcel_delivery(
                    parcel['parcel_id'],
                    new_date,
                    self.user['user_id']
                )
                wx.MessageBox(f"Доставка перенесена на {new_date.strftime('%d.%m.%Y')}", "Успех", wx.OK|wx.ICON_INFORMATION)
                self.load_todays_parcels()
            except Exception as e:
                wx.MessageBox(f"Ошибка при переносе доставки: {str(e)}", "Ошибка", wx.OK|wx.ICON_ERROR)
        dlg.Destroy()
    
    def on_print(self, event):
        selected_date = self.date_picker.GetValue()
        date_str = selected_date.FormatISODate()
        
        invoice = db.get_invoice_for_delivery_by_date(date_str)
        if not invoice:
            wx.MessageBox("Накладная не найдена", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        # Здесь должна быть реализация печати
        wx.MessageBox(f"Печать накладной {invoice['invoice_number']}", "Информация", wx.OK|wx.ICON_INFORMATION)
    
    def on_parcel_details(self, event):
        parcel = self.get_selected_parcel()
        if not parcel:
            return
            
        info = (
            f"Внутренний номер: {parcel['internal_number']}\n"
            f"Трек-номер: {parcel['track_number']}\n"
            f"Отправитель: {parcel['sender']}\n"
            f"Получатель: {parcel['recipient']}\n"
            f"Адрес: {parcel.get('address', 'не указан')}\n"
            f"Статус: {self.translate_status(parcel['status'])}\n"
            f"Дата поступления: {parcel['arrival_date'].strftime('%d.%m.%Y %H:%M')}"
        )
        
        wx.MessageBox(info, "Информация о посылке", wx.OK|wx.ICON_INFORMATION)

class RescheduleDialog(wx.Dialog):
    def __init__(self, parent):
        super(RescheduleDialog, self).__init__(parent, title="Перенос даты доставки", size=(300, 200))
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        vbox.Add(wx.StaticText(panel, label="Новая дата доставки:"), flag=wx.ALL, border=10)
        
        self.date_picker = wx.DatePickerCtrl(panel, style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY)
        self.date_picker.SetValue(wx.DateTime.Now() + wx.DateSpan(days=1))
        vbox.Add(self.date_picker, flag=wx.ALL, border=10)
        
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(panel, wx.ID_OK, "OK")
        btn_cancel = wx.Button(panel, wx.ID_CANCEL, "Отмена")
        
        btn_box.Add(btn_ok, flag=wx.ALL, border=5)
        btn_box.Add(btn_cancel, flag=wx.ALL, border=5)
        
        vbox.Add(btn_box, flag=wx.ALIGN_CENTER|wx.ALL, border=10)
        
        panel.SetSizer(vbox)
    
    def get_date(self):
        dt = self.date_picker.GetValue()
        return datetime(dt.GetYear(), dt.GetMonth()+1, dt.GetDay())
