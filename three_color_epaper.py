import PySimpleGUI as sg
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk

MAX_WIDTH = 255
MAX_HIGHT = 255
picture_size_x = 255
picture_size_y = 255



def main():
    sg.theme('Default1')
    #ウィンドウレイアウト定義
    layout = [
        [sg.Text('電子ペーパーの画像サイズ', size=(21,1)), sg.Input('212', size=(3,1),key = 'epaper_width'), sg.Text('x', size=(1,1)),
         sg.Input('104', size=(3,1), key = 'epaper_hight'), sg.Button('Set'), sg.T('(最大255)')],
        [sg.InputText('PNGファイルを選択', enable_events=True,), sg.FilesBrowse('Select', key='Open_file', file_types=(('PNG ファイル', '*.png'),)), sg.Button('OK')],

        #読み込み画像用
        [sg.Canvas(size =(MAX_WIDTH, MAX_HIGHT), key= 'canvas_orig', background_color='white'), sg.Canvas(size =(MAX_WIDTH, MAX_HIGHT), key= 'canvas_mix', background_color='white')],
        [sg.Canvas(size =(MAX_WIDTH, MAX_HIGHT), key= 'canvas_black', background_color='white'), sg.Canvas(size =(MAX_WIDTH, MAX_HIGHT), key= 'canvas_red', background_color='white')],
        [sg.Text('B/W閾値', size=(7,1)), sg.Slider((0, 255), 128, 1, orientation = 'h', size = (20,15), key = 'black_thresh_slider'),
         sg.Text('R/W閾値', size=(7,1)), sg.Slider((0, 255), 128, 1, orientation = 'h', size = (20,15), key = 'red_thresh_slider')],
        [sg.T(' '*120),sg.Exit()]
    ]
    window = sg.Window('3色電子ペーパーの画像データ生成用のﾊﾟｲﾁｮﾝｱﾌﾟﾘ', layout, location=(400, 200),finalize = True)

    canvas_orig = window['canvas_orig']
    canvas_mix = window['canvas_mix']
    canvas_black = window['canvas_black']
    canvas_red = window['canvas_red']


    while True:
        event, values = window.read(timeout=500)    # returns every 500 ms

        hight = int(values['epaper_hight'])
        width = int(values['epaper_width'])
        if event in (None, 'Exit'): #Exitが押されたらループを抜けて終了
            break
        if event == 'Set':  #電子ペーパー画像サイズ設定処理
            #最大値クリップ
            if hight > MAX_HIGHT :
                hight = MAX_HIGHT
            if width > MAX_WIDTH :
                width = MAX_WIDTH
            #クリップした数値をテキストボックスに反映
            window['epaper_hight'].update(str(hight))
            window['epaper_width'].update(str(width))
            canvas_orig.TKCanvas.create_rectangle(0,0,255,255, outline = 'white', fill = 'white') #一旦初期化
            canvas_mix.TKCanvas.create_rectangle(0,0,255,255, outline = 'white', fill = 'white') 
            canvas_black.TKCanvas.create_rectangle(0,0,255,255, outline = 'white', fill = 'white') 
            canvas_red.TKCanvas.create_rectangle(0,0,255,255, outline = 'white', fill = 'white') 

            if hight != 255: 
                canvas_orig.TKCanvas.create_rectangle(0,hight,255,255, outline = 'Gray26', fill = 'Gray26')
                canvas_mix.TKCanvas.create_rectangle(0,hight,255,255, outline = 'Gray26', fill = 'Gray26')
                canvas_black.TKCanvas.create_rectangle(0,hight,255,255, outline = 'Gray26', fill = 'Gray26')
                canvas_red.TKCanvas.create_rectangle(0,hight,255,255, outline = 'Gray26', fill = 'Gray26')
            if width != 255:
                canvas_orig.TKCanvas.create_rectangle(width,0,255,255, outline = 'Gray26', fill = 'Gray26')
                canvas_mix.TKCanvas.create_rectangle(width,0,255,255, outline = 'Gray26', fill = 'Gray26')
                canvas_black.TKCanvas.create_rectangle(width,0,255,255, outline = 'Gray26', fill = 'Gray26')
                canvas_red.TKCanvas.create_rectangle(width,0,255,255, outline = 'Gray26', fill = 'Gray26')

        elif event == 'OK':
            file_name = values['Open_file']
            print(file_name)
            image_init = Image.open(file_name)
            image_init= ImageTk.PhotoImage(image_init)
            canvas_orig.TKCanvas.create_image(0,0,image = image_init, anchor = tk.NW)   #読み込み画像描画
            if hight != 255: 
                canvas_orig.TKCanvas.create_rectangle(0,hight,255,255, outline = 'Gray26', fill = 'Gray26')
                canvas_mix.TKCanvas.create_rectangle(0,hight,255,255, outline = 'Gray26', fill = 'Gray26')
            if width != 255:
                canvas_orig.TKCanvas.create_rectangle(width,0,255,255, outline = 'Gray26', fill = 'Gray26')
                canvas_mix.TKCanvas.create_rectangle(width,0,255,255, outline = 'Gray26', fill = 'Gray26')


    #終了時処理
    window.close()  
main()