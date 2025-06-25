import wx
import db
from driver_window import DriverWindow
from manager_window import ManagerWindow
from courier_window import CourierWindow

class AuthWindow(wx.Frame):
    def __init__(self, parent, title):
        super(AuthWindow, self).__init__(parent, title=title, size=(350, 250))
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Элементы формы
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label="Логин:")
        hbox1.Add(st1, flag=wx.RIGHT, border=8)
        self.tc_login = wx.TextCtrl(panel)
        hbox1.Add(self.tc_login, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10, proportion=0)
        
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, label="Пароль:")
        hbox2.Add(st2, flag=wx.RIGHT, border=8)
        self.tc_password = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        hbox2.Add(self.tc_password, proportion=1)
        vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10, proportion=0)
        
        self.btn_login = wx.Button(panel, label="Войти")
        vbox.Add(self.btn_login, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10, proportion=0)
        
        panel.SetSizer(vbox)
        
        # Привязка событий
        self.btn_login.Bind(wx.EVT_BUTTON, self.on_login)
        self.tc_password.Bind(wx.EVT_TEXT_ENTER, self.on_login)
        
        self.Centre()
    
    def on_login(self, event):
        login = self.tc_login.GetValue()
        password = self.tc_password.GetValue()
        
        if not login or not password:
            wx.MessageBox("Введите логин и пароль", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
        
        user = db.authenticate_user(login, password)
        if not user:
            wx.MessageBox("Неверный логин или пароль", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
        
        # Закрываем окно авторизации
        self.Hide()
        
        # Открываем соответствующее окно
        if user['role'] == 'driver':
            frame = DriverWindow(None, title=f"Водитель-экспедитор: {user['full_name']}", user=user)
        elif user['role'] == 'manager':
            frame = ManagerWindow(None, title=f"Менеджер: {user['full_name']}", user=user)
        elif user['role'] == 'courier':
            frame = CourierWindow(None, title=f"Курьер: {user['full_name']}", user=user)
        
        frame.Show()
