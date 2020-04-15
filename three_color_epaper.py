import PySimpleGUI as sg
import numpy as np
from PIL import Image, ImageGrab, ImageChops

MAX_WIDTH = 255
MAX_HEIGHT = 255
picture_size_x = 255
picture_size_y = 255


def save_element_as_file(element, filename, height, width):
    """
    Saves any element as an image file.  Element needs to have an underlyiong Widget available (almost if not all of them do)
    :param element: The element to save
    :param filename: The filename to save to. The extension of the filename determines the format (jpg, png, gif, ?)
    """
    widget = element.Widget
    box = (widget.winfo_rootx(), widget.winfo_rooty(), widget.winfo_rootx() + widget.winfo_width() - (257 - width), widget.winfo_rooty() + widget.winfo_height() - (257 - height))
    grab = ImageGrab.grab(bbox=box)
    grab.save(filename)


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
         sg.Text('R/W閾値', size=(7,1)), sg.Slider((0, 255), 128, 1, orientation = 'h', size = (20,15), key = 'red_thresh_slider')],[sg.Button('Calc')],
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
        elif event == 'Calc':
            black_thresh = int(values['black_thresh_slider'])
            red_thresh = int(values['red_thresh_slider'])
            filename=r'trim.png'
            save_element_as_file(window['graph_orig'], filename, height , width)    #graph_origのスクショを保存
            #img = np.array(Image.open('trim.png'))  #スクショ部読み出し、np配列化
            img = Image.open('trim.png')

            #RGB抽出
            img_red, img_green, img_blue = img.split()
            #黒抽出
            img_red_bin = img_red.point(lambda x: 0 if x < black_thresh else 1, mode='1')
            #img_blue_bin = img_blue.point(lambda x: 0 if x < red_thresh else 1, mode='1')
            img_green_bin = img_green.point(lambda x: 0 if x < red_thresh else 1, mode='1')

            img_black_bin = img_red_bin #黒の抽出
            img_red_bin = ImageChops.logical_xor(img_red_bin, img_green_bin)    #赤の抽出
            mask = img_red_bin
            img_red_bin = ImageChops.invert(img_red_bin)    
            img_black_bin.save('black.png')
            img_red_bin.save('red.png')

            #黒の画像にマスクをかけて、赤を塗る
            img_black = Image.open('black.png')
            img_black = img_black.convert('RGB')
            fill_color = (255,0,0)
            img_black.paste(Image.new('RGB', (width ,height), fill_color), mask = mask)

            img_black.save('black_and_red.png')
            #img_red_color.save('red_color')
            #Image.fromarray(np.uint8(img_red_bin)).save('red.png')

            #読み込み画像描画
            graph_black.DrawImage(filename = './black.png', location = (0,0))
            graph_red.DrawImage(filename = './red.png', location = (0,0))
            graph_mix.DrawImage(filename = './black_and_red.png', location = (0,0))


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