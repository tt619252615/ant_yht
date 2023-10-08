import requests
import aiohttp
s = requests.session()
from json import dumps as jsonDumps
 
class QL:
    def __init__(self, address: str, id: str, secret: str) -> None:
        """
        初始化
        """
        self.address = address
        self.id = id
        self.secret = secret
        self.valid = True
        self.login()
 
    def log(self, content: str) -> None:
        """
        日志
        """
        print(content)
 
    def login(self) -> None:
        """
        登录
        """
        url = f"{self.address}/open/auth/token?client_id={self.id}&client_secret={self.secret}"
        try:
            rjson = requests.get(url).json()
            if(rjson['code'] == 200):
                self.auth = f"{rjson['data']['token_type']} {rjson['data']['token']}"
            else:
                self.log(f"登录失败：{rjson['message']}")
        except Exception as e:
            self.valid = False
            self.log(f"登录失败：{str(e)}")
 
    def getEnvs(self) -> list:
        """
        获取环境变量
        """
        url = f"{self.address}/open/envs?searchValue="
        headers = {"Authorization": self.auth}
        try:
            rjson = requests.get(url, headers=headers).json()
            if(rjson['code'] == 200):
                return rjson['data']
            else:
                self.log(f"获取环境变量失败：{rjson['message']}")
        except Exception as e:
            self.log(f"获取环境变量失败：{str(e)}")
 
    def deleteEnvs(self, ids: list) -> bool:
        """
        删除环境变量
        """
        url = f"{self.address}/open/envs"
        headers = {"Authorization": self.auth,"content-type": "application/json"}
        try:
            rjson = requests.delete(url, headers=headers, data=jsonDumps(ids)).json()
            print(rjson)
            if(rjson['code'] == 200):
                self.log(f"删除环境变量成功：{len(ids)}")
                return True
            else:
                self.log(f"删除环境变量失败：{rjson['message']}")
                self.log(f"删除环境变量失败：{rjson}")
                return False
        except Exception as e:
            self.log(f"删除环境变量失败：{str(e)}")
            return False
 
    def addEnvs(self, envs: list) -> bool:
        """
        新建环境变量
        """
        url = f"{self.address}/open/envs"
        headers = {"Authorization": self.auth,"content-type": "application/json"}
        try:
            rjson = requests.post(url, headers=headers, data=jsonDumps(envs)).json()
            if(rjson['code'] == 200):
                self.log(f"新建环境变量成功：{len(envs)}")
                return True
            else:
                self.log(f"新建环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.log(f"新建环境变量失败：{str(e)}")
            return False
 
    def updateEnv(self, env: dict) -> bool:
        """
        更新环境变量
        """
        url = f"{self.address}/open/envs"
        headers = {"Authorization": self.auth,"content-type": "application/json"}
        try:
            rjson = requests.put(url, headers=headers, data=jsonDumps(env)).json()
            if(rjson['code'] == 200):
                self.log(f"更新环境变量成功")
                return True
            else:
                self.log(f"更新环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.log(f"更新环境变量失败：{str(e)}")
            return False
    
    
    def deleteBlacklistedCookies(self) -> None:
        """ 
        Delete cookies that are blacklisted.
        """
        envs = self.getEnvs()
        to_delete_ids = []

        for env in envs:
            if env.get('name') == 'mt_cookie':
                cookie = env.get('value')
                if not self.getremark(cookie):
                    to_delete_ids.append(env.get('id'))

        if to_delete_ids:
            self.deleteEnvs(to_delete_ids)
            self.log(f"Deleted {len(to_delete_ids)} blacklisted cookies.")
        else:
            self.log("No blacklisted cookies found.")

    def deleteBlacklistedCookies(self) -> None:
        """ 
        Delete cookies that are blacklisted.
        """
        envs = self.getEnvs()
        to_delete = []

        for env in envs:
            if env.get('name') == 'mt_cookie':
                cookie = env.get('value')
                if not self.getremark(cookie):
                    to_delete.append({"name": "mt_cookie", "value": cookie})

        if to_delete:
            self.deleteEnvs(to_delete)
            self.log(f"Deleted {len(to_delete)} blacklisted cookies.")
        else:
            self.log("No blacklisted cookies found.")

    def is_blacklisted(self, response_text: str) -> bool:
        """ 
        Check if the response contains any of the blacklisted flags.
        """
        blacklist_flags = ["e牧尘2101", "1875441", "655479980"]
        return any(flag in response_text for flag in blacklist_flags)

    def getremark(self,cookie):
        url = 'https://open.meituan.com/user/v1/info/auditting?fields=auditAvatarUrl%2CauditUsername'
        headers = {
            "dj-token": "",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.38(0x18002629) NetType/WIFI Language/zh_CN",
            "Content-Type": "application/json",
            "X-Requested-With": "com.sankuai.meituan",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://market.waimai.meituan.com",
            "Cookie": cookie
        }
        response = s.get(url=url, headers=headers)
        response_text = response.text
        if 'user' not in response_text:
            self.log('cookie 失效')
            return None
        elif self.is_blacklisted(response_text):
            self.log('响应包含拉黑用户,踢出程序')
            self.deleteEnvs([{"name": "mt_cookie", "value": cookie}])
            return None
        else:
            resp = response.json()
            self.log(f'备注：{resp}')
            return resp['user']['username']
    def deleteAllMtCookies(self) -> None:
        """ 
        Delete all cookies named 'mt_cookie'.
        """
        envs = self.getEnvs()
        to_delete_ids = []

        for env in envs:
            if env.get('name') == 'mt_cookie':
                to_delete_ids.append(env.get('id'))

        if to_delete_ids:
            self.deleteEnvs(to_delete_ids)
            self.log(f"Deleted {len(to_delete_ids)} 'mt_cookie' entries.")
        else:
            self.log("No 'mt_cookie' entries found.")
    def getreamrk(self):
        envs = self.getEnvs()
        remark ={}
    def push(content):
        PUSH_URL = 'http://www.pushplus.plus/send'
        push_key = push_key,#push_key填自己的 
        topic = '3'
        template = 'json'
        print('开始推送')
        if not push_key:
            print.info('未设置PUSH_KEY，推送失败')
            return
        # content = '红包提醒,ck已经全部删除,可以再次提交了'
        params = {
            'text': '红包提醒',
            'content': content,
            "template": template,
            'token': push_key,
            "topic": topic,
        }
        headers = {'Content-Type': 'application/json'}
        response= requests.post(PUSH_URL, params=params, headers=headers)
        response_text = response.text
        print(response_text)
        if response.status_code == 200 :
            if 'success' in response_text:
                print('推送成功')
            else:
                print('推送失败', response_text)


 
 