import requests, threading
import json
import logging, time
import hmac, hashlib
from urllib import parse

from utils.SecuritySm import get_d_id
from utils.config import get_config, get_secret

config = get_config()
secret = get_secret()

app_code = '4ca99fa6b56cc2ba'

http_local = threading.local()
header = {
    'cred': '',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-A5560 Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/101.0.4951.61 Safari/537.36; SKLand/1.52.1',
    'Accept-Encoding': 'gzip',
    'Connection': 'close',
    'X-Requested-With': 'com.hypergryph.skland'
}
header_login = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-A5560 Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/101.0.4951.61 Safari/537.36; SKLand/1.52.1',
    'Accept-Encoding': 'gzip',
    'Connection': 'close',
    'dId': get_d_id(),
    'X-Requested-With': 'com.hypergryph.skland'
}

# 签名请求头一定要这个顺序，否则失败
# timestamp是必填的,其它三个随便填,不要为none即可
header_for_sign = {
    'platform': '3',
    'timestamp': '',
    'dId': header_login['dId'],
    'vName': '1.0.0'
}

# 签到url
sign_url_mapping = {
    'arknights': 'https://zonai.skland.com/api/v1/game/attendance',
    'endfield': 'https://zonai.skland.com/web/v1/game/endfield/attendance'
}

# 绑定的角色url
binding_url = "https://zonai.skland.com/api/v1/game/player/binding"
# 验证码url
login_code_url = "https://as.hypergryph.com/general/v1/send_phone_code"
# 验证码登录
token_phone_code_url = "https://as.hypergryph.com/user/auth/v2/token_by_phone_code"
# 密码登录
token_password_url = "https://as.hypergryph.com/user/auth/v1/token_by_phone_password"
# 使用token获得认证代码
grant_code_url = "https://as.hypergryph.com/user/oauth2/v2/grant"
# 使用认证代码获得cred
cred_code_url = "https://zonai.skland.com/web/v1/user/auth/generate_cred_by_code"
# refresh
refresh_token_url = "https://zonai.skland.com/web/v1/auth/refresh"

def generate_signature(path, body_or_query):
    """
    获得签名头
    接口地址+方法为Get请求？用query否则用body+时间戳+ 请求头的四个重要参数（dId，platform，timestamp，vName）.toJSON()
    将此字符串做HMAC加密，算法为SHA-256，密钥token为请求cred接口会返回的一个token值
    再将加密后的字符串做MD5即得到sign
    :param path: 请求路径（不包括网址）
    :param body_or_query: 如果是GET，则是它的query。POST则为它的body
    :return: 计算完毕的sign
    """
    # 总是说请勿修改设备时间，怕不是yj你的服务器有问题吧，所以这里特地-2
    t = str(int(time.time()) - 2)
    token = http_local.token.encode('utf-8')
    header_ca = json.loads(json.dumps(header_for_sign))
    header_ca['timestamp'] = t
    header_ca_str = json.dumps(header_ca, separators=(',', ':'))
    s = path + body_or_query + t + header_ca_str
    hex_s = hmac.new(token, s.encode('utf-8'), hashlib.sha256).hexdigest()
    md5 = hashlib.md5(hex_s.encode('utf-8')).hexdigest().encode('utf-8').decode('utf-8')
    logging.info(f'算出签名: {md5}')
    return md5, header_ca


def get_sign_header(url: str, method, body, h):
    p = parse.urlparse(url)
    if method.lower() == 'get':
        h['sign'], header_ca = generate_signature(p.path, p.query)
    else:
        h['sign'], header_ca = generate_signature(p.path, json.dumps(body) if body is not None else '')
    for i in header_ca:
        h[i] = header_ca[i]
    return h

def get_token_by_password(user):
    username = user["username"]
    password = user["password"]
    resp = requests.post(token_password_url, json={"phone": username, "password": password}, headers=header_login).json()
    return resp['data']['token']


def get_token_by_code(user):
    username = user["username"]
    resp = requests.post(login_code_url, json={'phone': username, 'type': 2}, headers=header_login).json()
    if resp.get("status") != 0:
        raise Exception(f"发送手机验证码出现错误: {resp['msg']}")
    code = input("请输入手机验证码：")
    resp = requests.post(token_phone_code_url, json={"phone": username, "code": code}, headers=header_login).json()
    if resp.get('status') != 0:
        raise Exception(f'获得token失败: {resp["msg"]}')
    return resp['data']['token']

def get_token_by_login_desp(desp):
    content = json.loads(desp)
    return content["data"]["content"]

def get_grant_code(token):
    response = requests.post(grant_code_url, json={
        'appCode': app_code,
        'token': token,
        'type': 0
    }, headers=header_login)
    resp = response.json()
    if response.status_code != 200:
        raise Exception(f'获得认证代码失败：{resp}')
    if resp.get('status') != 0:
        raise Exception(f'获得认证代码失败：{resp["msg"]}')
    return resp['data']['code']


def get_cred(grant):
    resp = requests.post(cred_code_url, json={
        'code': grant,
        'kind': 1
    }, headers=header_login).json()
    if resp['code'] != 0:
        raise Exception(f'获得cred失败：{resp["message"]}')
    return resp['data']

def get_cred_by_token(token):
    grant_code = get_grant_code(token)
    return get_cred(grant_code)

def refresh_token():
    headers = get_sign_header(refresh_token_url, 'get', None, http_local.header)
    resp = requests.get(refresh_token_url, headers=headers).json()
    if resp.get('code') != 0:
        raise Exception(f'刷新token失败:{resp["message"]}')
    http_local.token = resp['data']['token']

def get_binding_list():
    binding_list = []
    resp = requests.get(binding_url, headers=get_sign_header(binding_url, 'get', None, http_local.header)).json()

    if resp['code'] != 0:
        logging.error(f"请求角色列表出现问题：{resp['message']}")
        if resp.get('message') == '用户未登录':
            logging.error(f'用户登录可能失效了，请重新运行此程序！')
            # os.remove(token_save_name)
            return []
    for i in resp['data']['list']:
        # 也许有些游戏没有签到功能？
        if i.get('appCode') not in ('arknights', 'endfield'):
            continue
        for j in i.get('bindingList'):
            j['appCode'] = i['appCode']
        binding_list.extend(i['bindingList'])
    return binding_list


def sign_arknights(data: dict):
    # 返回是否成功，消息
    body = {
        'gameId': data.get('gameId'),
        'uid': data.get('uid')
    }
    url = sign_url_mapping['arknights']
    headers = get_sign_header(url, 'post', body, http_local.header)
    resp = requests.post(url, headers=headers, json=body).json()
    game_name = data.get('gameName')
    channel = data.get("channelName")
    nickname = data.get('nickName') or ''
    if resp.get('code') != 0:
        return [
            f'[{game_name}]角色{nickname}({channel})签到失败了！原因：{resp["message"]}']
    result = ''
    awards = resp['data']['awards']
    for j in awards:
        res = j['resource']
        result += f'{res["name"]}×{j.get("count") or 1}'
    return [f'[{game_name}]角色{nickname}({channel})签到成功，获得了{result}']


def sign_endfield(data: dict):
    roles: list[dict] = data.get('roles')
    game_name = data.get('gameName')
    channel = data.get("channelName")
    result = []
    for role in roles:
        nickname = role.get('nickname') or ''
        url = sign_url_mapping['endfield']
        headers = get_sign_header(url, 'post', None, http_local.header)
        headers.update({
            'Content-Type': 'application/json',
            # FIXME b服不知道是不是这样
            # gameid_roleid_serverid
            'sk-game-role': f'3_{role["roleId"]}_{role["serverId"]}',
            'referer': 'https://game.skland.com/',
            'origin': 'https://game.skland.com/'
        })
        j = requests.post(url, headers=headers).json()
        if j['code'] != 0:
            result.append(f'[{game_name}]角色{nickname}({channel})签到失败了！原因:{j["message"]}')
        else:
            awards_result = []
            result_data: dict = j['data']
            result_info_map: dict = result_data['resourceInfoMap']
            for a in result_data['awardIds']:
                award_id = a['id']
                awards = result_info_map[award_id]
                award_name = awards['name']
                award_count = awards['count']
                awards_result.append(f'{award_name}×{award_count}')

            result.append(f'[{game_name}]角色{nickname}({channel})签到成功，获得了:{",".join(awards_result)}')
    return result

def do_sign(cred_resp):
    http_local.token = cred_resp['token']
    http_local.header = header.copy()
    http_local.header['cred'] = cred_resp['cred']
    roles = get_binding_list()
    success = True
    logs_out = []  # 新增：用于 Server酱³ 的汇总文本
    for role in roles:
        app_code = role['appCode']
        msg = None
        if app_code == 'arknights':
            msg = sign_arknights(role)
        elif app_code == 'endfield':
            msg = sign_endfield(role)
        logging.info(msg)

        logs_out.extend(msg)

    return success, logs_out