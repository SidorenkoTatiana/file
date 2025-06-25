import wx
import wx.grid as gridlib
import db
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class ManagerWindow(wx.Frame):
    def __init__(self, parent, title, user):
        super(ManagerWindow, self).__init__(parent, title=title, size=(1000, 700))
        
        self.user = user
        self.unchecked_parcels = []
        self.current_invoice_type = 'delivery'
        
        self.init_ui()
        self.load_unchecked_parcels()
        
    def init_ui(self):
        panel = wx.Panel(self)
        self.notebook = wx.Notebook(panel)
        
        # Вкладка проверки посылок
        self.check_tab = wx.Panel(self.notebook)
        self.setup_check_ui()
        
        # Вкладка формирования накладных
        self.invoice_tab = wx.Panel(self.notebook)
        self.setup_invoice_ui()
        
        self.notebook.AddPage(self.check_tab, "Проверка посылок")
        self.notebook.AddPage(self.invoice_tab, "Накладные")
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        
        self.Centre()
    
    def setup_check_ui(self):
        panel = self.check_tab
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Таблица непроверенных посылок
        self.parcel_grid = gridlib.Grid(panel)
        self.parcel_grid.CreateGrid(0, 5)
        self.parcel_grid.SetColLabelValue(0, "Трек-номер")
        self.parcel_grid.SetColLabelValue(1, "Отправитель")
        self.parcel_grid.SetColLabelValue(2, "Получатель")
        self.parcel_grid.SetColLabelValue(3, "Дата поступления")
        self.parcel_grid.SetColLabelValue(4, "Статус")
        
        for i in range(5):
            self.parcel_grid.SetColSize(i, 150)
        
        # Панель действий
        action_box = wx.StaticBox(panel, label="Действия")
        action_sizer = wx.StaticBoxSizer(action_box, wx.HORIZONTAL)
        
        self.btn_confirm = wx.Button(panel, label="Подтвердить")
        self.btn_edit = wx.Button(panel, label="Редактировать")
        self.btn_missing = wx.Button(panel, label="Отметить отсутствие")
        
        action_sizer.Add(self.btn_confirm, flag=wx.ALL, border=5)
        action_sizer.Add(self.btn_edit, flag=wx.ALL, border=5)
        action_sizer.Add(self.btn_missing, flag=wx.ALL, border=5)
        
        # Бинды
        self.btn_confirm.Bind(wx.EVT_BUTTON, self.on_confirm)
        self.btn_edit.Bind(wx.EVT_BUTTON, self.on_edit)
        self.btn_missing.Bind(wx.EVT_BUTTON, self.on_missing)
        self.parcel_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_edit)
        
        # Сборка интерфейса
        vbox.Add(self.parcel_grid, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        vbox.Add(action_sizer, flag=wx.EXPAND|wx.ALL, border=5)
        
        panel.SetSizer(vbox)
    
    def setup_invoice_ui(self):
        panel = self.invoice_tab
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Панель управления
        control_box = wx.StaticBox(panel, label="Управление накладными")
        control_sizer = wx.StaticBoxSizer(control_box, wx.HORIZONTAL)
        
        btn_generate = wx.Button(panel, label="Сформировать на доставку")
        btn_print = wx.Button(panel, label="Печать")
        btn_return = wx.Button(panel, label="Сформировать возврат")
        
        control_sizer.Add(btn_generate, flag=wx.ALL, border=5)
        control_sizer.Add(btn_print, flag=wx.ALL, border=5)
        control_sizer.Add(btn_return, flag=wx.ALL, border=5)
        
        # Таблица накладных
        self.invoice_grid = gridlib.Grid(panel)
        self.invoice_grid.CreateGrid(0, 4)
        self.invoice_grid.SetColLabelValue(0, "Номер")
        self.invoice_grid.SetColLabelValue(1, "Тип")
        self.invoice_grid.SetColLabelValue(2, "Дата создания")
        self.invoice_grid.SetColLabelValue(3, "Кол-во посылок")
        
        for i in range(4):
            self.invoice_grid.SetColSize(i, 150)
        
        # Бинды
        btn_generate.Bind(wx.EVT_BUTTON, self.on_generate_delivery)
        btn_print.Bind(wx.EVT_BUTTON, self.on_print_invoice)
        btn_return.Bind(wx.EVT_BUTTON, self.on_generate_return)
        self.invoice_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_view_invoice)
        
        # Сборка интерфейса
        vbox.Add(control_sizer, flag=wx.EXPAND|wx.ALL, border=5)
        vbox.Add(self.invoice_grid, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        
        panel.SetSizer(vbox)
        
        self.load_invoices()
    
    def load_unchecked_parcels(self):
        self.unchecked_parcels = db.get_parcels_by_status('delivered_to_office')
        
        self.parcel_grid.ClearGrid()
        if self.parcel_grid.GetNumberRows() > 0:
            self.parcel_grid.DeleteRows(0, self.parcel_grid.GetNumberRows())
            
        for parcel in self.unchecked_parcels:
            row = self.parcel_grid.GetNumberRows()
            self.parcel_grid.AppendRows(1)
            self.parcel_grid.SetCellValue(row, 0, parcel['track_number'])
            self.parcel_grid.SetCellValue(row, 1, parcel['sender'])
            self.parcel_grid.SetCellValue(row, 2, parcel['recipient'])
            self.parcel_grid.SetCellValue(row, 3, parcel['arrival_date'].strftime('%d.%m.%Y %H:%M'))
            self.parcel_grid.SetCellValue(row, 4, "Доставлена в офис")
    
    def load_invoices(self):
        invoices = db.get_all_invoices()
        
        self.invoice_grid.ClearGrid()
        if self.invoice_grid.GetNumberRows() > 0:
            self.invoice_grid.DeleteRows(0, self.invoice_grid.GetNumberRows())
            
        for invoice in invoices:
            row = self.invoice_grid.GetNumberRows()
            self.invoice_grid.AppendRows(1)
            self.invoice_grid.SetCellValue(row, 0, invoice['invoice_number'])
            self.invoice_grid.SetCellValue(row, 1, "Доставка" if invoice['invoice_type'] == 'delivery' else "Возврат")
            self.invoice_grid.SetCellValue(row, 2, invoice['creation_date'].strftime('%d.%m.%Y %H:%M'))
            self.invoice_grid.SetCellValue(row, 3, str(invoice['parcel_count']))
    
    def get_selected_parcel(self):
        row = self.parcel_grid.GetGridCursorRow()
        if row == -1 or row >= len(self.unchecked_parcels):
            return None
        return self.unchecked_parcels[row]
    
    def get_selected_invoice(self):
        row = self.invoice_grid.GetGridCursorRow()
        if row == -1:
            return None
        return self.invoice_grid.GetCellValue(row, 0)
    
    def on_confirm(self, event):
        parcel = self.get_selected_parcel()
        if not parcel:
            wx.MessageBox("Выберите посылку", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        try:
            db.update_parcel_status(parcel['parcel_id'], 'ready_for_delivery', self.user['user_id'])
            wx.MessageBox("Посылка подтверждена и готова к доставке", "Успех", wx.OK|wx.ICON_INFORMATION)
            self.load_unchecked_parcels()
        except Exception as e:
            wx.MessageBox(f"Ошибка при подтверждении посылки: {str(e)}", "Ошибка", wx.OK|wx.ICON_ERROR)
    
    def on_edit(self, event):
        parcel = self.get_selected_parcel()
        if not parcel:
            wx.MessageBox("Выберите посылку", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        dlg = EditParcelDialog(self, parcel)
        if dlg.ShowModal() == wx.ID_OK:
            try:
                db.update_parcel_data(
                    parcel['parcel_id'],
                    dlg.get_sender(),
                    dlg.get_recipient(),
                    self.user['user_id']
                )
                wx.MessageBox("Данные посылки успешно обновлены", "Успех", wx.OK|wx.ICON_INFORMATION)
                self.load_unchecked_parcels()
            except Exception as e:
                wx.MessageBox(f"Ошибка при обновлении данных: {str(e)}", "Ошибка", wx.OK|wx.ICON_ERROR)
        dlg.Destroy()
    
    def on_missing(self, event):
        parcel = self.get_selected_parcel()
        if not parcel:
            wx.MessageBox("Выберите посылку", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        try:
            db.update_parcel_status(parcel['parcel_id'], 'error_missing', self.user['user_id'])
            wx.MessageBox("Посылка отмечена как отсутствующая", "Успех", wx.OK|wx.ICON_INFORMATION)
            self.load_unchecked_parcels()
        except Exception as e:
            wx.MessageBox(f"Ошибка при обновлении статуса: {str(e)}", "Ошибка", wx.OK|wx.ICON_ERROR)
    
    def on_generate_delivery(self, event):
        # Проверка времени (после 17:00)
        now = datetime.now()
        if now.hour < 17:
            wx.MessageBox("Список доставки можно формировать только после 17:00", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        # Проверка наличия непроверенных посылок
        unchecked = db.get_parcels_by_status('delivered_to_office')
        if unchecked:
            wx.MessageBox("Имеются непроверенные посылки. Сначала проверьте все посылки.", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        try:
            invoice_id = db.generate_delivery_list(self.user['user_id'])
            self.generate_pdf_invoice(invoice_id)
            wx.MessageBox("Накладная на доставку успешно сформирована", "Успех", wx.OK|wx.ICON_INFORMATION)
            self.load_invoices()
        except Exception as e:
            wx.MessageBox(f"Ошибка при формировании накладной: {str(e)}", "Ошибка", wx.OK|wx.ICON_ERROR)
    
    def on_generate_return(self, event):
        try:
            invoice_id = db.generate_return_list(self.user['user_id'])
            self.generate_pdf_invoice(invoice_id)
            wx.MessageBox("Накладная на возврат успешно сформирована", "Успех", wx.OK|wx.ICON_INFORMATION)
            self.load_invoices()
        except Exception as e:
            wx.MessageBox(f"Ошибка при формировании накладной: {str(e)}", "Ошибка", wx.OK|wx.ICON_ERROR)
    
    def on_print_invoice(self, event):
        invoice_num = self.get_selected_invoice()
        if not invoice_num:
            wx.MessageBox("Выберите накладную", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        self.generate_pdf_invoice(invoice_num)
    
    def on_view_invoice(self, event):
        invoice_num = self.get_selected_invoice()
        if not invoice_num:
            wx.MessageBox("Выберите накладную", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
            
        parcels = db.get_parcels_for_invoice(invoice_num)
        dlg = ParcelListDialog(self, f"Посылки в накладной {invoice_num}", parcels)
        dlg.ShowModal()
        dlg.Destroy()
    
    def generate_pdf_invoice(self, invoice_id):
        invoice = db.get_invoice_by_number(invoice_id)
        parcels = db.get_parcels_for_invoice(invoice_id)
        
        filename = f"Накладная_{invoice_id}.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        
        # Заголовок
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 800, f"Накладная №{invoice_id}")
        c.setFont("Helvetica", 12)
        c.drawString(100, 780, f"Тип: {'Доставка' if invoice['invoice_type'] == 'delivery' else 'Возврат'}")
        c.drawString(100, 760, f"Дата создания: {invoice['creation_date'].strftime('%d.%m.%Y %H:%M')}")
        c.drawString(100, 740, f"Количество посылок: {len(parcels)}")
        
        # Таблица посылок
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 710, "№")
        c.drawString(100, 710, "Трек-номер")
        c.drawString(250, 710, "Внутренний номер")
        c.drawString(400, 710, "Получатель")
        
        c.setFont("Helvetica", 10)
        y = 690
        for i, parcel in enumerate(parcels, 1):
            if y < 50:
                c.showPage()
                y = 800
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, "№")
                c.drawString(100, y, "Трек-номер")
                c.drawString(250, y, "Внутренний номер")
                c.drawString(400, y, "Получатель")
                y = 780
                c.setFont("Helvetica", 10)
            
            c.drawString(50, y, str(i))
            c.drawString(100, y, parcel['track_number'])
            c.drawString(250, y, parcel.get('internal_number', '-'))
            c.drawString(400, y, parcel['recipient'])
            y -= 20
        
        c.save()
        wx.MessageBox(f"PDF документ сохранен как {filename}", "Готово", wx.OK|wx.ICON_INFORMATION)

class EditParcelDialog(wx.Dialog):
    def __init__(self, parent, parcel):
        super(EditParcelDialog, self).__init__(parent, title="Редактирование посылки", size=(400, 300))
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        grid = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        
        grid.Add(wx.StaticText(panel, label="Трек-номер:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.tc_track = wx.TextCtrl(panel, value=parcel['track_number'])
        self.tc_track.Disable()
        grid.Add(self.tc_track, flag=wx.EXPAND)
        
        grid.Add(wx.StaticText(panel, label="Отправитель:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.tc_sender = wx.TextCtrl(panel, value=parcel['sender'])
        grid.Add(self.tc_sender, flag=wx.EXPAND)
        
        grid.Add(wx.StaticText(panel, label="Получатель:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.tc_recipient = wx.TextCtrl(panel, value=parcel['recipient'])
        grid.Add(self.tc_recipient, flag=wx.EXPAND)
        
        grid.Add(wx.StaticText(panel, label="Дата поступления:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.tc_date = wx.TextCtrl(panel, value=parcel['arrival_date'].strftime('%d.%m.%Y %H:%M'))
        self.tc_date.Disable()
        grid.Add(self.tc_date, flag=wx.EXPAND)
        
        vbox.Add(grid, flag=wx.EXPAND|wx.ALL, border=10)
        
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(panel, wx.ID_OK, "Сохранить")
        btn_cancel = wx.Button(panel, wx.ID_CANCEL, "Отмена")
        
        btn_box.Add(btn_ok, flag=wx.ALL, border=5)
        btn_box.Add(btn_cancel, flag=wx.ALL, border=5)
        
        vbox.Add(btn_box, flag=wx.ALIGN_CENTER|wx.ALL, border=5)
        
        panel.SetSizer(vbox)
    
    def get_sender(self):
        return self.tc_sender.GetValue()
    
    def get_recipient(self):
        return self.tc_recipient.GetValue()
