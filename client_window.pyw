import sys
import winreg

from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QLineEdit, QHBoxLayout, QVBoxLayout,
                             QColorDialog, QInputDialog, QFileDialog,
                             QMainWindow, QLabel, QGroupBox, QFormLayout,
                             QScrollArea, QFrame, QComboBox, QSystemTrayIcon,
                             QMenu, QAction)
from PyQt5.QtCore import Qt, QSize, QAbstractTableModel, QVariant, QPoint, pyqtSignal
from PyQt5.QtGui import QCursor,QColor, QImage, QPalette, QBrush, QPixmap, QIcon
from client.client import Client
from utils import save_config, load_config

BUTTON_ON_STYLE = """
    QPushButton{ background-color: #00D473; margin-left: 10px; margin-right: 10px; }
    QPushButton:hover{ background-color: #11E584; margin-left: 10px; margin-right: 10px; }
    QPushButton:pressed{ background-color: #00C362; margin-left: 10px; margin-right: 10px; }
"""

BUTTON_OFF_STYLE = """
    QPushButton{ background-color: #FF4C29; margin-left: 10px; margin-right: 10px; }
    QPushButton:hover{ background-color: #FF5D3A; margin-left: 10px; margin-right: 10px; }
    QPushButton:pressed{ background-color: #EE3B18; margin-left: 10px; margin-right: 10px; }
"""

class FrontWindow(QMainWindow):
    m_drag = True
    m_DragPosition = None
    client = None
    is_global = False
    is_boot = False

    def __init__(self):
        super().__init__()

        self.style = """
            QLineEdit{
                border: 2px solid;
                border-color: #119DCB;
                border-radius: 5px;
                color: #505050;
                font-family: "Microsoft Yahei";
            }
            QLineEdit:focus{
                border: 2px solid;
                border-color: #33BFED;
                border-radius: 5px;
                color: #505050;
                font-family: "Microsoft Yahei";
            }
            QAbstractItemView{
                border: 2px solid;
                border-color: #33BFED;
                border-radius: 5px;
                padding: 2px;
                selection-color: #303030;
                selection-background-color: white;
                background-color: white;
                color: #808080;
            }
            QPushButton{
                background-color: #008CBA;
                border-radius: 3px;
                color: white;
                padding: 5px 5px;
                text-align: center;
                font-size: 16px;
                font-family: "Microsoft Yahei";
            }
            QPushButton:hover{
                background-color: #119DCB;
                border-radius: 3px;
                color: white;
                padding: 5px 5px;
                text-align: center;
                font-size: 16px;
                font-family: "Microsoft Yahei";
            }
            QPushButton:pressed{
                background-color: #007BA9;
                border-radius: 3px;
                color: white;
                padding: 5px 5px;
                text-align: center;
                font-size: 16px;
                font-family: "Microsoft Yahei";
            }
        """
        self.setStyleSheet(self.style)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Fattysocks')
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowIcon(QIcon('res/icon.png'))

        background = QLabel('', self)
        background.resize(350, 250)
        background.setObjectName('WindowBg')
        background.setStyleSheet("#WindowBg{ background-image: url(res/main_page.png); }")

        mainWidget = QLabel('', self)
        mainWidget.resize(300, 140)
        mainWidget.setObjectName('MainWidget')
        mainWidget.setStyleSheet("#MainWidget{ background-color: white; border-radius: 0px; }")
        mainWidget.move(25, 85)

        closeBtn = QPushButton('x',self)
        closeBtn.resize(50, 40)
        closeBtn.clicked.connect(self.close)
        closeBtn.setObjectName('CloseButton')
        closeBtn.setStyleSheet('''
            #CloseButton{
                background-color: #008CBA;
                border-radius: 0px;
                color: white;
                padding: 5px 5px;
                text-align: center;
                font-size: 20px;
                font-family: "Microsoft Yahei";
            }
            #CloseButton:hover{
                background-color: #007BA9;
                border-radius: 0px;
                color: white;
                padding: 5px 5px;
                text-align: center;
                font-size: 20px;
                font-family: "Microsoft Yahei";
            }
        ''')
        closeBtn.move(325 - 10 - 60, 25)

        minBtn = QPushButton("-",self)
        minBtn.resize(50, 40)
        minBtn.clicked.connect(self.hide)
        minBtn.setObjectName('MinButton')
        minBtn.setStyleSheet('''
            #MinButton{
                background-color: #008CBA;
                border-radius: 0px;
                color: white;
                padding: 5px 5px;
                text-align: center;
                font-size: 20px;
            }
            #MinButton:hover{
                background-color: #007BA9;
                border-radius: 0px;
                color: white;
                padding: 5px 5px;
                text-align: center;
                font-size: 20px;
            }
        ''')
        minBtn.move(325 - 60 * 2, 25)

        main_wording = QLabel('Fattysocks', self)
        main_wording.setObjectName('MainWording')
        main_wording.setStyleSheet('#MainWording{font-family: "Microsoft Yahei"; color: white; font-size: 20px;}')
        main_wording.resize(150, 28)
        main_wording.move(60, 40)

        addr_wording = QLabel('服务器', self)
        addr_wording.setObjectName('AddrWording')
        addr_wording.setStyleSheet('#AddrWording{font-family: "Microsoft Yahei"; color: #666666; font-size: 12px;}')
        addr_wording.resize(60, 30)
        addr_wording.move(40, 100)

        self.addredit = QLineEdit('www.nxyexiong.xyz', self)
        self.addredit.resize(120, 30)
        self.addredit.move(90, 100)
        
        port_wording = QLabel('远程端口', self)
        port_wording.setObjectName('PortWording')
        port_wording.setStyleSheet('#PortWording{font-family: "Microsoft Yahei"; color: #666666; font-size: 12px;}')
        port_wording.resize(60, 30)
        port_wording.move(220, 100)

        self.portedit = QLineEdit('6666', self)
        self.portedit.resize(40, 30)
        self.portedit.move(275, 100)

        user_wording = QLabel('用户名', self)
        user_wording.setObjectName('UserWording')
        user_wording.setStyleSheet('#UserWording{font-family: "Microsoft Yahei"; color: #666666; font-size: 12px;}')
        user_wording.resize(60, 30)
        user_wording.move(40, 140)

        self.useredit = QLineEdit('18551828004', self)
        self.useredit.resize(120, 30)
        self.useredit.move(90, 140)

        lport_wording = QLabel('本地端口', self)
        lport_wording.setObjectName('LPortWording')
        lport_wording.setStyleSheet('#LPortWording{font-family: "Microsoft Yahei"; color: #666666; font-size: 12px;}')
        lport_wording.resize(60, 30)
        lport_wording.move(220, 140)

        self.lportedit = QLineEdit('1081', self)
        self.lportedit.resize(40, 30)
        self.lportedit.move(275, 140)

        self.connect_btn = QPushButton("代理: OFF", self)
        self.connect_btn.setStyleSheet(BUTTON_OFF_STYLE)
        self.connect_btn.clicked.connect(self.toggle_connect)
        self.connect_btn.resize(100, 30)
        self.connect_btn.move(30, 180)

        self.global_btn = QPushButton("全局: OFF", self)
        self.global_btn.setStyleSheet(BUTTON_OFF_STYLE)
        self.global_btn.clicked.connect(self.toggle_global)
        self.global_btn.resize(100, 30)
        self.global_btn.move(120, 180)

        self.boot_btn = QPushButton("自启动: OFF", self)
        self.boot_btn.setStyleSheet(BUTTON_OFF_STYLE)
        self.boot_btn.clicked.connect(self.toggle_boot)
        self.boot_btn.resize(115, 30)
        self.boot_btn.move(210, 180)

        self.set_tray()
        self.init_state()
        self.show()

    def init_state(self):
        # config
        config = load_config()
        if config:
            self.addredit.setText(config.get('addr'))
            self.portedit.setText(str(config.get('port')))
            self.lportedit.setText(str(config.get('lport')))
            self.useredit.setText(config.get('user'))

        # global
        key = 'ProxyEnable'
        path = r'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
        value = None
        try:
            reg = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, path, 0, access=winreg.KEY_ALL_ACCESS)
            value, ktype = winreg.QueryValueEx(reg, key)
            winreg.CloseKey(reg)
        except Exception:
            print('Reg ProxyEnable not exist!')
        if value:
            if value == 1:
                self.is_global = True
                self.global_btn.setText('全局: ON')
                self.global_btn.setStyleSheet(BUTTON_ON_STYLE)
            else:
                self.is_global = True
                self.global_btn.setText('全局: ON')
                self.global_btn.setStyleSheet(BUTTON_ON_STYLE)

        # boot
        key = 'Fattysocks'
        path = r'Software\Microsoft\Windows\CurrentVersion\Run'
        value = None
        try:
            reg = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, path, 0, access=winreg.KEY_ALL_ACCESS)
            value, ktype = winreg.QueryValueEx(reg, key)
            winreg.CloseKey(reg)
        except Exception:
            print('Reg Fattysocks not exist!')
            self.is_boot = False
            self.boot_btn.setText('自启动: OFF')
            self.boot_btn.setStyleSheet(BUTTON_OFF_STYLE)
        if value:
            if value == sys.argv[0]:
                self.is_boot = True
                self.boot_btn.setText('自启动: ON')
                self.boot_btn.setStyleSheet(BUTTON_ON_STYLE)
            else:
                self.is_boot = False
                self.boot_btn.setText('自启动: OFF')
                self.boot_btn.setStyleSheet(BUTTON_OFF_STYLE)

        self.tray.setToolTip(self.get_tooltip())

    def set_tray(self):
        self.tray = QSystemTrayIcon(QIcon('res/icon.png'), self)
        self.tray.activated.connect(self.tray_event)
        self.tray_menu = QMenu(QApplication.desktop())
        self.RestoreAction = QAction('打开', self, triggered=self.show)
        self.QuitAction = QAction('退出', self, triggered=self.close)
        self.tray_menu.addAction(self.RestoreAction)
        self.tray_menu.addAction(self.QuitAction)
        self.tray.setContextMenu(self.tray_menu)
        self.tray.setToolTip(self.get_tooltip())
        self.tray.show()

    def get_tooltip(self):
        tooltip = 'Fattysocks\n'
        tooltip += self.addredit.text() + ':' + self.portedit.text() + '\n'
        tooltip += '127.0.0.1:' + self.lportedit.text() + '\n'
        if self.client:
            tooltip += 'Proxy: On\n'
        else:
            tooltip += 'Proxy: Off\n'
        if self.is_global:
            tooltip += 'Global: On\n'
        else:
            tooltip += 'Global: Off\n'
        return tooltip

    def tray_event(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()

    def closeEvent(self, event):
        self.tray.hide()

    def mousePressEvent(self, event):
        if event.button()==Qt.LeftButton:
            self.m_drag=True
            self.m_DragPosition=event.globalPos()-self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_drag:
            if not self.m_DragPosition:
                return
            self.move(QMouseEvent.globalPos()-self.m_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_drag=False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def toggle_connect(self):
        if self.client:
            self.client.stop()
            self.client = None
            self.connect_btn.setText('代理: OFF')
            self.connect_btn.setStyleSheet(BUTTON_OFF_STYLE)
        else:
            addr = self.addredit.text()
            port = int(self.portedit.text())
            lport = int(self.lportedit.text())
            user = self.useredit.text()

            # save config
            config = {}
            config['addr'] = addr
            config['port'] = port
            config['lport'] = lport
            config['user'] = user
            save_config(config)

            self.client = Client(lport, addr, port, user)
            self.client.run()
            self.connect_btn.setText('代理: ON')
            self.connect_btn.setStyleSheet(BUTTON_ON_STYLE)
        self.tray.setToolTip(self.get_tooltip())

    def toggle_global(self):
        if not self.is_global:
            key = 'ProxyEnable'
            path = r'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
            value = 1
            try:
                reg = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(reg, key, 0, winreg.REG_DWORD, value)
                winreg.CloseKey(reg)
            except Exception:
                print('Reg set ProxyEnable failed!')

            key = 'ProxyServer'
            path = r'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
            value = 'socks5://127.0.0.1:' + self.lportedit.text()
            try:
                reg = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(reg, key, 0, winreg.REG_SZ, value)
                winreg.CloseKey(reg)
            except Exception:
                print('Reg set ProxyServer failed!')
            
            self.is_global = True
            self.global_btn.setText('全局: ON')
            self.global_btn.setStyleSheet(BUTTON_ON_STYLE)
        else:
            key = 'ProxyEnable'
            path = r'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
            value = 0
            try:
                reg = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(reg, key, 0, winreg.REG_DWORD, value)
                winreg.CloseKey(reg)
            except Exception:
                print('Reg set ProxyEnable failed!')
            
            self.is_global = False
            self.global_btn.setText('全局: OFF')
            self.global_btn.setStyleSheet(BUTTON_OFF_STYLE)
        self.tray.setToolTip(self.get_tooltip())

    def toggle_boot(self):
        if not self.is_boot:
            key = 'Fattysocks'
            path = r'Software\Microsoft\Windows\CurrentVersion\Run'
            value = sys.argv[0]
            try:
                reg = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(reg, key, 0, winreg.REG_SZ, value)
                winreg.CloseKey(reg)
            except Exception:
                print('Reg set Fattysocks failed!')

            self.is_boot = True
            self.boot_btn.setText('自启动: ON')
            self.boot_btn.setStyleSheet(BUTTON_ON_STYLE)
        else:
            key = 'Fattysocks'
            path = r'Software\Microsoft\Windows\CurrentVersion\Run'
            try:
                reg = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
                winreg.DeleteValue(reg, key)
                winreg.CloseKey(reg)
            except Exception:
                print('Reg del ProxyEnable failed!')

            self.is_boot = False
            self.boot_btn.setText('自启动: OFF')
            self.boot_btn.setStyleSheet(BUTTON_OFF_STYLE)


MAIN_WINDOW = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MAIN_WINDOW = FrontWindow()
    sys.exit(app.exec())
