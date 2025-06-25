import wx
from auth_window import AuthWindow

class CourierApp(wx.App):
    def OnInit(self):
        self.frame = AuthWindow(None, title="Авторизация - Курьерская служба")
        self.frame.Show()
        return True

if __name__ == "__main__":
    app = CourierApp(False)
    app.MainLoop()
