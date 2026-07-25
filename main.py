import json, os
from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.core.text import LabelBase

import arabic_reshaper
from bidi.algorithm import get_display

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "font.ttf")
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")

# تسجيل الخط العربي افتراضياً لكافة العناصر
if os.path.exists(FONT_PATH):
    LabelBase.register(name="Roboto", fn_regular=FONT_PATH)

def ar(text):
    if not text:
        return ""
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except:
        return text

FILE_NAME = os.path.join(BASE_DIR, "dukan_data.json")

def load_data():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"items": [], "debtors": []}

def save_data(data):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        if os.path.exists(LOGO_PATH):
            layout.add_widget(Image(source=LOGO_PATH, size_hint=(1, None), height=140, allow_stretch=True))
            
        layout.add_widget(Label(text=ar("أهلاً وسهلاً بكم في تطبيق دُكان"), font_size='22sp', halign="center"))
        layout.add_widget(Label(text=ar("إدارة المواد والأسعار ودفتر الديون"), font_size='16sp', halign="center"))
        
        btn1 = Button(text=ar("1. قائمة المواد والأسعار"), size_hint=(1, None), height=50, background_color=(0.2, 0.6, 1, 1))
        btn1.bind(on_release=lambda x: setattr(self.manager, 'current', 'items'))
        
        btn2 = Button(text=ar("2. دفتر الدين وسجل السداد"), size_hint=(1, None), height=50, background_color=(0.2, 0.6, 1, 1))
        btn2.bind(on_release=lambda x: setattr(self.manager, 'current', 'debtors'))
        
        btn3 = Button(text=ar("3. تقرير الصندوق والديون"), size_hint=(1, None), height=50, background_color=(0.2, 0.6, 1, 1))
        btn3.bind(on_release=lambda x: setattr(self.manager, 'current', 'reports'))
        
        layout.add_widget(btn1)
        layout.add_widget(btn2)
        layout.add_widget(btn3)
        self.add_widget(layout)

class ItemsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        top_bar = BoxLayout(size_hint=(1, None), height=40)
        btn_back = Button(text=ar("رجوع"), size_hint=(0.25, 1))
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        top_bar.add_widget(Label(text=ar("قائمة المواد والأسعار"), font_size='18sp'))
        top_bar.add_widget(btn_back)
        
        self.input_name = TextInput(hint_text=ar("اسم المادة"), multiline=False, size_hint=(1, None), height=40)
        self.input_wholesale = TextInput(hint_text=ar("سعر الجملة"), multiline=False, size_hint=(1, None), height=40)
        self.input_retail = TextInput(hint_text=ar("سعر المفرد"), multiline=False, size_hint=(1, None), height=40)
        
        btn_save = Button(text=ar("حفظ المادة"), size_hint=(1, None), height=45, background_color=(0.2, 0.8, 0.4, 1))
        btn_save.bind(on_release=self.add_item)
        
        layout.add_widget(top_bar)
        layout.add_widget(self.input_name)
        layout.add_widget(self.input_wholesale)
        layout.add_widget(self.input_retail)
        layout.add_widget(btn_save)
        
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        self.add_widget(layout)

    def on_enter(self): self.refresh_list()
    def refresh_list(self):
        self.grid.clear_widgets()
        db = load_data()
        for item in db["items"]:
            txt = f"{item['name']} - مفرد: {item['retail']} - جملة: {item['wholesale']}"
            self.grid.add_widget(Label(text=ar(txt), size_hint_y=None, height=40))

    def add_item(self, instance):
        name, w, r = self.input_name.text.strip(), self.input_wholesale.text.strip(), self.input_retail.text.strip()
        if name and w and r:
            db = load_data()
            db["items"].append({"name": name, "wholesale": w, "retail": r, "date": datetime.now().strftime("%Y-%m-%d")})
            save_data(db)
            self.input_name.text = ""; self.input_wholesale.text = ""; self.input_retail.text = ""
            self.refresh_list()

class DebtorsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        top_bar = BoxLayout(size_hint=(1, None), height=40)
        btn_back = Button(text=ar("رجوع"), size_hint=(0.25, 1))
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        top_bar.add_widget(Label(text=ar("دفتر الديون"), font_size='18sp'))
        top_bar.add_widget(btn_back)
        
        self.input_dname = TextInput(hint_text=ar("اسم المدين"), multiline=False, size_hint=(1, None), height=40)
        self.input_ditems = TextInput(hint_text=ar("المواد المشتراة"), multiline=False, size_hint=(1, None), height=40)
        self.input_damount = TextInput(hint_text=ar("المبلغ المطلوب"), multiline=False, size_hint=(1, None), height=40)
        
        btn_save = Button(text=ar("تسجيل الدين"), size_hint=(1, None), height=45, background_color=(0.2, 0.8, 0.4, 1))
        btn_save.bind(on_release=self.add_debtor)
        
        layout.add_widget(top_bar)
        layout.add_widget(self.input_dname)
        layout.add_widget(self.input_ditems)
        layout.add_widget(self.input_damount)
        layout.add_widget(btn_save)
        
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        self.add_widget(layout)

    def on_enter(self): self.refresh_list()
    def refresh_list(self):
        self.grid.clear_widgets()
        db = load_data()
        for d in db["debtors"]:
            txt = f"{d['name']} - المتبقي: {d['amount']} - المواد: {d['items']}"
            self.grid.add_widget(Label(text=ar(txt), size_hint_y=None, height=40))

    def add_debtor(self, instance):
        name, items, amount = self.input_dname.text.strip(), self.input_ditems.text.strip(), self.input_damount.text.strip()
        if name and amount:
            db = load_data()
            db["debtors"].append({"name": name, "items": items, "amount": float(amount)})
            save_data(db)
            self.input_dname.text = ""; self.input_ditems.text = ""; self.input_damount.text = ""
            self.refresh_list()

class ReportsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        top_bar = BoxLayout(size_hint=(1, None), height=40)
        btn_back = Button(text=ar("رجوع"), size_hint=(0.25, 1))
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        top_bar.add_widget(Label(text=ar("التقارير والصندوق"), font_size='18sp'))
        top_bar.add_widget(btn_back)
        layout.add_widget(top_bar)
        
        self.lbl_items = Label(font_size='16sp')
        self.lbl_debtors = Label(font_size='16sp')
        self.lbl_total = Label(font_size='18sp', color=(1, 0.3, 0.3, 1))
        
        layout.add_widget(self.lbl_items)
        layout.add_widget(self.lbl_debtors)
        layout.add_widget(self.lbl_total)
        self.add_widget(layout)

    def on_enter(self):
        db = load_data()
        total_debts = sum(d["amount"] for d in db["debtors"])
        self.lbl_items.text = ar(f"إجمالي عدد المواد: {len(db['items'])}")
        self.lbl_debtors.text = ar(f"إجمالي عدد الأشخاص بالدفتر: {len(db['debtors'])}")
        self.lbl_total.text = ar(f"إجمالي مبالغ الديون: {total_debts}")

class DukanApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(ItemsScreen(name='items'))
        sm.add_widget(DebtorsScreen(name='debtors'))
        sm.add_widget(ReportsScreen(name='reports'))
        return sm

if __name__ == "__main__":
    DukanApp().run()
