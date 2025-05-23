import sys
import time
import requests
import random
import re
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from interface.ui_main_window import Ui_MainWindow  # 这是通过 Qt Designer 生成的 UI 类

def ptqrtoken(value):
    e = 0
    for i in range(len(value)):
        e = e + (e << 5) + ord(value[i])
    return str(2147483647 & e)

def gen_bkn(value):
    t = 5381
    for n in range(len(value)):
        t += (t << 5) + ord(value[n])
    return str(t & 2147483647)

def calculate_g_tk(p_skey):
    hash = 5381
    for char in p_skey:
        hash += (hash << 5) + ord(char)
    return hash & 0x7fffffff

def truncate_string(s):
    # 创建一个列表来存储反向查找结果
    result = []
    # 从右侧开始迭代字符串
    for char in reversed(s):
        # 如果字符是数字且不是'0'，保存在结果列表中
        if char.isdigit() and char != '0':
            result.append(char)
        else:
            # 遇到'0'或非数字字符就结束
            break
    # 因为是逆序迭代，结果列表需要反转并连接到一个字符串
    return ''.join(reversed(result))

class QRCodeLoginApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 初始化网络会话
        self.session = requests.Session()
        
        # 获取二维码并显示
        self.get_qr_code()
        self.call_xlogin()
        
        # 设置定时器来轮询二维码状态
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_qr_status)
        self.timer.start(2000)  # 每2秒检查一次

    def get_qr_code(self):
        # 生成随机数
        random_number = random.random()
        
        # 获取二维码图片

        # 请求参数
        # params = {
        #     'appid': '715030901',
        #     'e': '2',
        #     'l': 'M',
        #     's': '3',
        #     'd': '72',
        #     'v': '4',
        #     't': str(random_number),
        #     'daid': '73',
        #     'pt_3rd_aid': '0',
        #     'u1': 'https://qun.qq.com/',
        # }
        params = {
            'appid': '549000912',
            'e': '2',
            'l': 'M',
            's': '3',
            'd': '72',
            'v': '4',
            't': str(random_number),
            'daid': '5',
            'pt_3rd_aid': '0',
            'u1': 'https://qzs.qzone.qq.com//',
        }
        url = f"https://ssl.ptlogin2.qq.com/ptqrshow"
        response = self.session.get(url, params=params)
        
        # 将二维码图片显示在 QLabel 中
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        self.qrCodeLabel.setPixmap(pixmap)

    def call_xlogin(self):
        # 请求参数
        # params = {
        #     'pt_disable_pwd': '1',
        #     'appid': '715030901',
        #     'hide_close_icon': '1',
        #     'daid': '73',
        #     'pt_no_auth': '1',
        #     's_url': 'https://qun.qq.com/'
        # }
        params = {
            # 'pt_disable_pwd': '1',
            'appid': '549000912',
            # 'hide_close_icon': '1',
            'daid': '5',
            'pt_no_auth': '1',
            's_url': 'https://qzs.qzone.qq.com/'
        }

        # URL
        url = "https://xui.ptlogin2.qq.com/cgi-bin/xlogin"

        # 发起 GET 请求
        response = self.session.get(url, params=params)

        # 返回响应内容
        # print(response.headers)
        return response.content

    def check_qr_status(self):
        # 计算 ptqrtoken
        # print(self.session.cookies)
        qrsig = self.session.cookies.get('qrsig')
        token = ptqrtoken(qrsig)
        
        # 构建请求 URL
        # params = {
        #     'u1': 'https://qun.qq.com/',
        #     'ptqrtoken': token,
        #     'ptredirect': '1',
        #     'h': '1',
        #     't': '1',
        #     'g': '1',
        #     'from_ui': '1',
        #     'ptlang': '2052',
        #     'action': f'0-0-{int(time.time() * 1000)}',
        #     'js_ver': '25051315',
        #     'js_type': '1',
        #     'login_sig': self.session.cookies.get('pt_login_sig'),
        #     'pt_uistyle': '40',
        #     'aid': '715030901',
        #     'daid': '73',
        #     'o1vId': '3ff19b57e1405d1b6e71d15bad29f07b',
        #     'pt_js_version': '9fce2a54',
        # }
        params = {
            'u1': 'https://qzs.qzone.qq.com/',
            'ptqrtoken': token,
            'ptredirect': '1',
            'h': '1',
            't': '1',
            'g': '1',
            'from_ui': '1',
            'ptlang': '2052',
            'action': f'0-0-{int(time.time() * 1000)}',
            'js_ver': '25051315',
            'js_type': '1',
            'login_sig': self.session.cookies.get('pt_login_sig'),
            'pt_uistyle': '40',
            'aid': '549000912',
            'daid': '5',
            'o1vId': '3ff19b57e1405d1b6e71d15bad29f07b',
            'pt_js_version': '9fce2a54',
        }
        url = "https://xui.ptlogin2.qq.com/ssl/ptqrlogin"
        
        # print(params)
        response = self.session.get(url, params=params)
        print(response.status_code)
        status = response.text.split(',')[0].strip("ptuiCB('")  # 提取状态码
        
        if status == '0':
            # 登录成功，获取跳转链接
            redirect_url = response.text.split(',')[2].strip("'")
            self.session.get(redirect_url)
            self.timer.stop()  # 停止轮询
            # 在这里可以添加进一步的逻辑，例如关闭窗口或显示登录成功信息
            print(self.fetch_album_list())
            
    def verify_login_success(self):
        # URL
        url = "https://qun.qq.com/cgi-bin/qun_mgr/search_group_members"

        # 请求数据
        bkn = gen_bkn(self.session.cookies.get('skey'))
        params = {
            'bkn': bkn,
            'ts': f'{int(time.time() * 1000)}'
        }
        data = {
            'st': '0',
            'end': '9',
            'sort': '1',
            'gc': '226739751',
            'g': '0',
            'bkn': bkn
        }

        # 发起 POST 请求
        print(self.session.cookies)
        response = self.session.post(url, params=params, data=data)

        # 返回响应内容
        return response.json()
    
    def fetch_album_list(self):
        # print(self.session.cookies)

        script_resp = self.session.get(f'https://h5.qzone.qq.com/groupphoto/index?inqq=3&groupId=185859827&type=102&uri=share&_t_{str(random.random())}')
        script = script_resp.text
        # print(script)
        for line in script.split('\n'):
            if line.strip().startswith('window.g_qzonetoken = window.shine0callback ='):
                match = re.search(r'return\s+"(.*?)"', line)
                qzonetoken = match.group(1)
                break

        g_tk = calculate_g_tk(self.session.cookies.get('p_skey'))
        uin = truncate_string(self.session.cookies.get('uin'))
        
        # 请求参数
        params = {
            'g_tk': g_tk,
            'qzonetoken': qzonetoken,
            'callback': 'shine2_Callback',
            't': str(random.randint(1_0000_0000, 9_9999_9999)),  # 随机数
            'qunId': '185859827',
            'uin': uin,
            'start': '0',
            'num': '36',
            'getMemberRole': '1',
            'format': 'jsonp',
            'platform': 'qzone',
            'inCharset': 'utf-8',
            'outCharset': 'utf-8',
            'source': 'qzone',
            'cmd': 'qunGetAlbumList',
            'attach_info': '',
            'callbackFun': 'shine2',
            '_': str(int(time.time() * 1000))  # 使用当前时间戳
        }

        url = 'https://h5.qzone.qq.com/proxy/domain/u.photo.qzone.qq.com/cgi-bin/upp/qun_list_album_v2'
        response = self.session.get(url, params=params)
        return response.text  # 在实际应用中可以对返回的内容进一步处理

def main():
    app = QApplication(sys.argv)
    window = QRCodeLoginApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    # print(ptqrtoken('6e5147ff28a55e8106d5b0031f301a37fd1b3349de8bd09f2470a9fba5a0c4495b7b8a5f7985d19e39e59ca000bf9187be8f6751f910b314'))