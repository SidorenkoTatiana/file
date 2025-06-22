### Шпаргалка по wxPython для разработки desktop-приложений  

#### **1. Основы wxPython**  
- **Инициализация приложения и главного окна**:  
  ```python
  import wx
  
  app = wx.App(False)  # False - чтобы не перенаправлять stdout/stderr
  frame = wx.Frame(None, title="Мое приложение", size=(800, 600))
  frame.Show()
  app.MainLoop()
  ```

#### **2. Основные виджеты**  
- **Кнопка (`wx.Button`)**  
  ```python
  button = wx.Button(frame, label="Нажми меня", pos=(10, 10), size=(100, 30))
  button.Bind(wx.EVT_BUTTON, lambda e: print("Кнопка нажата!"))
  ```

- **Текстовое поле (`wx.TextCtrl`)**  
  ```python
  text_ctrl = wx.TextCtrl(frame, pos=(10, 50), size=(200, 30))
  ```

- **Метка (`wx.StaticText`)**  
  ```python
  label = wx.StaticText(frame, label="Текст:", pos=(10, 90))
  ```

- **Список (`wx.ListBox`)**  
  ```python
  list_box = wx.ListBox(frame, choices=["Элемент 1", "Элемент 2"], pos=(10, 120), size=(200, 100))
  ```

- **Таблица (`wx.grid.Grid`)**  
  ```python
  grid = wx.grid.Grid(frame)
  grid.CreateGrid(5, 3)  # 5 строк, 3 столбца
  grid.SetCellValue(0, 0, "Данные")
  ```

- **Чекбокс (`wx.CheckBox`)**  
  ```python
  checkbox = wx.CheckBox(frame, label="Включить", pos=(10, 230))
  ```

- **Радиокнопки (`wx.RadioButton`)**  
  ```python
  radio1 = wx.RadioButton(frame, label="Вариант 1", pos=(10, 260), style=wx.RB_GROUP)
  radio2 = wx.RadioButton(frame, label="Вариант 2", pos=(10, 290))
  ```

#### **3. Работа с окнами**  
- **Модальное окно (`wx.MessageBox`)**  
  ```python
  wx.MessageBox("Текст сообщения", "Заголовок", wx.OK | wx.ICON_INFORMATION)
  ```

- **Диалог выбора файла (`wx.FileDialog`)**  
  ```python
  dialog = wx.FileDialog(frame, "Выберите файл", wildcard="*.txt")
  if dialog.ShowModal() == wx.ID_OK:
      print(dialog.GetPath())
  ```

- **Второе окно (`wx.Frame` или `wx.Dialog`)**  
  ```python
  second_frame = wx.Frame(frame, title="Второе окно")
  second_frame.Show()
  ```

#### **4. Разметка (`wx.Sizer`)**  
- **Вертикальный (`wx.BoxSizer`)**  
  ```python
  sizer = wx.BoxSizer(wx.VERTICAL)
  sizer.Add(wx.StaticText(frame, label="Текст"), 0, wx.ALL, 5)
  sizer.Add(wx.TextCtrl(frame), 0, wx.EXPAND | wx.ALL, 5)
  frame.SetSizer(sizer)
  ```

- **Сетка (`wx.GridSizer`)**  
  ```python
  sizer = wx.GridSizer(2, 2, 5, 5)  # 2 строки, 2 столбца, отступы 5px
  sizer.AddMany([(wx.Button(frame, label="1"), 0, wx.EXPAND),
                 (wx.Button(frame, label="2"), 0, wx.EXPAND)])
  frame.SetSizer(sizer)
  ```

#### **5. Работа с БД (SQLite + wxPython)**  
```python
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
conn.commit()

# Добавление данных
def add_to_db():
    name = text_ctrl.GetValue()
    cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
    conn.commit()
    wx.MessageBox("Данные сохранены!", "Успех")
```

#### **6. Кастомизация (цвета, шрифты, логотип)**  
- **Цвета**  
  ```python
  frame.SetBackgroundColour(wx.Colour(240, 240, 240))  # RGB
  button.SetBackgroundColour("#4CAF50")  # HEX
  ```

- **Шрифты**  
  ```python
  font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
  label.SetFont(font)
  ```

- **Логотип (иконка)**  
  ```python
  frame.SetIcon(wx.Icon("logo.png", wx.BITMAP_TYPE_PNG))
  ```

#### **7. Библиотека классов (пример)**  
```python
class MyForm(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Форма")
        self.panel = wx.Panel(self)
        self.setup_ui()

    def setup_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.text_ctrl = wx.TextCtrl(self.panel)
        sizer.Add(self.text_ctrl, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
```

---

### **Итог**  
- Используйте `wx.Frame` для окон, `wx.Panel` для группировки элементов.  
- Для разметки — `wx.BoxSizer` и `wx.GridSizer`.  
- Для работы с БД — `sqlite3` или другие библиотеки.  
- Кастомизируйте через `SetBackgroundColour`, `SetFont`, `SetIcon`.  

Теперь можно приступать к разработке! 🚀
