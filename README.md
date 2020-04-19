# 電子ペーパー用データ作成ソフト（開発中）
PNG画像を読み込んで、拡大・縮小・回転・移動の編集、3値（黒・赤）のバイナリデータを生成するGUIアプリ
![UI](https://raw.githubusercontent.com/ienaga045/three_color_epaper/master/UI_animation.gif)

## 出力ファイル例

![HEX](https://raw.githubusercontent.com/ienaga045/three_color_epaper/master/hex_text.png)

## 電子ペーパー表示例

<img src="https://raw.githubusercontent.com/ienaga045/three_color_epaper/master/e-paper_sample1.jpg" width=50%><img src="https://raw.githubusercontent.com/ienaga045/three_color_epaper/master/e-paper_sample2.jpg" width=50%>



## 仕様
- PNGフォーマットに対応
- 最大解像度は255x255
- データ方向は縦方向スキャン
- 0x00~0xffのuint8のテキストデータを出力
- モノクロ・3色用のテキストデータを出力
- PySimpeGUI、numpy、PILのインストールが別途必要
- macOS、Linuxでも動作（するはず…

## おまけ
本プログラムで生成したファイルをUartで転送するサンプルプログラムも作成しましたので、[参考まで。](https://github.com/ienaga045/simple_binary_uart)