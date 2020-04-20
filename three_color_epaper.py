import PySimpleGUI as sg
import numpy as np
from PIL import Image, ImageGrab, ImageChops, ImageOps

MAX_WIDTH = 255
MAX_HEIGHT = 255

#bit列をhexに変換する関数
def array2hex(bit0, bit1, bit2, bit3, bit4, bit5, bit6, bit7):
    pol = False
    hex_data = 0x00
    if bit0 == pol:
        hex_data = hex_data | 0x80
    if bit1 == pol:
        hex_data = hex_data | 0x40
    if bit2 == pol:
        hex_data = hex_data | 0x20
    if bit3 == pol:
        hex_data = hex_data | 0x10
    if bit4 == pol:
        hex_data = hex_data | 0x08
    if bit5 == pol:
        hex_data = hex_data | 0x04
    if bit6 == pol:
        hex_data = hex_data | 0x02
    if bit7 == pol:
        hex_data = hex_data | 0x01
    return hex_data

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
        [sg.InputText('PNG,JPEGファイルを選択', enable_events=True,), sg.FilesBrowse('Select', key='Open_file', file_types=(('PNGファイル', '*.png'),('JPEGファイル', '*.jpg'),)), sg.Button('OK'), sg.Button('Resize'), sg.Button('Rotation')],
        [sg.Graph((MAX_WIDTH, MAX_HEIGHT),(0,MAX_HEIGHT),(MAX_WIDTH, 0), key= 'graph_orig', change_submits=True, drag_submits=True,  # mouse click events 
         background_color='white'), sg.Graph((MAX_WIDTH, MAX_HEIGHT),(0,MAX_HEIGHT),(MAX_WIDTH, 0), key= 'graph_mix', background_color='white')],
        [sg.Graph((MAX_WIDTH, MAX_HEIGHT),(0,MAX_HEIGHT),(MAX_WIDTH, 0), key= 'graph_black', background_color='white'), sg.Graph((MAX_WIDTH, MAX_HEIGHT),(0,MAX_HEIGHT),(MAX_WIDTH, 0), key= 'graph_red', background_color='white')],
        [sg.Text('B/W閾値', size=(7,1)), sg.Slider((0, 255), 128, 1, orientation = 'h', size = (20,15), key = 'black_thresh_slider'),
         sg.Text('R/W閾値', size=(7,1)), sg.Slider((0, 255), 128, 1, orientation = 'h', size = (20,15), key = 'red_thresh_slider')],[sg.Button('Calc'),sg.Button('Save')],
        [sg.T(' '*120),sg.Exit()]
    ]
    window = sg.Window('3色電子ペーパー（Black/Red/White）の画像データ生成用のﾊﾟｲﾁｮﾝｱﾌﾟﾘ', layout, location=(400, 200),finalize = True)

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
    file_name = None
    while True:
        event, values = window.read()
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
            graph_red.erase()   #最大値以外はグレーアウト部を生成
            if height != 255: 
                fill_space_h()
            if width != 255:
                fill_space_v()
        elif event == 'OK': #ファイルオープン処理
            file_name = values['Open_file']
            if file_name.endswith('.jpg'):  #JPEGファイルの場合pngファイルに変換して実行
                img = Image.open(file_name)
                file_name = 'convert_from_jpg.png'
                img.save(file_name)
            graph_orig.erase() #一旦初期化
            graph_orig.DrawImage(filename = file_name, location = (0,0))   #読み込み画像描画
            if height != 255: #最大値以外はグレーアウト部を生成
                fill_space_h()
            if width != 255:
                fill_space_v()
            drag_figures = None
            dragging = False
        elif event == 'Resize': #リサイズ処理
            if file_name is not None:
                img = Image.open(file_name)
                resized_width = round(img.width * height / img.height)
                img = img.resize((resized_width, height))
                file_name = 'resized.png'
                img.save(file_name)
                graph_orig.erase() #一旦初期化
                graph_orig.DrawImage(filename = './resized.png', location = (0,0))   #読み込み画像描画
                if height != 255:  #最大値以外はグレーアウト部を生成
                    fill_space_h()
                if width != 255:
                    fill_space_v()
                drag_figures = None
                dragging = False
        elif event == 'Rotation': #回転処理
            if file_name is not None:
                img = Image.open(file_name)
                img = img.rotate(90, expand=True)
                file_name = 'rotated.png'
                img.save(file_name)
                graph_orig.erase() #一旦初期化
                graph_orig.DrawImage(filename = './rotated.png', location = (0,0))   #読み込み画像描画
                if height != 255:  #最大値以外はグレーアウト部を生成
                    fill_space_h()
                if width != 255:
                    fill_space_v()
                drag_figures = None
                dragging = False
        elif event == 'Calc':   #3値化処理実施
            black_thresh = int(values['black_thresh_slider'])   #スライダーの閾値読み出し
            red_thresh = int(values['red_thresh_slider'])
            filename=r'trim.png'
            save_element_as_file(window['graph_orig'], filename, height , width)    #graph_origのスクショを保存
            img = Image.open('trim.png')
            img_red, img_green, img_blue = img.split()  #RGB抽出
            img_red_bin = img_red.point(lambda x: 0 if x < black_thresh else 1, mode='1')
            img_blue_bin = img_blue.point(lambda x: 0 if x < red_thresh else 1, mode='1')
            img_green_bin = img_green.point(lambda x: 0 if x < red_thresh else 1, mode='1')
            img_black_bin = img_red_bin #黒の抽出
            img_green_and_blue = ImageChops.logical_and(img_green_bin, img_blue_bin)
            img_red_bin = ImageChops.logical_xor(img_red_bin, img_green_and_blue)    #赤の抽出
            mask = img_red_bin
            img_red_bin = ImageChops.invert(img_red_bin)    
            img_black_bin.save('black.png')
            img_red_bin.save('red.png')

            #黒の画像にマスクをかけて、赤を塗る
            img_black = Image.open('black.png')
            img_black = img_black.convert('RGB')
            fill_color = (180,0,0)
            img_black.paste(Image.new('RGB', (width ,height), fill_color), mask = mask)
            img_black.save('black_and_red.png')
            #読み込み画像描画
            graph_black.DrawImage(filename = './black.png', location = (0,0))
            graph_red.DrawImage(filename = './red.png', location = (0,0))
            graph_mix.DrawImage(filename = './black_and_red.png', location = (0,0))
        elif event == 'Save' :      #hexファイル保存処理
            text_file_name = 'hex_datas.txt'    #'0xXX'の形式でテキストとして保存。C言語とかで楽に使える。
            img = Image.open('black.png')
            img = ImageOps.mirror(img)
            black_array = np.array(img)
            text_file = open(text_file_name, 'w') # 書き込みモードで開く
            rem = height % 8    #8で割った時の余り
            for j in range (width):
                for i in range (0, height, 8):
                    if int(height/8) * 8 == i :    #縦の解像度が8で割り切れない時に参照エラーを防ぐための処理 クソコードなので、修正予定
                        if rem == 0:
                            bit0 = black_array[i][j]
                            bit1 = black_array[i+1][j]
                            bit2 = black_array[i+2][j]
                            bit3 = black_array[i+3][j]
                            bit4 = black_array[i+4][j]
                            bit5 = black_array[i+5][j]
                            bit6 = black_array[i+6][j]
                            bit7 = black_array[i+7][j]
                        elif rem == 1:
                            bit0 = black_array[i][j]
                            bit1 = True
                            bit2 = True
                            bit3 = True
                            bit4 = True
                            bit5 = True
                            bit6 = True
                            bit7 = True
                        elif rem == 2:
                            bit0 = black_array[i][j]
                            bit1 = black_array[i+1][j]
                            bit2 = True
                            bit3 = True
                            bit4 = True
                            bit5 = True
                            bit6 = True
                            bit7 = True
                        elif rem == 3:
                            print(str(i))
                            bit0 = black_array[i][j]
                            bit1 = black_array[i+1][j]
                            bit2 = black_array[i+2][j]
                            bit3 = True
                            bit4 = True
                            bit5 = True
                            bit6 = True
                            bit7 = True
                        elif rem == 4:
                            bit0 = black_array[i][j]
                            bit1 = black_array[i+1][j]
                            bit2 = black_array[i+2][j]
                            bit3 = black_array[i+3][j]
                            bit4 = True
                            bit5 = True
                            bit6 = True
                            bit7 = True
                        elif rem == 5:
                            bit0 = black_array[i][j]
                            bit1 = black_array[i+1][j]
                            bit2 = black_array[i+2][j]
                            bit3 = black_array[i+3][j]
                            bit4 = black_array[i+4][j]
                            bit5 = True
                            bit6 = True
                            bit7 = True
                        elif rem == 6:
                            bit0 = black_array[i][j]
                            bit1 = black_array[i+1][j]
                            bit2 = black_array[i+2][j]
                            bit3 = black_array[i+3][j]
                            bit4 = black_array[i+4][j]
                            bit5 = black_array[i+5][j]
                            bit6 = True
                            bit7 = True
                        elif rem == 7:
                            bit0 = black_array[i][j]
                            bit1 = black_array[i+1][j]
                            bit2 = black_array[i+2][j]
                            bit3 = black_array[i+3][j]
                            bit4 = black_array[i+4][j]
                            bit5 = black_array[i+5][j]
                            bit6 = black_array[i+6][j]
                            bit7 = True
                    else :
                        bit0 = black_array[i][j]
                        bit1 = black_array[i+1][j]
                        bit2 = black_array[i+2][j]
                        bit3 = black_array[i+3][j]
                        bit4 = black_array[i+4][j]
                        bit5 = black_array[i+5][j]
                        bit6 = black_array[i+6][j]
                        bit7 = black_array[i+7][j]

                    hex_data = array2hex(bit0, bit1, bit2, bit3, bit4, bit5, bit6, bit7)
                    hex_txt = hex(hex_data)
                    text_file.write('0x'+ hex_txt[2:].zfill(2) + ',' ) #0埋めの為のヘンテコ処理
                text_file.write('\n')
            img = Image.open('red.png')
            img = ImageOps.mirror(img)
            red_array = np.array(img)
            for j in range (width):
                for i in range (0, height, 8):
                    if int(height/8) * 8 == i :    #縦の解像度が8で割り切れない時に参照エラーを防ぐための処理 クソコードなので、修正予定
                        if rem == 0:
                            bit0 = red_array[i][j]
                            bit1 = red_array[i+1][j]
                            bit2 = red_array[i+2][j]
                            bit3 = red_array[i+3][j]
                            bit4 = red_array[i+4][j]
                            bit5 = red_array[i+5][j]
                            bit6 = red_array[i+6][j]
                            bit7 = red_array[i+7][j]
                        elif rem == 1:
                            bit0 = red_array[i][j]
                            bit1 = True
                            bit2 = True
                            bit3 = True
                            bit4 = True
                            bit5 = True
                            bit6 = True
                            bit7 = True
                        elif rem == 2:
                            bit0 = red_array[i][j]
                            bit1 = red_array[i+1][j]
                            bit2 = True
                            bit3 = True
                            bit4 = True
                            bit5 = True
                            bit6 = True
                            bit7 = True
                        elif rem == 3:
                            bit0 = red_array[i][j]
                            bit1 = red_array[i+1][j]
                            bit2 = red_array[i+2][j]
                            bit3 = True
                            bit4 = True
                            bit5 = True
                            bit6 = True
                            bit7 = True
                        elif rem == 4:
                            bit0 = red_array[i][j]
                            bit1 = red_array[i+1][j]
                            bit2 = red_array[i+2][j]
                            bit3 = red_array[i+3][j]
                            bit4 = True
                            bit5 = True
                            bit6 = True
                            bit7 = True
                        elif rem == 5:
                            bit0 = red_array[i][j]
                            bit1 = red_array[i+1][j]
                            bit2 = red_array[i+2][j]
                            bit3 = red_array[i+3][j]
                            bit4 = red_array[i+4][j]
                            bit5 = True
                            bit6 = True
                            bit7 = True
                        elif rem == 6:
                            bit0 = red_array[i][j]
                            bit1 = red_array[i+1][j]
                            bit2 = red_array[i+2][j]
                            bit3 = red_array[i+3][j]
                            bit4 = red_array[i+4][j]
                            bit5 = red_array[i+5][j]
                            bit6 = True
                            bit7 = True
                        elif rem == 7:
                            bit0 = red_array[i][j]
                            bit1 = red_array[i+1][j]
                            bit2 = red_array[i+2][j]
                            bit3 = red_array[i+3][j]
                            bit4 = red_array[i+4][j]
                            bit5 = red_array[i+5][j]
                            bit6 = red_array[i+6][j]
                            bit7 = True
                    else :
                        bit0 = red_array[i][j]
                        bit1 = red_array[i+1][j]
                        bit2 = red_array[i+2][j]
                        bit3 = red_array[i+3][j]
                        bit4 = red_array[i+4][j]
                        bit5 = red_array[i+5][j]
                        bit6 = red_array[i+6][j]
                        bit7 = red_array[i+7][j]

                    hex_data = array2hex(bit0, bit1, bit2, bit3, bit4, bit5, bit6, bit7)
                    hex_txt = hex(hex_data)
                    text_file.write('0x'+ hex_txt[2:].zfill(2) + ',' ) #0埋めの為のヘンテコ処理
                text_file.write('\n')
            text_file.close() # ファイルを閉じる
        if event == 'graph_orig':         #グラフエリアマウスドラッグ時処理
            x, y = values['graph_orig']
            graph_orig.Widget.config(cursor='fleur')
            if not dragging:
                start_point = (x, y)
                dragging = True
                if x > width-1: #描画エリア外のグレーアウト部を選択できない様にする為の処理
                    x = width-1
                if y > height-1:
                    y = height-1
                drag_figures = graph_orig.get_figures_at_location((x,y))    #クリックした場所のオブジェクトを取得
                lastxy = x, y
            else:
                end_point = (x, y)
            delta_x, delta_y = x - lastxy[0], y - lastxy[1]
            lastxy = x,y
            if None not in (start_point, end_point):    
                for fig in drag_figures:
                    graph_orig.move_figure(fig, delta_x, delta_y)
                    graph_orig.update()
        else:   #ドラッグ終了時処理
            start_point, end_point = None, None
            dragging = False
    #終了時処理
    window.close()  

main()