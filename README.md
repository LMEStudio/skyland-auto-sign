# skyland-auto-sign

基于 Python 的明日方舟森空岛一键签到脚本  
A fork from [gitee.com/FancyCabbage/skyland-auto-sign](https://gitee.com/FancyCabbage/skyland-auto-sign), which changed the secret structure for better management for automation.  

## Deployment

* Docker
* GitHub Actions
* Local

## Usage

1. Install dependencies of `requirements.txt`.  
2. Run at least once `configure.py` to generate `secret.json`.  
3. Run `main.py` to execute locally.  
4. (Additionally) To run on GitHub Actions, you need to fork the repository and allow the repository to run `Actions` in `Settings`, and create a environment `sign` which contains a environment variable `secret` including `secret.json` file. If you use cloud service for automatically runnings, each time you modify configuration or secret, you need to update the repository.  
5. (Additionally) To configure a push service, you need to run `configure.py` again and follow the instructions. If you use cloud service for automatically runnings, you need to update the repository.  
6. (Additionally) To modify default settings, you need to run `configure.py` again and generate new `config.py`. If you use cloud service for automatically runnings, you need to update the repository.  
7. Supported push service providers:  

    |Providers|Links|Names in `secret.json`|Required Parameters|
    |------|------|------|------|
    |Server Chan Turbo|[https://sct.ftqq.com/](https://sct.ftqq.com/)|`server_chan_turbo`|`provider`, `token`|
    |Server Chan Cubed|[https://sc3.ft07.com/](https://sc3.ft07.com/)|`server_chan_cubed`|`provider`, `token`, `uid`|
    |pushplus|[https://www.pushplus.plus/](https://www.pushplus.plus/)|`pushplus`|`provider`, `topic` (opt.), `token`|
    |Qmsg|[https://qmsg.zendee.cn/](https://qmsg.zendee.cn/)|`qmsg`|`provider`, `type`, `token`, `qq` (opt.), `bot` (opt.)|

8. Supported `config.json` parameters:

    |Parameters|Description|Necessity|Default|
    |------|------|------|------|
    |`messagePush`|Enable message push function|Required|`{"enabled": true}`|
    |`useProxy`|Enable proxy and configure proxy addresses|Dispensable|`{"enabled": false,"addr": ""}`|
    |`exitWhenFail`|Exit when encountering failure|Required|`false`|
    |`renewPeriod`|Control the renew period of each token (seconds)|Required|`2592000` (30 days)|

9. A possible `secret.json` structure:

    ```json
    {
        "pushProvider": [
            {
                "provider": "server_chan_turbo",
                "token": ""
            },
            {
                "provider": "server_chan_cubed",
                "token": "",
                "uid": ""
            },
            {
                "provider": "pushplus",
                "topic": "",
                "token": ""
            },
            {
                "provider": "qmsg",
                "type": "group",
                "token": "",
                "qq": "",
                "bot": ""
            }
        ],
        "auth": [
            {
                "username": "",
                "password": "",
                "token": "",
                "needRenewBefore": ""
            }
        ],
        "tokens": []
    }
    ```

10. Default `config.json` structure

    ```json
    {
        "messagePush": {
            "enabled": true
        },
        "useProxy": {
            "enabled": false,
            "addr": ""
        },
        "exitWhenFail": false,
        "renewPeriod": 2592000
    }
    ```

## sign-header

新版本森空岛添加了参数验证，有两个方法可以绕过，推荐第一种方法

1.森空岛签名请求头算法：

接口地址（不包括网址） + 如果是GET则使用网址问号后面的参数。如果是POST则使用body的json的字符串 + 时间戳 +
请求头的四个重要参数(`platform`,`timestamp`,`dId`和`vName`).toJSON()

将此字符串做HMAC加密，算法为SHA-256，密钥为请求cred接口会返回的一个token

再将加密后的字符串做MD5即得到签名

例子：

```text
    
    拼接的字符串：
    /api/v1/game/player/binding1695184599{"platform":"","timestamp":"1695184599","dId":"","vName":""}
    将其做hmac-sha256
    6b0516d1325dea1207e03f6840cd0c15ef2f55959c3d0ed2f18d99102a9cc7f5
    再做md5
    92229bf3c18c476e77bcd70c2bd997d3
    最后就是sign的头了
    
```

注意：

请求头四个值`platform`,`timestamp`,`dId`和`vName`必传，然后注意一下字符串顺序，四个值必须按照这样的顺序拼接

其中`platform`,`dId`和`vName`里面的值随便填

`timestamp`为时间戳，以秒为单位
不过`timestamp`因为精度问题容易造成服务器响应`请勿修改设备时间`，此时把这个时间戳稍微减少几秒就行

2.使用旧版本森空岛请求头，防止验参

```text
'User-Agent': 'Skland/1.0.1 (com.hypergryph.skland; build': '100001014; Android 31; ) Okhttp/4.11.0',
'vCode': '100001014',
'vName': '1.0.1',
'dId': 'de9759a5afaa634f',
'platform': '1'
```

## 有关新版本获得Cred必传的dId参数

2024.9.10 森空岛登入接口引入了数美接口，请求头必须传递dId参数，导致无法正常登陆

现已解决，具体实现看`SecuritySm.py`文件