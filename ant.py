import requests
import json
import time
import logging
from datetime import datetime, date
from rich.logging import RichHandler
from rich.console import Console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",  # Add time information
    datefmt="%Y-%m-%d %H:%M:%S",  # The format of time
    handlers=[RichHandler(rich_tracebacks=True)]
)
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console = Console()

class Qianggou:
    def __init__(self, start_time_str, thread_per_ck, cks):
        self.start_time = datetime.strptime(start_time_str, '%H:%M:%S.%f').time()
        self.thread_per_ck = thread_per_ck
        self.cks = cks
        self.results = {}
        self.logger = logging.getLogger('rich')

    def get_network_time(self):
        url = 'http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp'
        response = requests.get(url)
        result = response.json()
        timestamp = int(result['data']['t']) / 1000.0
        return datetime.fromtimestamp(timestamp).time()

    def print_remaining_time(self):
        while True:
            net_time = self.get_network_time()
            if net_time >= self.start_time:
                break
            remaining_seconds = (datetime.combine(date.today(), self.start_time) - datetime.combine(date.today(), net_time)).total_seconds()
            logging.info(f"剩余时间： {remaining_seconds} 秒")
            time.sleep(0.5)

    def run(self):
        self.print_remaining_time()
        for ck, ck_value in self.cks.items():
            for _ in range(self.thread_per_ck):
                self.fetch(ck, ck_value)

    def fetch(self, ck, ck_value):
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.42(0x18002a2a) NetType/WIFI Language/zh_CN",
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Accept": "v=1.0",
            "Content-Length": "64",
            "Qm-From": "wechat",
            'Qm-From-Type': 'catering',
            "Referer": "https://servicewechat.com/wx4080846d0cec2fd5/295/page-frame.html",
            "Qm-User-Token": ck_value
        }
        data = {"activityId": "914195788669427712", "appid": "wx4080846d0cec2fd5"}
        data = json.dumps(data)
        logging.info(data)

        url = 'https://webapi.qmai.cn/web/cmk-center/receive/takePartInReceive'
        while True:
            response = requests.post(url, headers=headers, data=data)
            response_text = response.text
            response_text = json.loads(response_text)
            logging.info(response_text)
            response_text = response_text['message']
            push_mesg = f"remark==>{ck}, response={response_text}"
            logging.info(f"remark==>{ck}, response={response_text}")
            
            if response.status_code == 200:
                if '不在' in response_text or '参数不符合规范' in response_text :
                    self.results[ck] = push_mesg
                    break
            else:
                logging.error(f'CK={ck}, 请求失败，响应状态码为{response.status_code}')
            time.sleep(0.002)

    def push(self, content):
        # 添加推送逻辑
        pass

if __name__ == '__main__':
    # 抢券开始时间
    start_time_str = '10:59:00.000'

    # 每个CK的并发数量
    thread_per_ck = 1

    # ck字典，填充你自己的ck值
    cks = {
        '备注': "token",
    }
    logging.info(f"start_time_str={start_time_str}, thread_per_ck={thread_per_ck}, cks={cks}")
    qianggou = Qianggou(start_time_str, thread_per_ck, cks)
    qianggou.run()
