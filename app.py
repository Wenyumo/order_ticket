import sys
import os
import threading
import time
from datetime import datetime, timedelta
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import get_vehicle_list, get_reserved_seats, create_order
from config import ROUTES

ROUTES_LIST = ROUTES

class VehicleItem(RecycleDataViewBehavior, BoxLayout):
    idx = ''
    vehicle_id = ''
    time = ''
    student_price = ''
    teacher_price = ''
    seats = ''
    index = None
    selected = BooleanProperty(False)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(VehicleItem, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(VehicleItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.select_vehicle(touch):
            return True

    def select_vehicle(self, touch=None):
        app = App.get_running_app()
        if hasattr(app, 'root') and hasattr(app.root, 'select_vehicle'):
            app.root.select_vehicle(self.vehicle_id, self.time)
        return True

class ConfigScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(ConfigScreen, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10

        title = Label(text='配置设置', size_hint_y=None, height=50, font_size=24, bold=True)
        self.add_widget(title)

        store = JsonStore('config.json')
        
        api_key = store.get('api_key', {}).get('value', '')
        user_id = store.get('user_id', {}).get('value', '')
        cookie = store.get('cookie', {}).get('value', '')
        xsrf = store.get('xsrf', {}).get('value', '')

        self.api_key_input = TextInput(text=api_key, size_hint_y=None, height=40, multiline=False)
        self.user_id_input = TextInput(text=user_id, size_hint_y=None, height=40, multiline=False)
        self.cookie_input = TextInput(text=cookie, size_hint_y=None, height=80, multiline=True)
        self.xsrf_input = TextInput(text=xsrf, size_hint_y=None, height=40, multiline=False)

        self.add_widget(Label(text='API_KEY:', size_hint_y=None, height=30))
        self.add_widget(self.api_key_input)
        self.add_widget(Label(text='USER_ID:', size_hint_y=None, height=30))
        self.add_widget(self.user_id_input)
        self.add_widget(Label(text='COOKIE_STR:', size_hint_y=None, height=30))
        self.add_widget(self.cookie_input)
        self.add_widget(Label(text='XSRF_TOKEN:', size_hint_y=None, height=30))
        self.add_widget(self.xsrf_input)

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        save_btn = Button(text='保存配置', on_press=self.save_config)
        back_btn = Button(text='返回', on_press=self.dismiss)
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(back_btn)
        self.add_widget(btn_layout)

    def save_config(self, instance):
        store = JsonStore('config.json')
        store.put('api_key', value=self.api_key_input.text)
        store.put('user_id', value=self.user_id_input.text)
        store.put('cookie', value=self.cookie_input.text)
        store.put('xsrf', value=self.xsrf_input.text)
        
        popup = Popup(title='成功', content=Label(text='配置保存成功！'), size_hint=(0.8, 0.3))
        popup.open()

    def dismiss(self, instance):
        self.parent.remove_widget(self)

class TicketApp(BoxLayout):
    def __init__(self, **kwargs):
        super(TicketApp, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.vehicles = []
        self.selected_vehicle = None
        self.running = False
        self.stop_flag = False
        self.booking_thread = None
        self.cached_free_seats = []

        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        route_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=150, padding=5, spacing=5)
        route_layout.add_widget(Label(text='1. 选择路线', size_hint_y=None, height=30, font_size=16, bold=True))
        
        row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        row1.add_widget(Label(text='路线:', size_hint_x=None, width=60))
        self.route_spinner = Spinner(text='请选择路线', values=ROUTES_LIST, size_hint_x=1)
        row1.add_widget(self.route_spinner)
        row1.add_widget(Label(text='日期:', size_hint_x=None, width=60))
        self.date_input = TextInput(text=datetime.now().strftime('%Y-%m-%d'), size_hint_x=None, width=120, multiline=False)
        row1.add_widget(self.date_input)
        row1.add_widget(Button(text='查询', size_hint_x=None, width=80, on_press=self.query_vehicles))
        row1.add_widget(Button(text='配置', size_hint_x=None, width=80, on_press=self.open_config))
        route_layout.add_widget(row1)
        self.add_widget(route_layout)

        vehicle_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=250, padding=5, spacing=5)
        vehicle_layout.add_widget(Label(text='2. 选择班次', size_hint_y=None, height=30, font_size=16, bold=True))
        self.vehicle_list = RecycleView()
        self.vehicle_list.data = []
        self.vehicle_list.layout_manager = RecycleBoxLayout(default_size=None, default_size_hint=1, None, size_hint_y=None, height=self.minimum_height, orientation='vertical')
        vehicle_layout.add_widget(self.vehicle_list)
        self.add_widget(vehicle_layout)

        control_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=120, padding=5, spacing=5)
        control_layout.add_widget(Label(text='3. 抢票控制', size_hint_y=None, height=30, font_size=16, bold=True))
        
        btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.start_button = Button(text='开始抢票', disabled=True, on_press=self.start_booking)
        self.stop_button = Button(text='停止', disabled=True, on_press=self.stop_booking)
        btn_row.add_widget(self.start_button)
        btn_row.add_widget(self.stop_button)
        control_layout.add_widget(btn_row)
        
        self.status_label = Label(text='状态: 未选择班次', size_hint_y=None, height=30, color=(0, 0, 1, 1))
        control_layout.add_widget(self.status_label)
        self.add_widget(control_layout)

        log_layout = BoxLayout(orientation='vertical', padding=5, spacing=5)
        log_layout.add_widget(Label(text='运行日志', size_hint_y=None, height=30, font_size=16, bold=True))
        scroll = ScrollView()
        self.log_text = TextInput(text='', readonly=True, size_hint_y=None, height=200, font_size=12)
        scroll.add_widget(self.log_text)
        log_layout.add_widget(scroll)
        self.add_widget(log_layout)

    def load_config(self):
        try:
            store = JsonStore('config.json')
            api_key = store.get('api_key', {}).get('value', '')
            user_id = store.get('user_id', {}).get('value', '')
            cookie = store.get('cookie', {}).get('value', '')
            xsrf = store.get('xsrf', {}).get('value', '')
            
            if api_key and user_id and cookie and xsrf:
                import config
                config.API_KEY = api_key
                config.USER_ID = user_id
                config.COOKIE_STR = cookie
                config.XSRF_TOKEN_HEADER = xsrf
        except:
            pass

    def log(self, msg):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.text += f'[{timestamp}] {msg}\n'
        Clock.schedule_once(lambda dt: setattr(self.log_text, 'cursor', (len(self.log_text.text), 0)), 0)

    def open_config(self, instance):
        config_screen = ConfigScreen()
        self.add_widget(config_screen)

    def query_vehicles(self, instance):
        route = self.route_spinner.text
        date = self.date_input.text
        if not route or not date or route == '请选择路线':
            self.log('请选择路线和日期')
            return

        self.log(f'正在查询 {date} {route} 的班次...')
        self.vehicles = []
        self.selected_vehicle = None
        self.vehicle_list.data = []
        self.start_button.disabled = True
        self.status_label.text = '状态: 未选择班次'

        result = get_vehicle_list(date, route)
        if isinstance(result, dict) and 'error' in result:
            self.log(f'查询失败：{result["error"]}')
            return

        if not result:
            self.log('未查询到任何班次')
            return

        self.vehicles = result
        data = []
        for idx, v in enumerate(result, 1):
            data.append({
                'idx': str(idx),
                'vehicle_id': v.get('id', ''),
                'time': v.get('origin_time', '未知'),
                'student_price': v.get('student_ticket_price', 'N/A'),
                'teacher_price': v.get('teacher_ticket_price', 'N/A'),
                'seats': v.get('reservation_num_able', '?')
            })
        self.vehicle_list.data = data
        self.log(f'查询成功，共 {len(result)} 个班次')

    def select_vehicle(self, vehicle_id, time):
        for v in self.vehicles:
            if v.get('id') == vehicle_id:
                self.selected_vehicle = v
                self.start_button.disabled = False
                self.status_label.text = f'状态: 已选择 {time} 班次'
                self.log(f'选中班次：{time} (ID:{vehicle_id})')
                return

    def start_booking(self, instance):
        if not self.selected_vehicle:
            self.log('请先选择一个班次')
            return
        if self.running:
            self.log('抢票已在运行中')
            return

        self.running = True
        self.stop_flag = False
        self.start_button.disabled = True
        self.stop_button.disabled = False
        self.log('启动抢票线程...')
        self.booking_thread = threading.Thread(target=self.booking_worker, daemon=True)
        self.booking_thread.start()

    def stop_booking(self, instance):
        self.stop_flag = True
        self.log('正在停止抢票...')

    def booking_worker(self):
        vehicle = self.selected_vehicle
        vehicle_id = vehicle.get('id')
        origin_time_str = vehicle.get('origin_time')
        date = self.date_input.text
        
        try:
            departure = datetime.strptime(f'{date} {origin_time_str}', '%Y-%m-%d %H:%M')
        except Exception as e:
            self.log(f'时间解析错误：{e}')
            self.stop_booking_done()
            return
        
        sale_time = departure - timedelta(hours=1)
        now = datetime.now()

        if now < sale_time:
            wait_seconds = (sale_time - now).total_seconds()
            self.log(f'当前时间 {now.strftime("%H:%M:%S")}，开售时间 {sale_time.strftime("%H:%M:%S")}')
            self.log(f'等待 {wait_seconds:.2f} 秒...')
            
            pre_wait = max(0, wait_seconds - 2)
            if pre_wait > 0:
                time.sleep(pre_wait)
            
            self.log('开售前预查询座位信息...')
            seat_result = get_reserved_seats(vehicle_id, date)
            if not seat_result.get('success'):
                self.log(f'预查询座位失败：{seat_result.get("error")}')
            else:
                reserved = set(seat_result['reserved'])
                disabled = set(seat_result['disabled'])
                max_seat = vehicle.get('reservation_num_able', 51)
                self.cached_free_seats = []
                for seat in range(1, max_seat + 1):
                    if seat not in reserved and seat not in disabled:
                        self.cached_free_seats.append(seat)
                self.log(f'预查询到 {len(self.cached_free_seats)} 个空闲座位')
            
            self.log('进入最后冲刺等待...')
            while datetime.now() < sale_time:
                time.sleep(0.001)
            self.log('开售时间到！立即抢票！')
        else:
            self.log('当前时间已过开售时间，立即开始抢票！')
            self.cached_free_seats = []

        seat_number = None
        retry_count = 0

        if self.cached_free_seats:
            self.log(f'使用预缓存座位列表，第一个候选座位：{self.cached_free_seats[0]}')

        while not self.stop_flag:
            if self.cached_free_seats:
                seat_number = self.cached_free_seats.pop(0)
                self.log(f'尝试使用缓存座位 {seat_number} 下单...')
            else:
                self.log('正在实时获取空闲座位...')
                seat_result = get_reserved_seats(vehicle_id, date)
                if not seat_result.get('success'):
                    self.log(f'获取座位失败：{seat_result.get("error")}')
                    if 'Cookie' in seat_result.get('error', ''):
                        self.log('Cookie可能已过期，请重新获取并更新配置')
                        break
                    time.sleep(0.2)
                    continue
                
                reserved = set(seat_result['reserved'])
                disabled = set(seat_result['disabled'])
                max_seat = vehicle.get('reservation_num_able', 51)
                free_seats = [s for s in range(1, max_seat + 1) if s not in reserved and s not in disabled]
                
                if not free_seats:
                    self.log('无空闲座位，等待0.2秒后重试')
                    time.sleep(0.2)
                    continue
                
                seat_number = free_seats[0]
                self.cached_free_seats = free_seats[1:]

            referer = f'http://hqapp1.bit.edu.cn/newbanche/choose?id={vehicle_id}&shuttleType=3&serviceTime=1,2,3,4,5&originTime={origin_time_str.replace(":", "%3A")}&price={vehicle.get("student_ticket_price", "")}'
            order_result = create_order(vehicle_id, date, seat_number, referer)
            
            if order_result.get('code') == '1':
                self.log(f'抢票成功！订单已创建，座位号 {seat_number}。请尽快登录系统支付。')
                break
            else:
                error_msg = order_result.get('message', '未知错误')
                self.log(f'下单失败（座位{seat_number}）：{error_msg}')
                
                if '已预约' in error_msg or '已被预约' in error_msg:
                    self.log('座位已被占，尝试下一个候选座位')
                    continue
                elif '未开启预约' in error_msg or '发车前一个小时' in error_msg:
                    self.log('尚未到可预约时间，等待0.5秒后重试')
                    time.sleep(0.5)
                    continue
                else:
                    retry_count += 1
                    if retry_count > 10:
                        self.log('连续失败次数过多，停止抢票')
                        break
                    time.sleep(0.2)
        else:
            self.log('抢票已停止')
        
        self.stop_booking_done()

    def stop_booking_done(self):
        self.running = False
        self.stop_flag = False
        self.start_button.disabled = False if self.selected_vehicle else True
        self.stop_button.disabled = True
        self.log('抢票线程已结束')

class TicketAppMain(App):
    def build(self):
        return TicketApp()

    def on_stop(self):
        if hasattr(self.root, 'booking_thread') and self.root.booking_thread:
            self.root.stop_flag = True

if __name__ == '__main__':
    TicketAppMain().run()
