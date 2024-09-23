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
        self.update_vid_status = True # 
        self.open_vid = False
        self.change_target = True
        self.state = True
        self.status = 1
        self.start_time = 0
        self.stop_time = 0
        self.comp = True
        self.time_working = 0
        self.status_run = 0
        self.run_time = 0
        self.prev_time = 0
        self.trackbar_length = 350
        self.client_data = {}
        self.currrent_step_yaxis = 0.0
        self.previous_step_yaxis = 0.0

        self.data = {}
        self.position_x = 0
        self.position_y = 0
        self.color = (255, 0, 0)



        #---------------------------------------  variable   -----------------------------------#
        self.current_value = tk.IntVar()
        self.h_lower = tk.IntVar()
        self.s_lower = tk.IntVar()
        self.v_lower = tk.IntVar()
        self.h_upper = tk.IntVar()
        self.s_upper = tk.IntVar()
        self.v_upper = tk.IntVar()

        self.hue_lower_val = tk.IntVar()
        self.sat_low_val = tk.IntVar()
        self.val_low_val = tk.IntVar()
        self.hue_upper_val = tk.IntVar()
        self.sat_upper_val = tk.IntVar()
        self.val_upper_val = tk.IntVar()
        
        self.speed_manual = tk.IntVar(value=600)
        self.step = tk.DoubleVar()
        self.kp = tk.DoubleVar()
        self.ki = tk.DoubleVar()
        self.kd = tk.DoubleVar()
        self.pos_x = tk.IntVar()
        self.pos_y = tk.IntVar()
        self.max_speed = tk.IntVar()
        self.st_r = tk.IntVar()
        self.end_r = tk.IntVar()
        self.st_cl = tk.IntVar()
        self.end_cl =tk.IntVar()
        self.clicked = tk.StringVar()
        self.target_tracking = tk.StringVar()

        #IP Camera
        self.url_camera1 = "rtsp://admin:Nu12131213@192.168.1.170:554/Streaming/Channels/101/"
        # self.url_camera2 = 'http://192.168.1.181:81/videostream.cgi?user=admin&pwd=Nu12131213'
        # self.cap1 = cv2.VideoCapture(0)
        # self.cap2 = cv2.VideoCapture(self.url_camera2)
        # self.url_request = "http://192.168.0.105/"

        self.client_list = ("select 0", "select 1", "select 2")
        
        self.url_list = ["http://192.168.0.106/", 
                         "http://192.168.0.107/"]
                        #  "http://192.168.0.108/",]

        self.url_request_update = ["http://192.168.0.106/update-data",
                                   "http://192.168.0.107/update-data"]
                                #    "http://192.168.0.108/update-data",]

        self.url_request_auto = ["http://192.168.0.106/auto-data",
                                 "http://192.168.0.107/auto-data" ]
                                #  "http://192.168.0.108/auto-data",]
        
        self.url_update_path = ["http://192.168.0.106/update-path",
                                "http://192.168.0.107/update-path"]
                                # "http://192.168.0.108/update-path",]
        
        self.url_update_rtc = ["http://192.168.0.106/update-rtc",
                               "http://192.168.0.107/update-rtc"]
                            #    "http://192.168.0.108/update-rtc",]

        self.motor_x1 = {"axis":"x", "dir": 1, "pwm": 0.003125, "speed":50}
        self.motor_y1 = {"axis":"y", "dir": 1, "pwm": 0.003125, "speed":50}

        self.path_data_log = 'F:\\Solar thermal Project\\data_log\\'+f'calibrate_position_id_0_{datetime.now().strftime("%d_%m_%Y")}'+'.csv'
        self.path_recv_log = 'F:\\Solar thermal Project\\data_log\\'+f'recv_position_id_0_{datetime.now().strftime("%d_%m_%Y")}.csv'
        self.path_data_log1 = 'F:\\Solar thermal Project\\data_log\\'+f'calibrate_position_id_1_{datetime.now().strftime("%d_%m_%Y")}'+'.csv'
        self.path_recv_log1 = 'F:\\Solar thermal Project\\data_log\\'+f'recv_position_id_1_{datetime.now().strftime("%d_%m_%Y")}.csv'

        self.last_time_update = 0
        self.state_change = True
        self.last_time_tracking = 0
        self.time_delay_tracking = 0
        self.msg_file_path = ''
        
        self.ADDR = ("192.168.1.2", 8080)
        self.list_ip_clients = {'0': '192.168.1.110',
                                '1': '192.168.1.111'}
        
        self.all_connections = []
        self.all_address = []
        self.data_list = []
        
        self.title("Solar Thermar Project")
        self.geometry('+0+0')
        self.tabControl = ttk.Notebook(self)
        
        #create tab
        self.calibrate_tab = ttk.Frame(self.tabControl)
        self.monitor_tab = ttk.Frame(self.tabControl)
        
        #add tab
        self.tabControl.add(self.calibrate_tab, text ='Calibrate')
        self.tabControl.add(self.monitor_tab, text ='Monitor')
        self.tabControl.pack(expand = 1, fill ="both")
        
        #Calibrate tab
        self.top_frame = tk.LabelFrame(self.calibrate_tab, font=('Arial', 18), bg='gray' )
        self.top_frame.pack(side="top", fill="both", expand=True)
        
        self.bottom_frame = tk.LabelFrame(self.calibrate_tab, font=('Arial', 18), bg='gray' )
        self.bottom_frame.pack(side="top", fill="both", expand=False)
        
        #Monitor tab
        self.top_frame_in_monitor = tk.LabelFrame(self.monitor_tab, font=('Arial', 18), bg='gray' )
        self.top_frame_in_monitor.pack(side="top", fill="both", expand=True)
        
        self.bottom_frame_in_monitor = tk.LabelFrame(self.monitor_tab, font=('Arial', 18), bg='gray' )
        self.bottom_frame_in_monitor.pack(side="top", fill="both", expand=False)
        
        self.tool_bar_in_monitor = tk.LabelFrame(self.bottom_frame_in_monitor, text="Threshold", font=('Arial', 16),  bg='gray')
        self.tool_bar_in_monitor.pack(side=tk.LEFT, fill='both', expand=True)

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
        # self.ip_cam_tap.add(self.camera_tap2, text ='Camera2')
        self.ip_cam_tap.pack(expand = 1, fill ="both")
        
        #----------------------------------------  Video Frame  ----------------------------------------#
        self.start_camera = tk.Button(self.camera_tap1, text="Start Camera", command=self.update_vid)
        self.start_camera.pack()
        
        #----------------------------------- Create canvas for image -----------------------------------#
        self.calibrate_frame = tk.Canvas(self.camera_tap1, width=640, height=480)
        self.calibrate_frame.pack()
        
        self.table_frame = tk.LabelFrame(self.top_frame, font=('Arial', 14), bg='gray')
        self.table_frame.pack(side='left', fill='both', expand=True)
        
        #----------------------------------- Create canvas for image -----------------------------------#
        self.receiver_frame = tk.Canvas(self.table_frame, width=320, height=320)
        self.receiver_frame.pack()
        
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
        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 8))
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

        #self.tabview.grid(row=1, column=0,)
        self.tabview.pack(fill='both', expand=True, padx=5, pady=5)
        self.tabview.bind('<Button-1>', self.select_item)
        
        #----------------------------------- Setting Connection ----------------------------------------#
        self.connect_frame = tk.Frame(self.top_frame_in_cnt, bg='blue')
        self.connect_frame.pack(side='left', fill='both',expand=True)
        
        self.btn_open = tk.Button(self.connect_frame, text="Start Server", font=('Arial', 12), width=16, command=self.start_server_thread)
        self.btn_open.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        #-------------------------------------- Create Dropdown menu -----------------------------------#
        self.drop = ttk.Combobox(self.connect_frame, textvariable=self.clicked, font=(None, 14), width=12)
        self.drop.set('Select Client')
        self.drop['values'] = self.client_list
        self.drop.grid(row=1, column=0, columnspan=2)
        
        self.btn_conn = tk.Button(self.connect_frame, text='Set Time',  font=('Arial', 12), bg='gray', command=self.on_connect)
        self.btn_conn.grid(row=3, column=0, pady=5)
        self.btn_close = tk.Button(self.connect_frame, text='Check ID',   width=7 ,font=('Arial', 12), bg='gray', command=self.on_close)
        self.btn_close.grid(row=3, column=1, pady=5)
        
        #------------------------------------------ open file button -----------------------------------#
        self.msg_recv = tk.Label(self.connect_frame, text='File: 0 bytes', font=('Arial', 12), bg='blue', fg='WHITE')
        self.msg_recv.grid(column=0, row=2, columnspan=2)
        self.open_button = tk.Button(self.connect_frame, text='Open File', width=16, font=('Arial', 12), bg='gray', command=self.open_text_file )
        self.open_button.grid(column=0, row=4, pady=5, columnspan=2)
        self.sent_button = tk.Button(self.connect_frame, text='Send File', width=16, font=('Arial', 12), bg='gray', command=self.send_text_file )
        self.sent_button.grid(column=0, row=5, pady=5, columnspan=2)
        
        self.cnt_frame2 = tk.Frame(self.top_frame_in_cnt, bg='blue')
        self.cnt_frame2.pack(side='left', fill='both', expand=True)
        
        cnt_frame1 = tk.Frame(self.bottom_frame_in_cnt, bg='#1EA1FF')
        cnt_frame1.pack(side='left', fill='both', expand=True)
        
        #----------------------------------- load image -----------------------------------#
        self.stop_img = tk.PhotoImage(file = "F:\\Solar thermal Project\\Control\\Photo\\stop.png")
        self.up_img = tk.PhotoImage(file = "F:\\Solar thermal Project\\Control\\Photo\\up-arrow.png")
        self.down_img = tk.PhotoImage(file = "F:\\Solar thermal Project\\Control\\Photo\\download.png")
        self.forward_img = tk.PhotoImage(file = "F:\\Solar thermal Project\\Control\\Photo\\forward.png")
        self.reverse_img = tk.PhotoImage(file = "F:\\Solar thermal Project\\Control\\Photo\\reverse.png")
        self.top_left_img = tk.PhotoImage(file = "F:\\Solar thermal Project\\Control\\Photo\\top_left.png")
        self.top_right_img = tk.PhotoImage(file = "F:\\Solar thermal Project\\Control\\Photo\\top_right.png")
        self.bottom_left_img = tk.PhotoImage(file = "F:\\Solar thermal Project\\Control\\Photo\\bottom_left.png")
        self.bottom_right_img = tk.PhotoImage(file = "F:\\Solar thermal Project\\Control\\Photo\\bottom_right.png")
        
        #------------------------------ trackbar_in_monitor_tab  ---------------------------#
        self.hue_lable = tk.Label(self.tool_bar_in_monitor, text="H_L", font=('Arial', 10), bg='gray')
        self.hue_lable.grid(row=0, column=0)
        self.hue_lower = tk.Scale(self.tool_bar_in_monitor, from_=0, to=179, length=350,  orient=tk.HORIZONTAL, variable=self.hue_lower_val)
        self.hue_lower.grid(row=0, column=1, padx=0, pady=0)
        self.hue_lower.set(0)
        
        self.sat_lable = tk.Label(self.tool_bar_in_monitor, text="S_L", font=('Arial', 10), bg='gray')
        self.sat_lable.grid(row=1, column=0)
        self.sat_lower = tk.Scale(self.tool_bar_in_monitor, from_=0, to=255, length=350, orient=tk.HORIZONTAL, variable=self.sat_low_val)
        self.sat_lower.grid(row=1, column=1,  padx=0, pady=0)
        self.sat_lower.set(0)
        
        self.val_lable = tk.Label(self.tool_bar_in_monitor, text="V_L", font=('Arial', 10), bg='gray')
        self.val_lable.grid(row=2, column=0)
        self.val_lower = tk.Scale(self.tool_bar_in_monitor, from_=0, to=255, length=350, orient=tk.HORIZONTAL, variable=self.val_low_val)
        self.val_lower.grid(row=2, column=1,  padx=0, pady=0)
        self.val_lower.set(175)
        
        self.hue_lable = tk.Label(self.tool_bar_in_monitor, text="H_U", font=('Arial', 10), bg='gray')
        self.hue_lable.grid(row=0, column=2)
        self.hue_upper = tk.Scale(self.tool_bar_in_monitor, from_=0, to=179, length=350, orient=tk.HORIZONTAL, variable=self.hue_upper_val)
        self.hue_upper.grid(row=0, column=3, padx=0, pady=0)
        self.hue_upper.set(175)

        self.sat_lable = tk.Label(self.tool_bar_in_monitor, text="S_U", font=('Arial', 10), bg='gray')
        self.sat_lable.grid(row=1, column=2)
        self.sat_upper = tk.Scale(self.tool_bar_in_monitor, from_=0, to=255, length=350, orient=tk.HORIZONTAL, variable=self.sat_upper_val)
        self.sat_upper.grid(row=1, column=3, padx=0, pady=0)
        self.sat_upper.set(255)

        self.val_lable = tk.Label(self.tool_bar_in_monitor, text="V_U", font=('Arial', 10), bg='gray')
        self.val_lable.grid(row=2, column=2)
        self.val_upper = tk.Scale(self.tool_bar_in_monitor, from_=0, to=255, length=350, orient=tk.HORIZONTAL, variable=self.val_upper_val)
        self.val_upper.grid(row=2, column=3, padx=0, pady=0)
        self.val_upper.set(255)

        style = ttk.Style()
        style.configure("TScale", background="gray")

        #----------------------------------- trackbar -----------------------------------#
        self.h_lower_label = tk.Label(self.tool_bar, text="H_L", font=('Arial', 10), bg='gray')
        self.h_lower_label.grid(row=0, column=0)
        self.h_l = ttk.Scale(self.tool_bar, style="TScale", from_=0, to=179, length=self.trackbar_length,  orient=tk.HORIZONTAL, variable=self.h_lower, command=self.slider_changed)
        self.h_l.grid(row=0, column=1, padx=0, pady=0)
        self.h_l.set(0)

        self.s_lower_label = tk.Label(self.tool_bar, text="H_L", font=('Arial', 10), bg='gray')
        self.s_lower_label.grid(row=1, column=0)
        self.s_l = ttk.Scale(self.tool_bar, from_=0, to=255, length=self.trackbar_length, orient=tk.HORIZONTAL, variable=self.s_lower, command=self.slider_changed)
        self.s_l.grid(row=1, column=1,  padx=0, pady=0)
        self.s_l.set(0)

        self.v_lower_label = tk.Label(self.tool_bar, text="V_L", font=('Arial', 10), bg='gray')
        self.v_lower_label.grid(row=2, column=0)
        self.v_l = ttk.Scale(self.tool_bar, from_=0, to=255, length=self.trackbar_length, orient=tk.HORIZONTAL, variable=self.v_lower, command=self.slider_changed)
        self.v_l.grid(row=2, column=1,  padx=0, pady=0)
        self.v_l.set(230)

        self.h_upper_label = tk.Label(self.tool_bar, text="H_U", font=('Arial', 10), bg='gray')
        self.h_upper_label.grid(row=0, column=2)
        self.h_u = ttk.Scale(self.tool_bar, from_=0, to=179, length=self.trackbar_length, orient=tk.HORIZONTAL, variable=self.h_upper, command=self.slider_changed)
        self.h_u.grid(row=0, column=3, padx=0, pady=0)
        self.h_u.set(179)

        self.s_upper_label = tk.Label(self.tool_bar, text="S_U", font=('Arial', 10), bg='gray')
        self.s_upper_label.grid(row=1, column=2)
        self.s_u = ttk.Scale(self.tool_bar, from_=0, to=255, length=self.trackbar_length, orient=tk.HORIZONTAL, variable=self.s_upper, command=self.slider_changed)
        self.s_u.grid(row=1, column=3, padx=0, pady=0)
        self.s_u.set(255)

        self.v_upper_label = tk.Label(self.tool_bar, text="V_U", font=('Arial', 10), bg='gray')
        self.v_upper_label.grid(row=2, column=2)
        self.v_u = ttk.Scale(self.tool_bar, from_=0, to=255, length=self.trackbar_length, orient=tk.HORIZONTAL, variable=self.v_upper, command=self.slider_changed)
        self.v_u.grid(row=2, column=3, padx=0, pady=0)
        self.v_u.set(255)

        self.filter_label = tk.Label(self.tool_bar, text="Fillter", font=('Arial', 10), bg='gray')
        self.filter_label.grid(row=6, column=0)

        self.area = ttk.Scale(self.tool_bar, from_=0, to=80000, length=self.trackbar_length, orient=tk.HORIZONTAL, command=self.slider_changed)
        self.area.grid(row=6, column=1, padx=0, pady=0)
        self.area.set(15000)

        self.off_set_label = tk.Label(self.tool_bar, text="Offset", font=('Arial', 10), bg='gray')
        self.off_set_label.grid(row=6, column=2)
        self.off_set = ttk.Scale(self.tool_bar, from_=0, to=100, length=self.trackbar_length, orient=tk.HORIZONTAL, command=self.slider_changed)
        self.off_set.grid(row=6, column=3, padx=0, pady=0)
        self.off_set.set(4)

        #-----------------------------------  Crop_Image  -----------------------------------#
        self.crop_frame = tk.LabelFrame(self.bottom_frame, text="Crop Image", font=('Arial', 14),  bg='gray')
        self.crop_frame.pack(side=tk.LEFT)
        self.start_row_label = tk.Label(self.crop_frame, text="Start row", font=('Arial', 10), bg='gray')
        self.start_row_label.grid(row=0, column=0)
        self.start_row = ttk.Scale(self.crop_frame, orient=tk.HORIZONTAL, from_=0, to=480, length=self.trackbar_length, variable=self.st_r, command=self.slider_changed)
        self.start_row.grid(row=0, column=1)
        #self.start_row.set(156)
        self.start_row.set(47)
        self.end_row_label = tk.Label(self.crop_frame, text="End row", font=('Arial', 10), bg='gray')
        self.end_row_label.grid(row=1, column=0)
        self.end_row = ttk.Scale(self.crop_frame, orient=tk.HORIZONTAL, from_=0, to=480, length=self.trackbar_length, variable=self.end_r, command=self.slider_changed)
        self.end_row.grid(row=1, column=1)
        #self.end_row.set(370)
        self.end_row.set(200)

        self.start_col_label = tk.Label(self.crop_frame, text="Start col", font=('Arial', 10), bg='gray')
        self.start_col_label.grid(row=2, column=0)
        self.start_col = ttk.Scale(self.crop_frame, orient=tk.HORIZONTAL, from_=0, to=640, length=self.trackbar_length, variable=self.st_cl, command=self.slider_changed)
        self.start_col.grid(row=2, column=1)
        #self.start_col.set(249)
        self.start_col.set(207)
        self.end_col_label = tk.Label(self.crop_frame, text="End col", font=('Arial', 10), bg='gray')
        self.end_col_label.grid(row=3, column=0)
        self.end_col = ttk.Scale(self.crop_frame, orient=tk.HORIZONTAL, from_=0, to=640, length=self.trackbar_length, variable=self.end_cl, command=self.slider_changed)
        self.end_col.grid(row=3, column=1)
        #self.end_col.set(472)
        self.end_col.set(407)

        #--------------------------------- Button_Widget -------------------------------------#
        btn_frame = tk.LabelFrame(cnt_frame1,  bg='#1EA1FF', borderwidth=0)
        btn_frame.pack(side=tk.LEFT, fill='y', expand=True, pady=25)
        manual_frame = tk.LabelFrame(cnt_frame1,  bg='#1EA1FF', borderwidth=0)
        manual_frame.pack(side=tk.LEFT, fill='x', expand=True)

        #--------------------------------- Button_Box -----------------------------------------#
        self.box_input = tk.LabelFrame(manual_frame, bg='#1EA1FF', borderwidth=0)
        self.box_input.grid(row=0, column=1, )

        self.button_box = tk.LabelFrame(manual_frame, bg='#1EA1FF', borderwidth=0)
        self.button_box.grid(row=2, column=1, )

        self.select_client = ttk.Combobox(btn_frame, textvariable=self.target_tracking, font=(None, 14), width=14)
        self.select_client.set('Select target')
        self.select_client['values'] = ("Calibrate", "Receiver")
        self.select_client.grid(row=0, column=0, columnspan=2, pady=5)
        self.select_client.bind('<<ComboboxSelected>>', self.combobox_callback)

        self.mode_btn = tk.Button(btn_frame, text="Manual", font=('Arial', 12, ), height=2, width=18, command=self.mode_call_back, bg='gray')
        self.mode_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.path_btn = tk.Button(btn_frame, text="Run path", font=('Arial', 12, ), height=2, width=18, command=self.path_call_back, bg='gray')
        self.path_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5)



        label_text = tk.Label(self.box_input, text="Step", font=('Arial', 12), bg='#1EA1FF',fg='black')
        label_text.grid(row=0, column=0, padx=2.5, pady=2.5)
    
        self.text_input = tk.Text(self.box_input, height=1, width=7, font=('Arial', 14), )
        self.text_input.grid(row=0, column=1, padx=2.5, pady=2.5)

        label_speed = tk.Label(self.box_input, text="Speed", font=('Arial', 12), bg='#1EA1FF', fg='black',)
        label_speed.grid(row=1, column=0, padx=2.5, pady=2.5)
        self.speed_input = tk.Entry(self.box_input,  width=7, font=('Arial', 14), textvariable=self.speed_manual,)
        self.speed_input.grid(row=1, column=1, padx=2.5, pady=2.5)

        self.label_led_x = tk.Label(self.box_input, text="Origin X", bg='#1EA1FF', font=('Arial', 12), fg='black')
        self.label_led_x.grid(row=0, column=2, padx=2.5, pady=2.5)
        self.led_origin_x = tk_tools.Led(self.box_input, size=22, bg='#1EA1FF')
        self.led_origin_x.grid(row=0, column=3, padx=2.5, pady=2.5)
        self.label_pos_x = tk.Label(self.box_input, text="Safety X+", bg='#1EA1FF', font=('Arial', 12), fg='black')
        self.label_pos_x.grid(row=0, column=6, padx=2.5, pady=2.5)
        self.led_pos_x = tk_tools.Led(self.box_input, size=22, bg='#1EA1FF')
        self.led_pos_x.grid(row=0, column=5, padx=2.5, pady=2.5)


        self.label_led_x = tk.Label(self.box_input, text="Origin Y", bg='#1EA1FF', font=('Arial', 12), fg='black')
        self.label_led_x.grid(row=1, column=2, padx=2.5, pady=2.5)
        self.led_origin_y = tk_tools.Led(self.box_input, size=22, bg='#1EA1FF')
        self.led_origin_y.grid(row=1, column=3, padx=2.5, pady=2.5)
        self.label_pos_y = tk.Label(self.box_input, text="Safety Y+", bg='#1EA1FF', font=('Arial', 12), fg='black')
        self.label_pos_y.grid(row=1, column=6, padx=2.5, pady=2.5)
        self.led_pos_y = tk_tools.Led(self.box_input, size=22, bg='#1EA1FF')
        self.led_pos_y.grid(row=1, column=5, padx=2.5, pady=2.5)

        self.label_limit_safety = tk.Label(self.box_input, text="Limit Safety", bg='#1EA1FF', font=('Arial', 12), fg='black')
        self.label_limit_safety.grid(row=2, column=6, padx=2.5, pady=2.5)
        self.led_limit_safety = tk_tools.Led(self.box_input, size=22, bg='#1EA1FF')
        self.led_limit_safety.grid(row=2, column=5, padx=2.5, pady=2.5)

        self.label_status_path = tk.Label(self.box_input, text="Path working", bg='#1EA1FF', font=('Arial', 12), fg='black')
        self.label_status_path.grid(row=2, column=2, padx=2.5, pady=2.5)
        self.led_status_path = tk_tools.Led(self.box_input, size=22, bg='#1EA1FF')
        self.led_status_path.grid(row=2, column=3, padx=2.5, pady=2.5)

  #---------------------------------------------- Test in tab monitor----------------------------------------------------------------# 
        
        self.label_id_monitor_tab = tk.Label(self.monitor_heliostat, text="ID", bg='gray', font=('Arial', 12), fg='black')
        self.label_id_monitor_tab.grid(row=1, column=1, padx=2.5, pady=2.5)
        self.label_OriginX_monitor_tab = tk.Label(self.monitor_heliostat, text="Safety NegX", bg='gray', font=('Arial', 12), fg='black')
        self.label_OriginX_monitor_tab.grid(row=1, column=2, padx=2.5, pady=2.5)
        self.label_OriginY_monitor_tab = tk.Label(self.monitor_heliostat, text="Safety NegY", bg='gray', font=('Arial', 12), fg='black')
        self.label_OriginY_monitor_tab.grid(row=1, column=3, padx=2.5, pady=2.5)
        self.label_safety_posX_monitor_tab = tk.Label(self.monitor_heliostat, text="Safety PosX", bg='gray', font=('Arial', 12), fg='black')
        self.label_safety_posX_monitor_tab.grid(row=1, column=4, padx=2.5, pady=2.5)
        self.label_safety_posY_monitor_tab = tk.Label(self.monitor_heliostat, text="Safety PosY", bg='gray', font=('Arial', 12), fg='black')
        self.label_safety_posY_monitor_tab.grid(row=1, column=5, padx=2.5, pady=2.5)
        self.label_limit_safety_monitor_tab = tk.Label(self.monitor_heliostat, text="Limit safety", bg='gray', font=('Arial', 12), fg='black')
        self.label_limit_safety_monitor_tab.grid(row=1, column=6, padx=2.5, pady=2.5) 
        self.label_path_status_monitor_tab = tk.Label(self.monitor_heliostat, text="Path status", bg='gray', font=('Arial', 12), fg='black')
        self.label_path_status_monitor_tab.grid(row=1, column=7, padx=2.5, pady=2.5)        

        
        self.label_id0_monitor_tab = tk.Label(self.monitor_heliostat, text="0", bg='gray', font=('Arial', 12), fg='black')
        self.label_id0_monitor_tab.grid(row=2, column=1, padx=2.5, pady=2.5)
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


        self.label_id1_monitor_tab = tk.Label(self.monitor_heliostat, text="1", bg='gray', font=('Arial', 12), fg='black')
        self.label_id1_monitor_tab.grid(row=3, column=1, padx=2.5, pady=2.5)
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
        self.top_left_btn = ttk.Button(self.button_box, text="top_left", image=self.top_left_img)
        self.top_left_btn.grid(row=0, column=0, padx=2.5, pady=2.5)
        self.top_left_btn.bind('<Button-1>', self.check_button)

        self.up_btn = ttk.Button(self.button_box, text="up",  image=self.up_img )
        self.up_btn.grid(row=0, column=1, padx=2.5, pady=2.5)
        self.up_btn.bind('<Button-1>', self.check_button)

        self.top_right_btn = ttk.Button(self.button_box, text="top_right",image=self.top_right_img )
        self.top_right_btn.grid(row=0, column=2, padx=2.5, pady=2.5)
        self.top_right_btn.bind('<Button-1>', self.check_button)

        self.forward_btn = ttk.Button(self.button_box, text="forward",  image=self.forward_img, )
        self.forward_btn.grid(row=1, column=0, padx=2.5, pady=2.5)
        self.forward_btn.bind('<Button-1>', self.check_button)
        
        self.stop_btn = ttk.Button(self.button_box, text="stop", image=self.stop_img )
        self.stop_btn.grid(row=1, column=1, padx=2.5, pady=2.5)
        self.stop_btn.bind('<Button-1>', self.check_button)

        self.reverse_btn = ttk.Button(self.button_box, text="reverse",  image=self.reverse_img, )
        self.reverse_btn.grid(row=1, column=2, padx=2.5, pady=2.5)
        self.reverse_btn.bind('<Button-1>', self.check_button)

        self.bottom_left_btn = ttk.Button(self.button_box, text="bottom_left", image=self.bottom_left_img )
        self.bottom_left_btn.grid(row=2, column=0, padx=2.5, pady=2.5)
        self.bottom_left_btn.bind('<Button-1>', self.check_button)

        self.down_btn = ttk.Button(self.button_box, text="down",  image=self.down_img, )
        self.down_btn.grid(row=2, column=1, padx=2.5, pady=2.5)
        self.down_btn.bind('<Button-1>', self.check_button)

        self.bottom_right_btn = ttk.Button(self.button_box, text="bottom_right", image=self.bottom_right_img )
        self.bottom_right_btn.grid(row=2, column=2, padx=2.5, pady=2.5)
        self.bottom_right_btn.bind('<Button-1>', self.check_button)

        self.origin_x = tk.Button(btn_frame, text='Origin X', bg='yellow', font=('Arial', 12), width=8 )
        self.origin_x.grid(row=3, column=0, pady=5)
        self.origin_x.bind('<Button-1>', self.check_button)

        self.origin_y = tk.Button(btn_frame, text='Origin Y', bg='yellow', font=('Arial', 12), width=8 )
        self.origin_y.grid(row=3, column=1, pady=5)
        self.origin_y.bind('<Button-1>', self.check_button)

        self.stop = tk.Button(btn_frame, text='stop', bg='red', font=('Arial', 12), width=18, height=2 )
        self.stop.grid(row=4, column=0, columnspan=2, padx=5, pady=5 )
        self.stop.bind('<Button-1>', self.check_button )

        self.send_point = tk.Button(btn_frame, text='send point', bg='green', font=('Arial', 12), width=18, height=2 ,command=self.path_call_back)
        self.send_point.grid(row=5, column=0,columnspan=2, padx=5, pady=5 )

        self.led_move_complete = tk_tools.Led(btn_frame, size=22, bg='gray')
        self.led_move_complete.grid(row=6, column=0, padx=2.5, pady=2.5)



        #--------------------------------- current_position_label -----------------------------------------#
        self.label_status = tk.Label(self.cnt_frame2, text="Status", font=('DS-DIGITAL', 20), bg='blue')
        self.label_status.grid(row=0, column=1)
        
        self.led = tk_tools.Led(self.cnt_frame2, size=50, bg='blue')
        self.led.grid(row=0, column=2, columnspan=2)
        self.led.to_grey(on=True)
       
        #--------------------------------- PID_Parameter -----------------------------------------#
        label_kp = tk.Label(self.cnt_frame2, text='Kp', font=('Arial', 12), bg='blue', fg='WHITE' )
        label_kp.grid(row=2, column=0 )
        self.Kp  = tk.Entry(self.cnt_frame2, width=10, font=('Arial', 12), textvariable=self.kp, justify='center')
        self.Kp.grid(row=2, column=1, padx=5, pady=2.5 )
        self.kp.set(10)

        label_ki = tk.Label(self.cnt_frame2, text='Ki', font=('Arial', 12), fg='WHITE', bg='blue' )
        label_ki.grid(row=3, column=0 )
        self.Ki  = tk.Entry(self.cnt_frame2, width=10, font=('Arial', 12),  textvariable=self.ki, justify='center' )
        self.Ki.grid(row=3, column=1, padx=5, pady=2.5 )
        self.ki.set(1)

        label_kd = tk.Label(self.cnt_frame2, text='Kd', font=('Arial', 12), bg='blue', fg='WHITE' )
        label_kd.grid(row=4, column=0 )
        self.Kd  = tk.Entry(self.cnt_frame2, width=10, font=('Arial', 12),  textvariable=self.kd, justify='center' )
        self.Kd.grid(row=4, column=1, padx=5, pady=2.5 )

        #---------------------------------------- Set_points_X_Y_speed  -----------------------------------------#
        tk.Label(self.cnt_frame2, text='Set Point X', bg='blue', font=('Arial', 12),fg='WHITE').grid(row=2, column=2)
        self.setpoint_x  = tk.Entry(self.cnt_frame2, width=10, font=('Arial', 12), textvariable=self.pos_x, justify='center')
        self.setpoint_x.grid(row=2, column=3, padx=0, pady=2.5)
        self.pos_x.set(320)

        tk.Label(self.cnt_frame2, text='Set Point Y', bg='blue', font=('Arial', 12),fg='WHITE').grid(row=3, column=2)
        self.setpoint_y  = tk.Entry(self.cnt_frame2, width=10, font=('Arial', 12), textvariable=self.pos_y, justify='center')
        self.setpoint_y.grid(row=3, column=3, padx=0, pady=2.5)
        self.pos_y.set(240)

        tk.Label(self.cnt_frame2, text='Max Speed', bg='blue', font=('Arial', 12),fg='WHITE').grid(row=4, column=2)
        self.speed_m  = tk.Entry(self.cnt_frame2, width=10, font=('Arial', 12), textvariable=self.max_speed, justify='center')
        self.speed_m.grid(row=4, column=3, padx=0, pady=2.5)
        self.max_speed.set(600)

        #----------------------------------------- off_set_x_y_calibarte -----------------------------------------#
        self.label_text = tk.Label(self.cnt_frame2, text="Offset X", font=('Arial', 12), bg='blue', fg='WHITE')
        self.label_text.grid(row=5, column=0, pady=2.5)
        self.off_set_x = tk.Text(self.cnt_frame2, height=1, width=10, font=('Arial', 12), )
        self.off_set_x.grid(row=5, column=1, pady=2.5)

        self.label_speed = tk.Label(self.cnt_frame2, text="Offset Y", font=('Arial', 12), bg='blue', fg='WHITE')
        self.label_speed.grid(row=6, column=0)
        self.off_set_y = tk.Text(self.cnt_frame2, height=1, width=10, font=('Arial', 12), )
        self.off_set_y.grid(row=6, column=1, padx=5, pady=2.5)

        self.button_set_offset = tk.Button(self.cnt_frame2, text="Off Set Recv", font=('Arial', 10), bg='green',width=10, command=self.set_off_set_recv)
        self.button_set_offset.grid(row=7, column=1, pady=2.5)

        #----------------------------------------- off_set_x_y_receiver -----------------------------------------#
        self.label_text = tk.Label(self.cnt_frame2, text="Offset X", font=('Arial', 12), bg='blue', fg='WHITE')
        self.label_text.grid(row=5, column=2, pady=2.5)
        self.off_set_x_recv = tk.Text(self.cnt_frame2, height=1, width=10, font=('Arial', 12), )
        self.off_set_x_recv.grid(row=5, column=3, pady=2.5)

        self.label_speed = tk.Label(self.cnt_frame2, text="Offset Y", font=('Arial', 12), bg='blue', fg='WHITE')
        self.label_speed.grid(row=6, column=2, pady=2.5)
        self.off_set_y_recv = tk.Text(self.cnt_frame2, height=1, width=10, font=('Arial', 12), )
        self.off_set_y_recv.grid(row=6, column=3, padx=5, pady=2.5)

        self.button_set_offset_recv = tk.Button(self.cnt_frame2, text="Set Scale", font=('Arial', 10), bg='green',width=10, command=self.set_off_set)
        self.button_set_offset_recv.grid(row=7, column=3, pady=2.5)
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

        #self.save_btn = tk.Button(self.table_frame, text='Save', font=('Arial', 12), bg='green', command=self.save_position, width=10)
        #self.save_btn.grid(row=1, column=0, pady=5)
        #self.show_frame()  #Display 

         

        self.mainloop()  #Starts GUI

    ### --- Earth_comment camera start --- ###
    def update_vid(self):
        if self.update_vid_status:  ## ---> Earth_comment if update_vid_status is true start cap camera frame 
            self.open_vid = True
            self.cap1 = cv2.VideoCapture(self.url_camera1)
            self.show_frame()  ##Display  ---> Earth_comment start cap camera frame and send to operate auto mode 
            self.update_vid_status = False
            print("Start Video")
        else:
            self.open_vid = False
            self.calibrate_frame.after_cancel(self.show_frame)
            self.cap1.release()

            blank_img_cal = np.zeros((480,640,3), np.uint8)
            blank_img_recv = np.zeros((320,320,3), np.uint8)

            self.calibrate = Image.fromarray(blank_img_cal)
            self.calibrate = ImageTk.PhotoImage(image=self.calibrate)
            self.calibrate_frame.create_image(0, 0,  anchor=tk.NW, image=self.calibrate)

            recv = Image.fromarray(blank_img_recv)
            self.receiver_vid = ImageTk.PhotoImage(recv)
            self.receiver_frame.create_image(0,0,anchor=tk.NW, image=self.receiver_vid)

            self.update_vid_status = True
            print("Stop Video")

    def combobox_callback(self, event):
        print(self.target_tracking.get(),  end=" ")
        if(self.target_tracking.get() == "Calibrate"): self.state_change = True
        elif(self.target_tracking.get() == "Receiver"): self.state_change = False
        else: print("selet target ?")

    def select_item(self, event):
        cur_item = self.tabview.focus()
        print(self.tabview.item(cur_item))

    def bind_server(self):
        for url in self.url_list: 
            try:
                result = requests.get(url , timeout=1) ### --- Eath_comment get data from url http://192.168.0.106 ###
                if result.status_code == 200:  self.led.to_green(on=True)
            
                payload = result.json() ### --- Earth_comment convert data to json format 
                self.data_list.append(payload) ### --- Earth_comment append data in empty list 

                #remove duplicate value
                new_list = list({dictionary['id'] : dictionary for dictionary in self.data_list }.values())
                new_list = sorted(new_list, key=lambda d: d['id']) #sorte by id
                # print(new_list)

                if not self.state:
                    index = int(self.clicked.get().replace("select ",''))                 
                    for i in new_list:
                        if self.is_true: #check position in target
                            if i['id'] == index :
                                path = self.path_data_log if self.state_change else self.path_recv_log
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

                            # if d['safety']['x'] : self.led_origin_x.to_green(on=True)
                            # else : self.led_origin_x.to_grey(on=True)
                            # if d['safety']['y'] : self.led_origin_y.to_green(on=True)
                            # else : self.led_origin_y.to_grey(on=True)
                            # if d['safety']['x1'] : self.led_pos_x.to_red(on=True)
                            # else : self.led_pos_x.to_grey(on=True)
                            # if d['safety']['y1'] : self.led_pos_y.to_red(on=True)
                            # else : self.led_pos_y.to_grey(on=True)
                            # if d['safety']['ls1'] : self.led_limit_safety.to_red(on=True)
                            # else : self.led_limit_safety.to_grey(on=True)
                            # if d['safety']['st_path'] : self.led_status_path.to_yellow(on=True)
                            # else : self.led_status_path.to_grey(on=True)

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
                            if d['safety']['move_comp'] :                                
                                self.led_move_complete.to_yellow(on=True)
                            else : 
                                self.led_move_complete.to_red(on=True)


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

        self.current_page()
        self.after(500, self.bind_server)

    def start_server_thread(self):
        self.bind_server()

        # threading._start_new_thread(on_server, ())
        # thread_server = threading.Thread(target=self.bind_server)
        # thread_server.start()


    #--------- set time ----------------------------------#
    def on_connect(self):  
        hour = datetime.now().strftime("%H")
        minute = datetime.now().strftime("%M")
        sec = datetime.now().strftime("%S")
        # print(hour,minute,sec)
        try:
            index = int(self.clicked.get().replace("select ",''))
            payload = {"topic": "rtc", 'hour': hour, 'minute': minute, 'sec':sec}
            result = requests.post(self.url_update_rtc[index], json=payload, timeout=1)
            if(result.status_code == 200):
                print(result.text)
                data = json.loads(result.text)
                messagebox.showinfo("Time", data['time'])
                # print(data['time'])

        except requests.exceptions.ReadTimeout as ee:
            print("Time Out")
        except requests.exceptions.ConnectionError as ee:
            print("Connection Error")
        except ValueError:
            messagebox.showerror("Error", "Select Client")
    

    def current_page(self):
        self.current_id = int(self.clicked.get().replace("select ",''))
        # print(self.current_id)
        if self.current_id == 0:
           if self.status_xneg_id0:self.led_origin_x.to_green(on=True)
           else : self.led_origin_x.to_grey(on=True)
           if self.status_yneg_id0:self.led_origin_y.to_green(on=True)
           else : self.led_origin_y.to_grey(on=True)  
           if self.status_xpos_id0 :self.led_pos_x.to_red(on=True)
           else : self.led_pos_x.to_grey(on=True) 
           if self.status_ypos_id0 :self.led_pos_y.to_red(on=True)
           else : self.led_pos_y.to_grey(on=True) 
           if self.status_limit_id0 :self.led_limit_safety.to_red(on=True)
           else : self.led_limit_safety.to_grey(on=True) 
           if self.status_path_id0 :
              self.led_status_path.to_yellow(on=True)
              self.path_btn.config(text = 'Path Working')  
              self.path_btn.config(bg = 'green')               
           else : 
              self.led_status_path.to_grey(on=True) 
              self.path_btn.config(text = 'Run Path') 
              self.path_btn.config(bg = 'gray')

        if self.current_id == 1:
           if self.status_xneg_id1:self.led_origin_x.to_green(on=True)
           else : self.led_origin_x.to_grey(on=True)
           if self.status_yneg_id1:self.led_origin_y.to_green(on=True)
           else : self.led_origin_y.to_grey(on=True)
           if self.status_xpos_id1 :self.led_pos_x.to_red(on=True)
           else : self.led_pos_x.to_grey(on=True) 
           if self.status_ypos_id1 :self.led_pos_y.to_red(on=True)
           else : self.led_pos_y.to_grey(on=True) 
           if self.status_limit_id1 :self.led_limit_safety.to_red(on=True)
           else : self.led_limit_safety.to_grey(on=True) 
           if self.status_path_id1 :
              self.led_status_path.to_yellow(on=True)
              self.path_btn.config(text = 'Path Working')  
              self.path_btn.config(bg = 'green') 
           else : 
              self.led_status_path.to_grey(on=True) 
              self.path_btn.config(text = 'Run Path') 
              self.path_btn.config(bg = 'gray')   


   
    #-------------------------log data csv------------------------#

    ### --- Earth_comment this save X-image positon and Y-image postion --- ### 
    def write_csv(self, path, curr_x, curr_y, err_x, err_y):
        with open(path, 'a') as f:
            writer = csv.writer(f, lineterminator='\n')
            date = datetime.now().strftime("%Y-%m-%d")
            time = datetime.now().strftime("%H:%M:%S")
            writer.writerow([date, time, curr_x, curr_y, err_x, err_y])

    def path_call_back(self):
        try:
            index = int(self.clicked.get().replace("select ",''))
            print(index)
            payload = {"topic": "mode", "status": self.status_run, "speed":self.speed_input.get()}
            result = requests.post(self.url_request_update[index], json=payload, timeout=1)
            print(result.status_code)
            if not self.status_run:
                self.status_run = 1
                # self.path_btn.config(text = 'Run Path') 
                # self.path_btn.config(bg = 'gray')
                print("Path State: ", self.status_run)
            else:
                self.status_run = 0
                # self.path_btn.config(text = 'Path Working')  
                # self.path_btn.config(bg = 'green')              
                print("Path State: ", self.status_run)

        except requests.exceptions.ReadTimeout as ee:
            print("Time Out")
        except requests.exceptions.ConnectionError as ee:
            print("Connection Error")
        except ValueError:
            messagebox.showerror("Error", " Please select client ")
            

    ### -- Earth_comment send auto mode to backend -- ###
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

    ### -- Earth_comment calculate find center auto mode -- ###
    def calculate_center(self, contours):
        m = cv2.moments(contours)
        if m['m00'] != 0:
            cx = int(m['m10']/m['m00'])
            cy = int(m['m01']/m['m00'])
        return (cx, cy)

    ### -- Earth_comment haddle calculate control helio stat auto mode -- ###
    def get_contours(self, contours, img, x_medium, y_medium, path, print_str=True, dir_motor=0):
        cv2.line(img, (x_medium, 0), (x_medium, img.shape[0]), (255,0,0), 1)
        cv2.line(img, (0, y_medium), (img.shape[1], y_medium), (255,0,0), 1)

        for cnt in contours:
            if cv2.contourArea(cnt) > self.area.get():
                self.area_px = cv2.contourArea(cnt)
                cx, cy = self.calculate_center(cnt) #calculate x, y center contour
                cv2.circle(img, (int(cx), int(cy)), 2, (255,0,0), cv2.FILLED)
                cv2.putText(img ,f"X {int(cx)},Y {int(cy)}", (int(cx)-70, int(cy)-60), 2, 0.75, (255, 0, 0), 2)
                #cv2.circle(self.roi, (int(cx),int(cy)), int(r) , (255, 0, 0), 2)
                x_error = (cx - x_medium)
                y_error = (cy - y_medium)

                if print_str:
                    cv2.putText(img, 'X Error: {:.2f}'.format(x_error/0.533), (5, 20), 2, 0.7, (0, 0, 255), 1)
                    cv2.putText(img, 'Y Error: {:.2f}'.format(y_error/0.436), (5, 40), 2, 0.7, (0, 255, 0), 1)
                    cv2.putText(img, 'Area[px]: {:.2f}'.format(self.area_px), (5, 60), 2, 0.7, (0, 255, 0), 1)
                
                if not self.state:
                    # if self.change_target: 
                    if time.time() - self.prev_time > 5: #0.05 every 50 ms send actual position
                        self.prev_time = time.time()
                        # if((cy < int(y_medium - self.off_set.get())) or (cy > int(y_medium + self.off_set.get()))):
                        #     self.feed_bcak('y', cx, cy, self.kp.get(), self.ki.get(), self.kd.get(), x_medium, y_medium, self.max_speed.get(), self.off_set.get(), "1")
                        # elif((cx < int(x_medium - self.off_set.get())) or (cx > int(x_medium + self.off_set.get()))):
                        #     self.feed_bcak('x', cx, cy, self.kp.get(), self.ki.get(), self.kd.get(), x_medium, y_medium, self.max_speed.get(), self.off_set.get(), "1")
                        print(cx, cy)
                        self.feed_bcak('x', cx, cy, self.kp.get(), self.ki.get(), self.kd.get(), x_medium, y_medium, self.max_speed.get(), self.off_set.get(), "1")
                    if (int(x_medium + self.off_set.get()) > cx > int(x_medium - self.off_set.get())) and (int(y_medium + self.off_set.get()) > cy > int(y_medium - self.off_set.get())):
                        self.color = (0,255,0)
                        if time.time() - self.last_time_update > 1:
                            self.last_time_update = time.time()
                            self.is_true = True #check position in target
                    else:
                        self.is_true = False
                        self.color = (255,0,0)

                cv2.drawContours(img, cnt, -1, self.color, 2)
                # self.change_target = False

    ### --- Earth_comment camera get frame and update auto mode --- ### 
    def show_frame(self):
        
        lower = np.array([self.h_lower.get(), self.s_lower.get(), self.v_lower.get()], np.uint8)
        upper = np.array([self.h_upper.get(), self.s_upper.get(), self.v_upper.get()], np.uint8)
        lower_recv = np.array([self.h_lower.get(), self.s_lower.get(), self.val_low_val.get()], np.uint8)
        upper_recv = np.array([self.h_upper.get(), self.s_upper.get(), self.v_upper.get()], np.uint8)
       
        # lower_thread = np.array([self.hue_lower_val.get(), self.sat_low_val.get(), self.val_low_val.get()], np.uint8)
        # upper_thread = np.array([self.hue_upper_val.get(), self.sat_upper_val.get(), self.val_upper_val.get()], np.uint8)
        # print(lower_thread, upper_thread)

        if self.open_vid:
            _, frame = self.cap1.read()
            origianl = frame.copy()
            origianl = cv2.resize(origianl, (int(origianl.shape[1]*0.35), int(origianl.shape[0]*0.35)), cv2.INTER_AREA)
            origianl = cv2.cvtColor(origianl, cv2.COLOR_BGR2RGB)
            
            #crop image calibarte
            self.roi = origianl[self.st_r.get(): self.end_r.get(), self.st_cl.get(): self.end_cl.get()]
            self.roi = cv2.resize(self.roi, (640, 480), cv2.INTER_AREA)
            hsv = cv2.cvtColor(self.roi, cv2.COLOR_RGB2HSV)
            mask = cv2.inRange(hsv, lower, upper)

            #crop image receiver
            self.recv_frame = origianl[7:91, 306:403]
            self.recv_frame = cv2.resize(self.recv_frame, (320, 320), cv2.INTER_AREA)
            recv_hsv = cv2.cvtColor(self.recv_frame, cv2.COLOR_RGB2HSV)
            recv_mask = cv2.inRange(recv_hsv, lower, upper)
            # cv2.imshow('Calibarte', mask)

            '''cv2.imshow('Receiver', recv_mask)
            # self.roi = cv2.GaussianBlur(self.roi, (3, 3), cv2.BORDER_DEFAULT)
            # roi = cv2.resize(roi, (origianl.shape[1], origianl.shape[0]), cv2.INTER_AREA)
            # x_medium, y_medium = img.shape[1]//2, img.shape[0]//2
            # x_medium, y_medium = self.roi.shape[1]//2, self.roi.shape[0]//2
            # print(x_medium, y_medium)'''
    
            calibarte_contours, h = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            sorted_calibarte_contours = sorted(calibarte_contours, key=cv2.contourArea, reverse=True)

            recv_contours, _ = cv2.findContours(recv_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            sorted_recv_contours = sorted(recv_contours, key=cv2.contourArea, reverse=True)

            if self.state_change:
                #Calibarte
                if sorted_calibarte_contours: self.get_contours(sorted_calibarte_contours, self.roi, 320, 240, self.path_data_log1, True, 0)
            else:
                #Receiver
                if sorted_recv_contours: self.get_contours(sorted_recv_contours, self.recv_frame, 160, 160, self.path_recv_log1, False, 1)
        
            # self.recv_frame = cv2.resize(self.recv_frame, (480, 480), cv2.INTER_AREA)
            recv = Image.fromarray(self.recv_frame)
            self.receiver_vid = ImageTk.PhotoImage(image=recv)
            self.receiver_frame.create_image(0,0,anchor=tk.NW, image=self.receiver_vid)
            # self.monitor_frame.imgtk = imgtk
            # self.monitor_frame.configure(image=imgtk)
            
            self.calibrate = Image.fromarray(self.roi)
            self.calibrate = ImageTk.PhotoImage(image=self.calibrate)
            # self.calibrate_frame.imgtk = mask
            # self.calibrate_frame.configure(image=mask)
            # Update image
            self.calibrate_frame.create_image(0, 0,  anchor=tk.NW, image=self.calibrate)
            self.calibrate_frame.after(2, self.show_frame) #2
            # self.after(10, self.show_frame) #2

if __name__ == "__main__":
    app = App()
















































































