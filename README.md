# オブジェクトをデフォーマに接続するツール

## 概要
複数のオブジェクトを既存のデフォーマに一括で接続するためのツールです。

## インストール方法
 - FT_object_deformer.pyファイルをMayaのスクリプトディレクトリに配置します。
    - Windows: C:\Users\<ユーザー名>\Documents\maya\scripts
    - Mac: ~/Library/Preferences/Autodesk/maya/scripts
    - Linux: ~/maya/scripts

## 使用方法
![image](images/sample.gif)

1. スクリプトをMayaのスクリプトエディタで実行するか、Pythonモジュールとしてインポートします。

    ```python
    import FT_object_deformer
    FT_object_deformer.show_connect_to_deformer_gui()
    ```

2. デフォーマを適用したいオブジェクトを「変形対象オブジェクト」に追加します
3. 適用させたいデフォーマを「デフォーマ」に追加します
4. 「デフォーマを適用」ボタンを押すと変形対象オブジェクトにデフォーマが適用されます

## エラー処理
「選択したデフォーマを追加」で追加されない場合は「強制追加（検証なし）」を使用してください

## 動作環境
- Maya 2020以降
- Python 3.x

## バージョン
- 1.0: 初版リリース