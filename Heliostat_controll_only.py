import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog as fd
import tk_tools
from PIL import Image, ImageTk
import datetime
from datetime import datetime
import math
import socket 
import json
import time
import threading
import csv
import requests
from concurrent.futures import ThreadPoolExecutor
import webbrowser

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        #----------------------------------- global_variable -----------------------------------#
        self.is_true = False #check position in target
        self.state = True
        self.status = 1
        self.status_run = 0
        self.trackbar_length = 350
        self.data = {}
        self.color = (255, 0, 0)
        #---------------------------------------  variable   -----------------------------------#
        self.speed_manual = tk.IntVar(value=400)
        self.clicked = tk.StringVar()

        self.url_list = ["http://192.168.0.106/"] 
        ### Here_is send command to heliostat ###
        self.url_request_update = ["http://192.168.0.106/update-data"]
        ### Here_is send command to heliostat in auto mode ###
        self.url_request_auto = ["http://192.168.0.106/auto-data"]
        self.url_update_rtc = ["http://192.168.0.106/update-rtc"]

        self.path_data_log = 'F:\\Program PLC\\Solar_thermal_Project\\data_log\\'+f'calibrate_position_id_0_{datetime.now().strftime("%d_%m_%Y")}'+'.csv'
        self.path_recv_log = 'F:\\Program PLC\\Solar_thermal_Project\\data_log\\'+f'recv_position_id_0_{datetime.now().strftime("%d_%m_%Y")}.csv'

        self.state_change = True

        self.list_ip_clients = {'0': '192.168.1.110',
                                '1': '192.168.1.111'}
        
        self.all_connections = []
        self.all_address = []
        self.data_list = []
        self.tabControl = ttk.Notebook(self)
        
        #create tab
        self.calibrate_tab = ttk.Frame(self.tabControl)
        self.monitor_tab = ttk.Frame(self.tabControl)
        
        #add tab
        
        #Calibrate tab
        self.top_frame = tk.LabelFrame(self.calibrate_tab, font=('Arial', 18), bg='gray' )
        self.top_frame.pack(side="top", fill="both", expand=True)
        
        self.bottom_frame = tk.LabelFrame(self.calibrate_tab, font=('Arial', 18), bg='gray' )
        self.bottom_frame.pack(side="top", fill="both", expand=False)
        
        #Monitor tab
        self.top_frame_in_monitor = tk.LabelFrame(self.monitor_tab, font=('Arial', 18), bg='gray' )
        self.top_frame_in_monitor.pack(side="top", fill="both", expand=True)

        self.monitor_heliostat = tk.LabelFrame(self.top_frame_in_monitor, text="Heliostat", font=('Arial', 16),  bg='gray')
        self.monitor_heliostat.pack(side=tk.LEFT, fill='both', expand=True)

        #Widget in top frame Calibrate
        self.right_frame = tk.LabelFrame(self.top_frame, text="IP Camera", font=('Arial', 14), bg='gray' )
        self.right_frame.pack(side='left', fill='both', expand=True)
        
        #Camera tap
        self.ip_cam_tap = ttk.Notebook(self.right_frame)
        self.camera_tap1 = ttk.Frame(self.ip_cam_tap)
        self.camera_tap2 = ttk.Frame(self.ip_cam_tap)
        self.ip_cam_tap.add(self.camera_tap1, text ='Camera1')
        self.ip_cam_tap.pack(expand = 1, fill ="both")
        
        #----------------------------------------  Video Frame  ----------------------------------------#
        
        #----------------------------------- Create canvas for image -----------------------------------#
        self.calibrate_frame = tk.Canvas(self.camera_tap1, width=640, height=480)
        self.calibrate_frame.pack()
        
        self.table_frame = tk.LabelFrame(self.top_frame, font=('Arial', 14), bg='gray')
        self.table_frame.pack(side='left', fill='both', expand=True)
        
        #----------------------------------- Create canvas for image -----------------------------------#        
        self.control_bar = tk.LabelFrame(self.top_frame, text="Control", font=('Arial', 14),  bg='gray' )
        self.control_bar.pack(side='left', fill='both', expand=True)
        
        self.top_frame_in_cnt = tk.LabelFrame(self.control_bar, font=('Arial', 18), bg='gray' )
        self.top_frame_in_cnt.pack(side="top", fill="both", expand=True)
        self.bottom_frame_in_cnt = tk.LabelFrame(self.control_bar, font=('Arial', 18), bg='gray' )
        self.bottom_frame_in_cnt.pack(side=tk.LEFT, fill='x', expand=True)
        
        #----------------------------------- widget in bouttom frame -----------------------------------#
        self.tool_bar = tk.LabelFrame(self.bottom_frame, text="Threshold", font=('Arial', 14),  bg='gray' )
        self.tool_bar.pack(side=tk.LEFT, fill='both',  expand=True)
        
        #----------------------------------- table data sensor -----------------------------------------#
        self.columns_name = ('ID', 'position x', 'position y', 'error x', 'error y', 'elevation', 'azimuth')
        self.tabview = ttk.Treeview(self.table_frame, columns=self.columns_name, show='headings')
        self.tabview.heading('ID', text='ID')
        self.tabview.heading('position x', text='Position X')
        self.tabview.heading('position y', text='Position Y')
        self.tabview.heading('error x', text='Error X')
        self.tabview.heading('error y', text='Error Y')
        self.tabview.heading('elevation', text='Elevation')
        self.tabview.heading('azimuth', text='Azimuth')
        self.tabview.column('ID', width=10, anchor=tk.CENTER)
        self.tabview.column('position x', width=60, anchor=tk.CENTER)
        self.tabview.column('position y', width=60, anchor=tk.CENTER)
        self.tabview.column('error x', width=60, anchor=tk.CENTER)
        self.tabview.column('error y', width=60, anchor=tk.CENTER)
        self.tabview.column('elevation', width=60, anchor=tk.CENTER)
        self.tabview.column('azimuth', width=60, anchor=tk.CENTER)

        self.tabview.pack(fill='both', expand=True, padx=5, pady=5)
        self.tabview.bind('<Button-1>', self.select_item)
        
        #----------------------------------- Setting Connection ----------------------------------------#
        
        #-------------------------------------- Create Dropdown menu -----------------------------------#

        #------------------------------------------ open file button -----------------------------------#
        self.cnt_frame2 = tk.Frame(self.top_frame_in_cnt, bg='blue')
        self.cnt_frame2.pack(side='left', fill='both', expand=True)
        
        cnt_frame1 = tk.Frame(self.bottom_frame_in_cnt, bg='#1EA1FF')
        cnt_frame1.pack(side='left', fill='both', expand=True)
        
        #----------------------------------- load image -----------------------------------#

        #----------------------------------- trackbar -----------------------------------#

        self.off_set = ttk.Scale(self.tool_bar, from_=0, to=100, length=self.trackbar_length, orient=tk.HORIZONTAL, command=self.slider_changed)
        self.off_set.grid(row=6, column=3, padx=0, pady=0)
        self.off_set.set(4)

        #-----------------------------------  Crop_Image  -----------------------------------#

        #--------------------------------- Button_Widget -------------------------------------#
        btn_frame = tk.LabelFrame(cnt_frame1,  bg='#1EA1FF', borderwidth=0)
        btn_frame.pack(side=tk.LEFT, fill='y', expand=True, pady=25)
        manual_frame = tk.LabelFrame(cnt_frame1,  bg='#1EA1FF', borderwidth=0)
        manual_frame.pack(side=tk.LEFT, fill='x', expand=True)

        #--------------------------------- Button_Box -----------------------------------------#
        self.box_input = tk.LabelFrame(manual_frame, bg='#1EA1FF', borderwidth=0)
        self.box_input.grid(row=0, column=1, )
        self.text_input = tk.Text(self.box_input, height=1, width=7, font=('Arial', 14), )
        self.text_input.grid(row=0, column=1, padx=2.5, pady=2.5)
        self.speed_input = tk.Entry(self.box_input,  width=7, font=('Arial', 14), textvariable=self.speed_manual,)
        self.speed_input.grid(row=1, column=1, padx=2.5, pady=2.5)
        self.led_origin_x = tk_tools.Led(self.box_input, size=22, bg='#1EA1FF')
        self.led_origin_x.grid(row=0, column=3, padx=2.5, pady=2.5)
        self.led_origin_y = tk_tools.Led(self.box_input, size=22, bg='#1EA1FF')
        self.led_origin_y.grid(row=1, column=3, padx=2.5, pady=2.5)
        self.led_limit_safety = tk_tools.Led(self.box_input, size=22, bg='#1EA1FF')
        self.led_limit_safety.grid(row=2, column=5, padx=2.5, pady=2.5)

  #---------------------------------------------- Test in tab monitor----------------------------------------------------------------# 
        
        self.led_origin_x_monitor_tab = tk_tools.Led(self.monitor_heliostat, size=22, bg='gray')
        self.led_origin_x_monitor_tab.grid(row=2, column=2, padx=2.5, pady=2.5)
        self.led_origin_y_monitor_tab = tk_tools.Led(self.monitor_heliostat, size=22, bg='gray')
        self.led_origin_y_monitor_tab.grid(row=2, column=3, padx=2.5, pady=2.5)
        self.led_safety_posX_monitor_tab = tk_tools.Led(self.monitor_heliostat, size=22, bg='gray')
        self.led_safety_posX_monitor_tab.grid(row=2, column=4, padx=2.5, pady=2.5)
        self.led_safety_posY_monitor_tab = tk_tools.Led(self.monitor_heliostat, size=22, bg='gray')
        self.led_safety_posY_monitor_tab.grid(row=2, column=5, padx=2.5, pady=2.5)
        self.led_limit_safety_monitor_tab = tk_tools.Led(self.monitor_heliostat, size=22, bg='gray')
        self.led_limit_safety_monitor_tab.grid(row=2, column=6, padx=2.5, pady=2.5)
        self.led_path_status_monitor_tab = tk_tools.Led(self.monitor_heliostat, size=22, bg='gray')
        self.led_path_status_monitor_tab.grid(row=2, column=7, padx=2.5, pady=2.5)

        self.led_origin_x1_monitor_tab = tk_tools.Led(self.monitor_heliostat, size=22, bg='gray')
        self.led_origin_x1_monitor_tab.grid(row=3, column=2, padx=2.5, pady=2.5)
        self.led_origin_y1_monitor_tab = tk_tools.Led(self.monitor_heliostat, size=22, bg='gray')
        self.led_origin_y1_monitor_tab.grid(row=3, column=3, padx=2.5, pady=2.5)
        self.led_safety_posX1_monitor_tab = tk_tools.Led(self.monitor_heliostat, size=22, bg='gray')
        self.led_safety_posX1_monitor_tab.grid(row=3, column=4, padx=2.5, pady=2.5)
        self.led_safety_posY1_monitor_tab = tk_tools.Led(self.monitor_heliostat, size=22, bg='gray')
        self.led_safety_posY1_monitor_tab.grid(row=3, column=5, padx=2.5, pady=2.5)
        self.led_limit_safety1_monitor_tab = tk_tools.Led(self.monitor_heliostat, size=22, bg='gray')
        self.led_limit_safety1_monitor_tab.grid(row=3, column=6, padx=2.5, pady=2.5)
        self.led_path_status1_monitor_tab = tk_tools.Led(self.monitor_heliostat, size=22, bg='gray')
        self.led_path_status1_monitor_tab.grid(row=3, column=7, padx=2.5, pady=2.5)
#--------------------------------------------------------------------------------------------------------------------------------------------------#

        self.origin_x = tk.Button(btn_frame, text='Origin X', bg='yellow', font=('Arial', 12), width=8 )
        self.origin_x.grid(row=3, column=0, pady=5)
        self.origin_x.bind('<Button-1>', self.check_button)

        self.origin_y = tk.Button(btn_frame, text='Origin Y', bg='yellow', font=('Arial', 12), width=8 )
        self.origin_y.grid(row=3, column=1, pady=5)
        self.origin_y.bind('<Button-1>', self.check_button)

        self.stop = tk.Button(btn_frame, text='stop', bg='red', font=('Arial', 12), width=18, height=2 )
        self.stop.grid(row=4, column=0, columnspan=2, padx=5, pady=5 )
        self.stop.bind('<Button-1>', self.check_button )

        #--------------------------------- **** current_position_label -----------------------------------------#        
        self.led = tk_tools.Led(self.cnt_frame2, size=50, bg='blue')
        self.led.grid(row=0, column=2, columnspan=2)
        self.led.to_grey(on=True)
        #--------------------------------- **** PID_Parameter -----------------------------------------#
        #---------------------------------------- **** Set_points_X_Y_speed  -----------------------------------------#
        self.max_speed.set(200)
        #----------------------------------------- **** off_set_x_y_calibarte -----------------------------------------#
        self.off_set_x = tk.Text(self.cnt_frame2, height=1, width=10, font=('Arial', 12), )
        self.off_set_x.grid(row=5, column=1, pady=2.5)
        self.off_set_y = tk.Text(self.cnt_frame2, height=1, width=10, font=('Arial', 12), )
        self.off_set_y.grid(row=6, column=1, padx=5, pady=2.5)

        #----------------------------------------- **** off_set_x_y_receiver -----------------------------------------#
        self.off_set_x_recv = tk.Text(self.cnt_frame2, height=1, width=10, font=('Arial', 12), )
        self.off_set_x_recv.grid(row=5, column=3, pady=2.5)

        self.off_set_y_recv = tk.Text(self.cnt_frame2, height=1, width=10, font=('Arial', 12), )
        self.off_set_y_recv.grid(row=6, column=3, padx=5, pady=2.5)

        #----------------- check status LED from Heliostat ---------------------------------------#
        self.current_id = 0

        self.status_limit_id0 = 0
        self.status_xneg_id0 = 0
        self.status_yneg_id0 = 0
        self.status_xpos_id0 = 0
        self.status_ypos_id0 = 0
        self.status_path_id0 = 0

        self.status_limit_id1 = 0
        self.status_xneg_id1 = 0
        self.status_yneg_id1 = 0
        self.status_xpos_id1 = 0
        self.status_ypos_id1 = 0
        self.status_path_id1 = 0

        self.mainloop()  #Starts GUI

    ### Here_is Sending data to heliostat? ###
    def set_off_set(self):
        conn = self.get_client(self.clicked.get())
        payload = {'state': 'off_set', 'x': self.off_set_x_recv.get(0.1, "end-1c"), 'y': self.off_set_y_recv.get(0.1, "end-1c")}
        payload = json.dumps(payload)
        payload = f'{payload}\n'
        
    ### Here_is Sending data to heliostat? ###
    def set_off_set_recv(self):
        payload = {'topic': 'off_set_scale', 'x': self.off_set_x.get(0.1, "end-1c"), 'y': self.off_set_y.get(0.1, "end-1c")}
        print(payload)
        index = int(self.clicked.get().replace("select ",''))
        result = requests.post(self.url_request_update[index], json=payload, timeout=1)
        print(result.status_code)

    ### Here_is connect to server function ### 
    def bind_server(self):
        for url in self.url_list:
            try:
                result = requests.get(url , timeout=1)
                if result.status_code == 200:  self.led.to_green(on=True)
            
                payload = result.json()
                self.data_list.append(payload)
                #remove duplicate value
                new_list = list({
                                    dictionary['id'] : dictionary
                                    for dictionary in self.data_list
                                }.values())
                
                new_list = sorted(new_list, key=lambda d: d['id']) #sorte by id
                # print(new_list)

                if not self.state:
                    index = int(self.clicked.get().replace("select ",''))                 
                    for i in new_list:
                        if self.is_true: #check position in target
                            if i['id'] == index :
                                path = self.path_data_log if self.state_change else self.path_recv_log
                                # self.write_data(path, i['currentX'], i['currentY'], i['err_posx'], i['err_posy'])
                                self.write_csv(path, i['currentX'], i['currentY'], i['err_posx'], i['err_posy'])
                            else:
                                pass

                for i in self.tabview.get_children(): #clear data
                    try:
                        self.tabview.delete(i)
                    except Exception as e:
                        pass   

                for i, d in enumerate(new_list):
                    if d is not None: 
                        self.tabview.insert('', tk.END, values=[d['id'], d['currentX'], d['currentY'], d['err_posx'], d['err_posy'], d['elevation'], d['azimuth']])
                        #led  origin status

                    # LED monitor is ok
                        if i == 0:                        
                            if d['safety']['x'] : 
                                self.led_origin_x_monitor_tab.to_green(on=True)
                                self.status_xneg_id0 = 1
                            else : 
                                self.led_origin_x_monitor_tab.to_grey(on=True)
                                self.status_xneg_id0 = 0
                            if d['safety']['y'] : 
                                self.led_origin_y_monitor_tab.to_green(on=True)
                                self.status_yneg_id0 = 1
                            else : 
                                self.led_origin_y_monitor_tab.to_grey(on=True)
                                self.status_yneg_id0 = 0
                            if d['safety']['x1'] : 
                                self.led_safety_posX_monitor_tab.to_red(on=True)
                                self.status_xpos_id0 = 1
                            else : 
                                self.led_safety_posX_monitor_tab.to_grey(on=True)
                                self.status_xpos_id0 = 0
                            if d['safety']['y1'] : 
                                self.led_safety_posY_monitor_tab.to_red(on=True)
                                self.status_ypos_id0 = 1
                            else : 
                                self.led_safety_posY_monitor_tab.to_grey(on=True)
                                self.status_ypos_id0 =0
                            if d['safety']['ls1'] :
                                self.led_limit_safety_monitor_tab.to_red(on=True)
                                self.status_limit_id0 = 1
                            else : 
                                self.led_limit_safety_monitor_tab.to_grey(on=True)
                                self.status_limit_id0 = 0
                            if d['safety']['st_path'] : 
                                self.led_path_status_monitor_tab.to_yellow(on=True)
                                self.status_path_id0 = 1
                            else : 
                                self.led_path_status_monitor_tab.to_grey(on=True)
                                self.status_path_id0 = 0

                        if i == 1:                        
                            if d['safety']['x'] : 
                                self.led_origin_x1_monitor_tab.to_green(on=True)
                                self.status_xneg_id1 = 1
                            else : 
                                self.led_origin_x1_monitor_tab.to_grey(on=True)
                                self.status_xneg_id1 = 0
                            if d['safety']['y'] : 
                                self.led_origin_y1_monitor_tab.to_green(on=True)
                                self.status_yneg_id1 = 1
                            else : 
                                self.led_origin_y1_monitor_tab.to_grey(on=True)
                                self.status_yneg_id1 = 0
                            if d['safety']['x1'] : 
                                self.led_safety_posX1_monitor_tab.to_red(on=True)
                                self.status_xpos_id1 = 1
                            else : 
                                self.led_safety_posX1_monitor_tab.to_grey(on=True)
                                self.status_xpos_id1 = 0
                            if d['safety']['y1'] : 
                                self.led_safety_posY1_monitor_tab.to_red(on=True)
                                self.status_ypos_id1 = 1
                            else : 
                                self.led_safety_posY1_monitor_tab.to_grey(on=True)
                                self.status_ypos_id1 = 0
                            if d['safety']['ls1'] : 
                                self.led_limit_safety1_monitor_tab.to_red(on=True)
                                self.status_limit_id1 = 1
                            else : 
                                self.led_limit_safety1_monitor_tab.to_grey(on=True)
                                self.status_limit_id1 = 0
                            if d['safety']['st_path'] : 
                                self.led_path_status1_monitor_tab.to_yellow(on=True)
                                self.status_path_id1 = 1
                            else : 
                                self.led_path_status1_monitor_tab.to_grey(on=True)
                                self.status_path_id1 = 0
                    else: 
                        pass

            except requests.exceptions.HTTPError as errh: 
                print("HTTP Error") 
                # print(errh.args[0])
            except requests.exceptions.ReadTimeout as ee:
                self.led.to_yellow(on=True)
                print("Time Out")
            except requests.exceptions.ConnectionError as ee:
                # print(ee)
                self.led.to_red(on=True)
                print("Connection Error")
            except requests.exceptions.RequestException as errex: 
                print("Exception request")
        self.after(500, self.bind_server)

    ### Here_is starting server ### 
    def start_server_thread(self):
        self.bind_server()

    def get_client(self, client_id):
        id_ = client_id.replace("select ",'')
        ip = self.list_ip_clients[id_]
        if ip in self.all_address:
            index_ip = self.all_address.index(ip)
            conn = self.all_connections[index_ip]
            return conn
        else:
            return None
    #--------- set time ----------------------------------#

    def on_connect(self):  
        hour = datetime.now().strftime("%H")
        minute = datetime.now().strftime("%M")
        sec = datetime.now().strftime("%S")
        try:
            index = int(self.clicked.get().replace("select ",''))
            payload = {"topic": "rtc", 'hour': hour, 'minute': minute, 'sec':sec}
            result = requests.post(self.url_update_rtc[index], json=payload, timeout=1)
            if(result.status_code == 200):
                print(result.text)
                data = json.loads(result.text)
                messagebox.showinfo("Time", data['time'])
        except requests.exceptions.ReadTimeout as ee:
            print("Time Out")
        except requests.exceptions.ConnectionError as ee:
            print("Connection Error")
        except ValueError:
            messagebox.showerror("Error", "Select Client")
    
    def on_close(self): 
        self.current_id = int(self.clicked.get().replace("select ",''))
        print(self.current_id)

    ### Here_is send command to heliostat
    def path_call_back(self):
        try:
            index = int(self.clicked.get().replace("select ",''))
            print(index)
            payload = {"topic": "mode", "status": self.status_run, "speed":self.speed_input.get()}
            result = requests.post(self.url_request_update[index], json=payload, timeout=1)
            print(result.status_code)
            if not self.status_run:
                self.status_run = 1
                print("Path State: ", self.status_run)
            else:
                self.status_run = 0        
                print("Path State: ", self.status_run)

        except requests.exceptions.ReadTimeout as ee:
            print("Time Out")
        except requests.exceptions.ConnectionError as ee:
            print("Connection Error")
        except ValueError:
            messagebox.showerror("Error", " Please select client ")

    ### Here_is send command to heliostat in auto mode
    def feed_bcak(self, axis, cx, cy, kp, ki, kd, pos_x, pos_y, speed, off_set, status):
        try:
            index = int(self.clicked.get().replace("select ",''))
            payload = {'topic': 'auto', 'axis':axis, 'cx': cx, 'cy': cy, 'target_x': pos_x, 'target_y': pos_y,
                'kp': kp, 'ki': ki, 'kd': kd, 'max_speed': speed, 'off_set':off_set, "status": status}
            result = requests.post(self.url_request_auto[index], json=payload,)
        except requests.exceptions.ReadTimeout as ee:
                print("Time Out")
        except requests.exceptions.ConnectionError as ee:
            print("Connection Error")

    ### Here_is Send data that btn control to heliostat ### 
    def check_button(self, event):
        try:
            payload = {}
            index = int(self.clicked.get().replace("select ",''))
            if self.state:
                if event.widget['text'] == "up":
                    payload = {"topic": "up", "step": self.text_input.get(0.1, "end-1c"),"speed": self.speed_manual.get(), "speed_y": int(self.speed_manual.get())}
                elif event.widget['text'] == "down":
                    payload = {"topic": "down", "step": self.text_input.get(0.1, "end-1c"),"speed":self.speed_manual.get(), "speed_y": int(self.speed_manual.get())}         
                elif event.widget['text'] == "forward":
                    payload = {"topic": "reverse", "step": self.text_input.get(0.1, "end-1c"),"speed":self.speed_manual.get(), "speed_y": int(self.speed_manual.get())}              
                elif event.widget['text'] == "reverse":
                    payload = {"topic": "forward", "step": self.text_input.get(0.1, "end-1c"),"speed":self.speed_manual.get(), "speed_y": int(self.speed_manual.get())}           
                elif event.widget['text'] == "top_left":
                    payload = {"topic": "top_left", "step": self.text_input.get(0.1, "end-1c"),"speed":self.speed_manual.get(), "speed_y": int(self.speed_manual.get())}           
                elif event.widget['text'] == "top_right":
                    payload = {"topic": "top_right", "step": self.text_input.get(0.1, "end-1c"),"speed":self.speed_manual.get(), "speed_y": int(self.speed_manual.get())}            
                elif event.widget['text'] == "bottom_left":
                    payload = {"topic": "bottom_right", "step": self.text_input.get(0.1, "end-1c"),"speed":self.speed_manual.get(), "speed_y": int(self.speed_manual.get())}           
                elif event.widget['text'] == "bottom_right":
                    payload = {"topic": "bottom_left", "step": self.text_input.get(0.1, "end-1c"),"speed":self.speed_manual.get(), "speed_y": int(self.speed_manual.get())}       
                elif event.widget['text'] == "stop":
                    payload = {"topic": "stop"}
                elif event.widget['text'] == "Origin X":
                    payload = {"topic": "origin", "axis": "x", "speed":self.speed_manual.get()}                
                elif event.widget['text'] == "Origin Y":
                    payload = {"topic": "origin", "axis": "y", "speed":self.speed_manual.get()}            
                try:
                    result = requests.post(self.url_request_update[index], json=payload, timeout=1)
                    print(result.status_code)
                except requests.exceptions.ReadTimeout as ee:
                    pass
                except requests.exceptions.ConnectionError as ee:
                    print("Connection Error")
        except ValueError:
            messagebox.showerror("Error", "Select Client")

if __name__ == "__main__":
    app = App()