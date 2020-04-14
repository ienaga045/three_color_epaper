import PySimpleGUI as sg
import numpy as np
from PIL import Image, ImageTk

MAX_WIDTH = 255
MAX_HEIGHT = 255
picture_size_x = 255
picture_size_y = 255

def main():
    sg.theme('Default1')
    #ウィンドウレイアウト定義
    layout = [
        [sg.Text('電子ペーパーの画像サイズ', size=(21,1)), sg.Input('212', size=(3,1),key = 'epaper_width'), sg.Text('x', size=(1,1)),
         sg.Input('104', size=(3,1), key = 'epaper_height'), sg.Button('Set'), sg.T('(最大255)')],
        [sg.InputText('PNGファイルを選択', enable_events=True,), sg.FilesBrowse('Select', key='Open_file', file_types=(('PNG ファイル', '*.png'),)), sg.Button('OK'), sg.Button('Resize')],

        #読み込み画像用
        [sg.Graph((MAX_WIDTH, MAX_HEIGHT),(0,MAX_HEIGHT),(MAX_WIDTH, 0), key= 'graph_orig', change_submits=True, drag_submits=True,  # mouse click events 
         background_color='white'), sg.Graph((MAX_WIDTH, MAX_HEIGHT),(0,MAX_HEIGHT),(MAX_WIDTH, 0), key= 'graph_mix', background_color='white')],
        [sg.Graph((MAX_WIDTH, MAX_HEIGHT),(0,MAX_HEIGHT),(MAX_WIDTH, 0), key= 'graph_black', background_color='white'), sg.Graph((MAX_WIDTH, MAX_HEIGHT),(0,MAX_HEIGHT),(MAX_WIDTH, 0), key= 'graph_red', background_color='white')],
        [sg.Text('B/W閾値', size=(7,1)), sg.Slider((0, 255), 128, 1, orientation = 'h', size = (20,15), key = 'black_thresh_slider'),
         sg.Text('R/W閾値', size=(7,1)), sg.Slider((0, 255), 128, 1, orientation = 'h', size = (20,15), key = 'red_thresh_slider')],
        [sg.T(' '*120),sg.Exit()]
    ]
    window = sg.Window('3色電子ペーパーの画像データ生成用のﾊﾟｲﾁｮﾝｱﾌﾟﾘ', layout, location=(400, 200),finalize = True)

    graph_orig = window['graph_orig']
    graph_mix = window['graph_mix']
    graph_black = window['graph_black']
    graph_red = window['graph_red']

    #解像度外エリアをグレーで埋める
    def fill_space_h():
        graph_orig.draw_rectangle((0,height),(255,255), line_color = 'Gray26', fill_color = 'Gray26')
        graph_mix.draw_rectangle((0,height),(255,255), line_color = 'Gray26', fill_color = 'Gray26')
        graph_black.draw_rectangle((0,height),(255,255), line_color = 'Gray26', fill_color = 'Gray26')
        graph_red.draw_rectangle((0,height),(255,255), line_color = 'Gray26', fill_color = 'Gray26')

    def fill_space_v():
        graph_orig.draw_rectangle((width,0),(255,255), line_color = 'Gray26', fill_color = 'Gray26')
        graph_mix.draw_rectangle((width,0),(255,255), line_color = 'Gray26', fill_color = 'Gray26')
        graph_black.draw_rectangle((width,0),(255,255), line_color = 'Gray26', fill_color = 'Gray26')
        graph_red.draw_rectangle((width,0),(255,255), line_color = 'Gray26', fill_color = 'Gray26')

    dragging = False
    start_point = end_point = None
    drag_figures = None
    while True:
        event, values = window.read()
        file_name = values['Open_file']
        height = int(values['epaper_height'])
        width = int(values['epaper_width'])

        #ボタン押下時処理
        if event in (None, 'Exit'): #Exitが押されたらループを抜けて終了
            break
        if event == 'Set':  #電子ペーパー画像サイズ設定処理
            #最大値クリップ
            if height > MAX_HEIGHT :
                height = MAX_HEIGHT
            if width > MAX_WIDTH :
                width = MAX_WIDTH
            #クリップした数値をテキストボックスに反映
            window['epaper_height'].update(str(height))
            window['epaper_width'].update(str(width))
            graph_orig.erase() #一旦初期化
            graph_mix.erase() 
            graph_black.erase() 
            graph_red.erase()  
            if height != 255: 
                fill_space_h()
            if width != 255:
                fill_space_v()
        elif event == 'OK':
            print(file_name)
            graph_orig.DrawImage(filename = file_name, location = (0,0))   #読み込み画像描画
            if height != 255: 
                fill_space_h()
            if width != 255:
                fill_space_v()
            drag_figures = None
            dragging = False
        elif event == 'Resize':
            img = Image.open(file_name)
            resized_width = round(img.width * height / img.height)
            img = img.resize((resized_width, height))
            print(str(resized_width) + ',' + str(height))
            img.save('resized.png')
            graph_orig.erase() #一旦初期化
            graph_orig.DrawImage(filename = './resized.png', location = (0,0))   #読み込み画像描画
            if height != 255: 
                fill_space_h()
            if width != 255:
                fill_space_v()
            drag_figures = None
            dragging = False
        #グラフエリアマウスドラッグ時処理
        if event == 'graph_orig': 
            x, y = values['graph_orig']
            graph_orig.Widget.config(cursor='fleur')
            if not dragging:
                start_point = (x, y)
                dragging = True
                drag_figures = graph_orig.get_figures_at_location((x,y))
                lastxy = x, y
            else:
                end_point = (x, y)
            delta_x, delta_y = x - lastxy[0], y - lastxy[1]
            lastxy = x,y
            if None not in (start_point, end_point):
                for fig in drag_figures:
                    graph_orig.move_figure(fig, delta_x, delta_y)
                    graph_orig.update()
        
    #終了時処理



    window.close()  

main()