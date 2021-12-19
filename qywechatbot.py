from requests import post
from base64 import b64encode
from hashlib import md5
import os
from json import load


class BotsendMsg:
    def __init__(self):
        configs = load(open("configure/config.json", 'r'))
        self.send_url = configs['qywechat']['send_url']
        self.id_url = configs['qywechat']['id_url']

    # 文本类型消息
    def send_msg_txt(self, content):
        send_url = self.send_url

        headers = {"Content-Type": "text/plain"}
        send_data = {
            "msgtype": "text",  # 消息类型，此时固定为text
            "text": {
                "content": content  # 文本内容，最长不超过2048个字节，必须是utf8编码
            }
        }

        return post(url=send_url, headers=headers, json=send_data)

    # mk文本类型消息
    def send_msg_mk(self, mkcontent):
        send_url = self.send_url
        headers = {"Content-Type": "text/plain"}
        send_data = {
            "msgtype": "markdown",
            "markdown": {
                "content": mkcontent
            }
        }

        return post(url=send_url, headers=headers, json=send_data)

    # 发送图片
    def send_msg_image(self, image):
        with open(image, 'rb') as file:  # 转换图片成base64格式
            data = file.read()
            encodestr = b64encode(data)
            image_data = str(encodestr, 'utf-8')

        with open(image, 'rb') as file:  # 图片的MD5值
            md = md5()
            md.update(file.read())
            image_md5 = md.hexdigest()

        url = self.send_url  # 填上机器人Webhook地址
        headers = {"Content-Type": "application/json"}
        data = {
            "msgtype": "image",
            "image": {
                "base64": image_data,
                "md5": image_md5
            }
        }

        return post(url, headers=headers, json=data)

    def send_msg_file(self, file):
        id_url = self.id_url  # 上传文件接口地址
        data = {'file': open(file, 'rb')}  # post jason
        response = post(url=id_url, files=data)  # post 请求上传文件
        json_res = response.json()  # 返回转为json
        media_id = json_res['media_id']  # 提取返回ID
        send_url = self.send_url  # 发送消息接口地址
        data = {"msgtype": "file", "file": {"media_id": media_id}}  # post json
        return post(url=send_url, json=data)  # post请求消息

    # 消息通知发送函数
    def messagenotification(self, filedir, Dataoperation):
        """
        :param filedir:遍历的发送消息文件的文件夹
        :param Dataoperation: 文件操作类
        :return:
        """
        # 检查消息文档目录是否为空
        while True:
            if os.listdir('Msg'):
                break
            pass
        # 遍历消息文档目录获取消息文件名
        filelist = os.listdir(filedir)
        print(filelist)
        for filename in filelist:
            content = Dataoperation.readtxt('Msg/' + str(filename))
            print(content)
            while self.send_msg_txt(content) is False:
                print("发送消息出错")
