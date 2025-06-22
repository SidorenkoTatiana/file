import wx
import wx.grid
import psycopg2
from crud import *

# Конфигурация приложения
APP_TITLE = "__"
DB_CONFIG = {
    "host": "your_host",
    "dbname": "your_dbname",
    "user": "your_username",
    "password": "your_password"
}

# Цветовая схема (можно изменить под требования)
COLORS = {
    "primary": wx.Colour(64, 115, 158),  # Синий
    "secondary": wx.Colour(237, 237, 237),  # Светло-серый
    "accent": wx.Colour(255, 165, 0)  # Оранжевый
}

# Класс для окна аутентификации
class LoginDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Аутентификация", size=(300, 200))
        
        self.username = None
        self.password = None
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Элементы формы
        user_label = wx.StaticText(panel, label="Логин:")
        self.user_text = wx.TextCtrl(panel)
        
        pass_label = wx.StaticText(panel, label="Пароль:")
        self.pass_text = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        
        login_btn = wx.Button(panel, label="Войти")
        login_btn.Bind(wx.EVT_BUTTON, self.on_login)
        
        # Размещение элементов
        sizer.Add(user_label, 0, wx.ALL, 5)
        sizer.Add(self.user_text, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(pass_label, 0, wx.ALL, 5)
        sizer.Add(self.pass_text, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(login_btn, 0, wx.ALIGN_CENTER|wx.ALL, 15)
        
        panel.SetSizer(sizer)
        self.Centre()
    
    def on_login(self, event):
        self.username = self.user_text.GetValue()
        self.password = self.pass_text.GetValue()
        
        # Здесь можно добавить проверку логина/пароля
        if self.username and self.password:
            self.EndModal(wx.ID_OK)
        else:
            wx.MessageBox("Введите логин и пароль", "Ошибка", wx.OK|wx.ICON_ERROR)

# Главное окно приложения
class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(800, 600))
        
        self.current_table = None
        self.user_role = None  # Можно использовать для разграничения прав
        
        # Создаем меню
        self.create_menu()
        
        # Создаем панель с элементами управления
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Панель инструментов
        toolbar_panel = wx.Panel(panel)
        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.table_choice = wx.Choice(toolbar_panel, choices=self.get_table_list())
        self.table_choice.Bind(wx.EVT_CHOICE, self.on_table_select)
        
        refresh_btn = wx.Button(toolbar_panel, label="Обновить")
        refresh_btn.Bind(wx.EVT_BUTTON, self.on_refresh)
        
        add_btn = wx.Button(toolbar_panel, label="Добавить")
        add_btn.Bind(wx.EVT_BUTTON, self.on_add)
        
        edit_btn = wx.Button(toolbar_panel, label="Изменить")
        edit_btn.Bind(wx.EVT_BUTTON, self.on_edit)
        
        delete_btn = wx.Button(toolbar_panel, label="Удалить")
        delete_btn.Bind(wx.EVT_BUTTON, self.on_delete)
        
        toolbar_sizer.Add(self.table_choice, 0, wx.ALL, 5)
        toolbar_sizer.Add(refresh_btn, 0, wx.ALL, 5)
        toolbar_sizer.Add(add_btn, 0, wx.ALL, 5)
        toolbar_sizer.Add(edit_btn, 0, wx.ALL, 5)
        toolbar_sizer.Add(delete_btn, 0, wx.ALL, 5)
        toolbar_panel.SetSizer(toolbar_sizer)
        
        # Таблица для отображения данных
        self.grid = wx.grid.Grid(panel)
        self.grid.CreateGrid(0, 0)
        self.grid.EnableEditing(False)
        
        # Добавляем элементы на главную панель
        main_sizer.Add(toolbar_panel, 0, wx.EXPAND)
        main_sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 5)
        
        panel.SetSizer(main_sizer)
        self.Centre()
        
        # Применяем цветовую схему
        self.apply_theme()
    
    def apply_theme(self):
        """Применение цветовой схемы и шрифтов"""
        self.SetBackgroundColour(COLORS["secondary"])
        
        # Можно добавить настройку шрифтов, если они указаны в требованиях
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.SetFont(font)
    
    def create_menu(self):
        """Создание меню приложения"""
        menubar = wx.MenuBar()
        
        # Меню "Файл"
        file_menu = wx.Menu()
        import_item = file_menu.Append(wx.ID_ANY, "Импорт данных", "Импорт данных из файла")
        export_item = file_menu.Append(wx.ID_ANY, "Экспорт данных", "Экспорт данных в файл")
        exit_item = file_menu.Append(wx.ID_EXIT, "Выход", "Выход из приложения")
        
        menubar.Append(file_menu, "&Файл")
        
        # Меню "Справка"
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "О программе", "Информация о программе")
        
        menubar.Append(help_menu, "&Справка")
        
        self.SetMenuBar(menubar)
        
        # Привязка событий
        self.Bind(wx.EVT_MENU, self.on_import, import_item)
        self.Bind(wx.EVT_MENU, self.on_export, export_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)
    
    def get_table_list(self):
        """Получение списка таблиц из БД"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            return tables
        except Exception as e:
            print(f"Ошибка при получении списка таблиц: {e}")
            return []
    
    def on_table_select(self, event):
        """Обработчик выбора таблицы"""
        table_name = self.table_choice.GetStringSelection()
        if table_name:
            self.current_table = table_name
            self.load_table_data(table_name)
    
    def load_table_data(self, table_name):
        """Загрузка данных таблицы в grid"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            # Получаем данные
            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            
            # Получаем названия столбцов
            col_names = [desc[0] for desc in cur.description]
            
            # Настраиваем grid
            self.grid.ClearGrid()
            if self.grid.GetNumberRows() > 0:
                self.grid.DeleteRows(0, self.grid.GetNumberRows())
            if self.grid.GetNumberCols() > 0:
                self.grid.DeleteCols(0, self.grid.GetNumberCols())
            
            self.grid.CreateGrid(len(rows), len(col_names))
            
            # Устанавливаем названия столбцов
            for col, name in enumerate(col_names):
                self.grid.SetColLabelValue(col, name)
            
            # Заполняем данными
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    self.grid.SetCellValue(row_idx, col_idx, str(value))
            
            cur.close()
            conn.close()
        except Exception as e:
            wx.MessageBox(f"Ошибка при загрузке данных: {e}", "Ошибка", wx.OK|wx.ICON_ERROR)
    
    def on_refresh(self, event):
        """Обновление данных таблицы"""
        if self.current_table:
            self.load_table_data(self.current_table)
    
    def on_add(self, event):
        """Добавление новой записи"""
        if not self.current_table:
            wx.MessageBox("Выберите таблицу", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
        
        # Здесь можно реализовать диалоговое окно для ввода данных
        # или использовать редактирование непосредственно в grid
        
        # Пример простой реализации:
        dlg = wx.TextEntryDialog(self, "Введите данные для новой записи (в формате JSON):", "Добавление записи")
        if dlg.ShowModal() == wx.ID_OK:
            try:
                import json
                data = json.loads(dlg.GetValue())
                if isinstance(data, dict):
                    record_id = add_record(self.current_table, data)
                    if record_id:
                        wx.MessageBox(f"Запись добавлена с ID: {record_id}", "Успех", wx.OK|wx.ICON_INFORMATION)
                        self.on_refresh(None)
            except Exception as e:
                wx.MessageBox(f"Ошибка при добавлении: {e}", "Ошибка", wx.OK|wx.ICON_ERROR)
        dlg.Destroy()
    
    def on_edit(self, event):
        """Редактирование записи"""
        if not self.current_table:
            wx.MessageBox("Выберите таблицу", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
        
        selected_row = self.grid.GetGridCursorRow()
        if selected_row < 0:
            wx.MessageBox("Выберите запись для редактирования", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
        
        # Получаем ID записи (предполагаем, что первый столбец - ID)
        record_id = self.grid.GetCellValue(selected_row, 0)
        
        # Здесь можно реализовать диалоговое окно для редактирования
        # или использовать редактирование непосредственно в grid
        
        # Пример простой реализации:
        dlg = wx.TextEntryDialog(
            self, 
            f"Введите новые данные для записи ID {record_id} (в формате JSON):", 
            "Редактирование записи", 
            str({self.grid.GetColLabelValue(col): self.grid.GetCellValue(selected_row, col) 
                 for col in range(self.grid.GetNumberCols())})
        )
        
        if dlg.ShowModal() == wx.ID_OK:
            try:
                import json
                data = json.loads(dlg.GetValue())
                if isinstance(data, dict):
                    updated = update_record(self.current_table, record_id, data)
                    if updated > 0:
                        wx.MessageBox("Запись обновлена", "Успех", wx.OK|wx.ICON_INFORMATION)
                        self.on_refresh(None)
            except Exception as e:
                wx.MessageBox(f"Ошибка при обновлении: {e}", "Ошибка", wx.OK|wx.ICON_ERROR)
        dlg.Destroy()
    
    def on_delete(self, event):
        """Удаление записи"""
        if not self.current_table:
            wx.MessageBox("Выберите таблицу", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
        
        selected_row = self.grid.GetGridCursorRow()
        if selected_row < 0:
            wx.MessageBox("Выберите запись для удаления", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
        
        # Получаем ID записи (предполагаем, что первый столбец - ID)
        record_id = self.grid.GetCellValue(selected_row, 0)
        
        confirm = wx.MessageBox(
            f"Вы уверены, что хотите удалить запись с ID {record_id}?", 
            "Подтверждение удаления", 
            wx.YES_NO|wx.ICON_QUESTION
        )
        
        if confirm == wx.YES:
            deleted = delete_record(self.current_table, record_id)
            if deleted > 0:
                wx.MessageBox("Запись удалена", "Успех", wx.OK|wx.ICON_INFORMATION)
                self.on_refresh(None)
    
    def on_import(self, event):
        """Импорт данных из файла"""
        if not self.current_table:
            wx.MessageBox("Выберите таблицу", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
        
        wildcard = "CSV files (*.csv)|*.csv|JSON files (*.json)|*.json"
        dlg = wx.FileDialog(
            self, 
            message="Выберите файл для импорта", 
            wildcard=wildcard, 
            style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST
        )
        
        if dlg.ShowModal() == wx.ID_OK:
            file_path = dlg.GetPath()
            if file_path.endswith('.csv'):
                success = import_from_csv(self.current_table, file_path)
            elif file_path.endswith('.json'):
                success = import_from_json(self.current_table, file_path)
            else:
                success = False
            
            if success:
                wx.MessageBox("Данные успешно импортированы", "Успех", wx.OK|wx.ICON_INFORMATION)
                self.on_refresh(None)
            else:
                wx.MessageBox("Ошибка при импорте данных", "Ошибка", wx.OK|wx.ICON_ERROR)
        
        dlg.Destroy()
    
    def on_export(self, event):
        """Экспорт данных в файл"""
        if not self.current_table:
            wx.MessageBox("Выберите таблицу", "Ошибка", wx.OK|wx.ICON_ERROR)
            return
        
        wildcard = "CSV files (*.csv)|*.csv|JSON files (*.json)|*.json"
        dlg = wx.FileDialog(
            self, 
            message="Выберите файл для экспорта", 
            wildcard=wildcard, 
            style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT
        )
        
        if dlg.ShowModal() == wx.ID_OK:
            file_path = dlg.GetPath()
            try:
                conn = psycopg2.connect(**DB_CONFIG)
                cur = conn.cursor()
                
                # Получаем данные
                cur.execute(f"SELECT * FROM {self.current_table}")
                rows = cur.fetchall()
                col_names = [desc[0] for desc in cur.description]
                
                if file_path.endswith('.csv'):
                    import csv
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(col_names)
                        writer.writerows(rows)
                
                elif file_path.endswith('.json'):
                    import json
                    data = [dict(zip(col_names, row)) for row in rows]
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                
                wx.MessageBox("Данные успешно экспортированы", "Успех", wx.OK|wx.ICON_INFORMATION)
                
            except Exception as e:
                wx.MessageBox(f"Ошибка при экспорте: {e}", "Ошибка", wx.OK|wx.ICON_ERROR)
            finally:
                if 'conn' in locals():
                    conn.close()
        
        dlg.Destroy()
    
    def on_exit(self, event):
        """Выход из приложения"""
        self.Close()
    
    def on_about(self, event):
        """О программе"""
        wx.MessageBox(
            f"{APP_TITLE}\nВерсия 1.0\n\nПриложение для работы с базой данных", 
            "О программе", 
            wx.OK|wx.ICON_INFORMATION
        )

# Запуск приложения
if __name__ == "__main__":
    app = wx.App(False)
    
    # Показываем окно аутентификации
    login_dlg = LoginDialog(None)
    if login_dlg.ShowModal() == wx.ID_OK:
        # После успешной аутентификации показываем главное окно
        frame = MainFrame(None, APP_TITLE)
        frame.Show()
    
    login_dlg.Destroy()
    app.MainLoop()
