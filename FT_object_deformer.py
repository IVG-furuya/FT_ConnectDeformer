import maya.cmds as cmds
import maya.OpenMayaUI as omui

# PySide2/PySide6 互換インポート
try:
    from PySide2.QtWidgets import (
        QDialog, QLabel, QListWidget, QPushButton, QVBoxLayout,
        QHBoxLayout, QGroupBox, QWidget
    )
    from PySide2.QtCore import Qt
    from PySide2.QtGui import QColor
    from shiboken2 import wrapInstance
except ImportError:
    from PySide6.QtWidgets import (
        QDialog, QLabel, QListWidget, QPushButton, QVBoxLayout,
        QHBoxLayout, QGroupBox, QWidget
    )
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor
    from shiboken6 import wrapInstance

def maya_main_window():
    """Mayaのメインウィンドウを取得する。
    
    Returns:
        QWidget: Mayaのメインウィンドウ
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QWidget)


class FTConnectDeformerGUI(QDialog):
    def __init__(self, parent=maya_main_window()):
        """初期化。
        
        Args:
            parent (QWidget, optional): 親ウィジェット。デフォルトはMayaのメインウィンドウ。
        """
        super(FTConnectDeformerGUI, self).__init__(parent)
        
        self.setWindowTitle("FT Connect Deformer")
        self.setWindowFlags(Qt.Window)
        self.setMinimumSize(400, 500)
        
        # データ格納用リスト
        self.stored_objects = []
        self.stored_deformers = []
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
    def create_widgets(self):
        """UIウィジェットを作成する。"""
        # オブジェクトセクション
        self.objects_label = QLabel("変形対象オブジェクト:")
        self.objects_list = QListWidget()
        self.objects_list.setMaximumHeight(150)
        self.add_objects_btn = QPushButton("選択したオブジェクトを追加")
        self.remove_objects_btn = QPushButton("選択項目を削除")
        
        # デフォーマーセクション
        self.deformers_label = QLabel("デフォーマー:")
        self.deformers_list = QListWidget()
        self.deformers_list.setMaximumHeight(150)
        self.add_deformers_btn = QPushButton("選択したデフォーマーを追加")
        self.force_add_btn = QPushButton("強制追加（検証なし）")
        self.force_add_btn.setStyleSheet(
            "QPushButton { "
            "background-color: #FF9800; "
            "color: white; "
            "}")
        self.remove_deformers_btn = QPushButton("選択項目を削除")
        
        # 実行ボタン
        self.apply_btn = QPushButton("デフォーマーを適用")
        self.apply_btn.setStyleSheet(
            "QPushButton { "
            "background-color: #4CAF50; "
            "color: white; "
            "font-weight: bold; "
            "padding: 8px; "
            "}")
        
        # リセットボタン
        self.reset_btn = QPushButton("リセット")
        self.reset_btn.setStyleSheet(
            "QPushButton { "
            "background-color: #f44336; "
            "color: white; "
            "padding: 8px; "
            "}")
        
        # 閉じるボタン
        self.close_btn = QPushButton("閉じる")
        
        # ステータスラベル
        self.status_label = QLabel("準備完了")
        self.status_label.setStyleSheet(
            "QLabel { "
            "color: #333; "
            "padding: 5px; "
            "}")
        
    def create_layouts(self):
        """UIレイアウトを作成する。"""
        main_layout = QVBoxLayout(self)
        
        # オブジェクトセクション
        objects_group = QGroupBox("変形対象オブジェクト")
        objects_layout = QVBoxLayout()
        objects_layout.addWidget(self.objects_list)
        
        objects_btn_layout = QHBoxLayout()
        objects_btn_layout.addWidget(self.add_objects_btn)
        objects_btn_layout.addWidget(self.remove_objects_btn)
        objects_layout.addLayout(objects_btn_layout)
        
        objects_group.setLayout(objects_layout)
        main_layout.addWidget(objects_group)
        
        # デフォーマーセクション
        deformers_group = QGroupBox("デフォーマー")
        deformers_layout = QVBoxLayout()
        deformers_layout.addWidget(self.deformers_list)
        
        deformers_btn_layout = QHBoxLayout()
        deformers_btn_layout.addWidget(self.add_deformers_btn)
        deformers_btn_layout.addWidget(self.force_add_btn)
        deformers_btn_layout.addWidget(self.remove_deformers_btn)
        deformers_layout.addLayout(deformers_btn_layout)
        
        deformers_group.setLayout(deformers_layout)
        main_layout.addWidget(deformers_group)
        
        # 実行ボタンセクション
        main_layout.addWidget(self.apply_btn)
        
        # 下部ボタン
        bottom_btn_layout = QHBoxLayout()
        bottom_btn_layout.addWidget(self.reset_btn)
        bottom_btn_layout.addStretch()
        bottom_btn_layout.addWidget(self.close_btn)
        main_layout.addLayout(bottom_btn_layout)
        
        # ステータス
        main_layout.addWidget(self.status_label)
        
    def create_connections(self):
        """シグナルとスロットを接続する。"""
        # オブジェクト関連ボタン
        self.add_objects_btn.clicked.connect(self.add_selected_objects)
        self.remove_objects_btn.clicked.connect(self.remove_selected_objects)
        
        # デフォーマー関連ボタン
        self.add_deformers_btn.clicked.connect(self.add_selected_deformers)
        self.force_add_btn.clicked.connect(self.force_add_deformers)
        self.remove_deformers_btn.clicked.connect(self.remove_selected_deformers)
        
        # 実行・制御ボタン
        self.apply_btn.clicked.connect(self.apply_deformers)
        self.reset_btn.clicked.connect(self.reset_all)
        self.close_btn.clicked.connect(self.close)
        
    def add_selected_objects(self):
        """選択したオブジェクトをリストに追加する。"""
        selection = cmds.ls(selection=True, type='transform')
        if not selection:
            self.update_status(
                "オブジェクトが選択されていません", "warning")
            return
            
        added_count = 0
        for obj in selection:
            if obj not in self.stored_objects:
                self.stored_objects.append(obj)
                self.objects_list.addItem(obj)
                added_count += 1
                
        if added_count > 0:
            self.update_status(
                f"{added_count}個のオブジェクトを追加しました", 
                "success")
        else:
            self.update_status(
                "既に追加済みのオブジェクトです", "info")
            
    def remove_selected_objects(self):
        """選択したオブジェクトをリストから削除する。"""
        current_row = self.objects_list.currentRow()
        if current_row >= 0:
            item = self.objects_list.takeItem(current_row)
            self.stored_objects.remove(item.text())
            self.update_status(
                "オブジェクトを削除しました", "info")
        else:
            self.update_status(
                "削除するアイテムを選択してください", "warning")
            
    def add_selected_deformers(self):
        """選択したデフォーマーをリストに追加する。"""
        selection = cmds.ls(selection=True)
        if not selection:
            self.update_status(
                "デフォーマーが選択されていません", "warning")
            return
            
        added_count = 0
        skipped_count = 0
        
        for item in selection:
            # デフォーマーかどうかチェック
            deformer_result = self.is_deformer(item)
            
            # クラスターハンドルの特別処理
            is_cluster = 'cluster' in item.lower()
            if is_cluster and not deformer_result['is_deformer']:
                # クラスターハンドルの場合は特別に処理
                try:
                    # 関連するクラスターノードを探す
                    cluster_nodes = cmds.listConnections(item, type='cluster')
                    if cluster_nodes:
                        # 関連するクラスターノードを使用
                        item = cluster_nodes[0]
                        deformer_result = {'is_deformer': True, 'type': 'cluster'}
                        print(f"クラスターハンドル '{item}' から"
                              f"クラスターノード '{cluster_nodes[0]}' を使用します")
                except Exception as e:
                    print(f"クラスター処理エラー: {e}")
                    
            # nonLinearハンドルの特別処理
            nonlinear_types = ['twist', 'bend', 'sine', 'wave', 'flare', 'squash']
            is_nonlinear = any(nl_type in item.lower() for nl_type in nonlinear_types)
            if is_nonlinear and not deformer_result['is_deformer']:
                try:
                    # 関連するnonLinearノードを探す
                    nonlinear_nodes = cmds.listConnections(item, type='nonLinear')
                    if nonlinear_nodes:
                        # 関連するnonLinearノードを使用
                        item = nonlinear_nodes[0]
                        deformer_result = {'is_deformer': True, 'type': 'nonLinear'}
                        print(f"nonLinearハンドル '{item}' から"
                              f"nonLinearノード '{nonlinear_nodes[0]}' を使用します")
                except Exception as e:
                    print(f"nonLinear処理エラー: {e}")
            
            if deformer_result['is_deformer']:
                if item not in self.stored_deformers:
                    self.stored_deformers.append(item)
                    # デフォーマータイプも表示
                    display_name = f"{item} ({deformer_result['type']})"
                    self.deformers_list.addItem(display_name)
                    added_count += 1
                else:
                    skipped_count += 1
            else:
                # デバッグ情報を表示
                print(f"デバッグ: '{item}' のタイプは '{deformer_result['type']}' です")
                self.update_status(
                    f"'{item}' は有効なデフォーマーではありません "
                    f"(タイプ: {deformer_result['type']})", 
                    "warning")
                
        if added_count > 0:
            self.update_status(
                f"{added_count}個のデフォーマーを追加しました", 
                "success")
        elif skipped_count > 0:
            self.update_status(
                "既に追加済みのデフォーマーです", 
                "info")
        elif len(selection) > 0:
            self.update_status(
                "選択されたアイテムにデフォーマーが含まれていません", 
                "warning")
            
    def force_add_deformers(self):
        """選択したアイテムを強制的にデフォーマーとして追加（検証なし）。"""
        selection = cmds.ls(selection=True)
        if not selection:
            self.update_status(
                "アイテムが選択されていません", "warning")
            return
            
        added_count = 0
        for item in selection:
            if item not in self.stored_deformers:
                self.stored_deformers.append(item)
                # 強制追加の場合は [強制] マークを付ける
                display_name = f"{item} [強制追加]"
                self.deformers_list.addItem(display_name)
                added_count += 1
                    
            if added_count > 0:
                self.update_status(
                    f"{added_count}個のアイテムを強制追加しました", 
                    "success")
            else:
                self.update_status(
                    "既に追加済みのアイテムです", 
                    "info")
            
    def remove_selected_deformers(self):
        """選択したデフォーマーをリストから削除する。"""
        current_row = self.deformers_list.currentRow()
        if current_row >= 0:
            item = self.deformers_list.takeItem(current_row)
            # 表示名から実際のデフォーマー名を抽出 
            # 例: "cluster1 (cluster)" -> "cluster1" または "item1 [強制追加]" -> "item1"
            display_text = item.text()
            if ' (' in display_text:
                actual_name = display_text.split(' (')[0]
            elif ' [' in display_text:
                actual_name = display_text.split(' [')[0]
            else:
                actual_name = display_text
            
            if actual_name in self.stored_deformers:
                self.stored_deformers.remove(actual_name)
            self.update_status(
                "デフォーマーを削除しました", "info")
        else:
            self.update_status(
                "削除するアイテムを選択してください", "warning")
            
    def is_deformer(self, node):
        """ノードがデフォーマーかどうかチェックする。
        
        Args:
            node (str): チェック対象のノード名
            
        Returns:
            dict: デフォーマー情報を含む辞書
                - is_deformer (bool): デフォーマーかどうか
                - type (str): ノードタイプ
        """
        try:
            node_type = cmds.nodeType(node)
            
            # より包括的なデフォーマータイプリスト
            deformer_types = [
                # 基本デフォーマー
                'cluster', 'skinCluster', 'blendShape', 'lattice', 'ffd',
                'nonLinear', 'sculpt', 'wrap', 'wire', 'jiggle', 'softMod',
                'tweak', 'groupParts', 'groupId', 'objectSet',
                # nonLinearデフォーマーの具体的なタイプ
                'sine', 'squash', 'twist', 'wave', 'flare', 'bend',
                # ハンドルタイプ
                'clusterHandle', 'latticeShape'
            ]
            
            # デフォーマーの継承チェック
            is_deformer_node = False
            debug_info = []
            
            # 直接的なタイプチェック
            if node_type in deformer_types:
                is_deformer_node = True
                debug_info.append(f"直接タイプマッチ: {node_type}")
            
            # Cluster特殊ケース
            if not is_deformer_node:
                # クラスターハンドルの場合
                if 'cluster' in node.lower():
                    try:
                        # クラスターハンドルかチェック
                        is_cluster_handle = cmds.objectType(
                            node, isAType='clusterHandle')
                        is_transform = cmds.objectType(
                            node, isAType='transform')
                            
                        if is_cluster_handle or is_transform:
                            connections = cmds.listConnections(
                                node, type='cluster') or []
                            if connections:
                                is_deformer_node = True
                                node_type = 'clusterHandle'
                                debug_info.append(
                                    f"クラスター接続検出: {connections}")
                    except Exception as e:
                        debug_info.append(f"クラスターチェックエラー: {e}")
            
            # NonLinear特殊ケース
            if not is_deformer_node:
                nonlinear_types = ['twist', 'bend', 'sine', 'wave', 'flare', 'squash']
                nl_match = any(nl_type in node.lower() for nl_type in nonlinear_types)
                if nl_match:
                    try:
                        # nonLinearハンドルかチェック
                        connections = cmds.listConnections(
                            node, type='nonLinear') or []
                        if connections:
                            is_deformer_node = True
                            node_type = 'nonLinearHandle'
                            debug_info.append(
                                f"nonLinear接続検出: {connections}")
                        # 直接nonLinearタイプかチェック
                        elif cmds.objectType(node, isAType='nonLinear'):
                            is_deformer_node = True
                            node_type = 'nonLinear'
                            debug_info.append("nonLinearタイプ検出")
                    except Exception as e:
                        debug_info.append(f"nonLinearチェックエラー: {e}")
            
            # Maya APIを使用してデフォーマーの継承をチェック
            if not is_deformer_node:
                try:
                    # デフォーマーベースクラスから継承しているかチェック
                    if cmds.nodeType(node, isTypeName=True):
                        inheritance = cmds.nodeType(node, inherited=True) or []
                        base_types = ['deformer', 'geometryFilter']
                        if any(bt in str(inheritance) for bt in base_types):
                            is_deformer_node = True
                            debug_info.append(f"継承検出: {inheritance}")
                except Exception as e:
                    debug_info.append(f"継承チェックエラー: {e}")
            
            # 特別なケース: transformノードでもdeformerコマンドで使用可能な場合
            if not is_deformer_node and node_type == 'transform':
                # クラスターハンドルなどの可能性をチェック
                try:
                    # 子シェイプをチェック
                    shapes = cmds.listRelatives(
                        node, shapes=True, fullPath=True) or []
                    for shape in shapes:
                        shape_type = cmds.nodeType(shape)
                        if shape_type in deformer_types:
                            is_deformer_node = True
                            node_type = shape_type
                            debug_info.append(f"子シェイプ検出: {shape_type}")
                            break
                        
                                        # 接続をチェック
                    if not is_deformer_node:
                        deformer_check_types = [
                            'cluster', 'nonLinear', 'lattice', 'blendShape'
                        ]
                        for deformer_type in deformer_check_types:
                            connections = cmds.listConnections(
                                node, type=deformer_type) or []
                            if connections:
                                is_deformer_node = True
                                node_type = f"{deformer_type}Handle"
                                debug_info.append(
                                    f"{deformer_type}接続検出: {connections}")
                                break
                except Exception as e:
                    debug_info.append(f"Transform特殊チェックエラー: {e}")
            
            # デバッグ情報を出力
            if debug_info:
                debug_str = ' | '.join(debug_info)
                print(f"デバッグ情報 ({node}): {debug_str}")
            
            return {
                'is_deformer': is_deformer_node,
                'type': node_type
            }
            
        except Exception as e:
            print(f"デバッグ: is_deformer エラー: {e}")
            return {
                'is_deformer': False,
                'type': 'unknown'
            }
            
    def apply_deformers(self):
        """デフォーマーを適用する。"""
        if not self.stored_objects:
            self.update_status(
                "変形対象オブジェクトが設定されていません", 
                "error")
            return
            
        if not self.stored_deformers:
            self.update_status(
                "デフォーマーが設定されていません", 
                "error")
            return
            
        success_count = 0
        error_count = 0
        
        for deformer in self.stored_deformers:
            for obj in self.stored_objects:
                try:
                    cmds.deformer(deformer, edit=True, geometry=obj)
                    success_count += 1
                    print(f"'{obj}' をデフォーマー '{deformer}' に追加しました。")
                except RuntimeError as e:
                    error_count += 1
                    print(f"エラー: '{obj}' を '{deformer}' に"
                          f"追加できませんでした。{e}")
                    
        if error_count == 0:
            self.update_status(
                f"成功: {success_count}個の接続を作成しました", 
                "success")
        else:
            self.update_status(
                f"完了: {success_count}個成功, {error_count}個失敗", 
                "warning")
            
    def reset_all(self):
        """すべての選択とリストをリセットする。"""
        self.stored_objects.clear()
        self.stored_deformers.clear()
        self.objects_list.clear()
        self.deformers_list.clear()
        self.update_status(
            "リセットしました", 
            "info")
        
    def update_status(self, message, status_type="info"):
        """ステータスメッセージを更新する。
        
        Args:
            message (str): 表示するメッセージ
            status_type (str, optional): メッセージの種類。
                'success', 'warning', 'error', 'info'のいずれか。
                デフォルトは'info'。
        """
        # ステータスタイプに応じた色の定義
        colors = {
            "success": "#4CAF50",  # 緑
            "warning": "#FF9800",  # オレンジ
            "error": "#f44336",    # 赤
            "info": "#2196F3"      # 青
        }
        color = colors.get(status_type, "#333")
        self.status_label.setText(message)
        self.status_label.setStyleSheet(
            f"QLabel {{ "
            f"color: {color}; "
            f"padding: 5px; "
            f"font-weight: bold; "
            f"}}")

def show_connect_to_deformer_gui():
    """GUIを表示する関数。
    既存のGUIがある場合は閉じて新しいインスタンスを作成する。
    """
    global connect_to_deformer_gui
    try:
        connect_to_deformer_gui.close()
        connect_to_deformer_gui.deleteLater()
    except (NameError, AttributeError):
        pass
    
    connect_to_deformer_gui = FTConnectDeformerGUI()
    connect_to_deformer_gui.show()


# 実行
if __name__ == "__main__":
    show_connect_to_deformer_gui()