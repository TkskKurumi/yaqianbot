# 千千bot

## 快速开始

安装依赖库。（其中AnnoyIndex在Windows下安装需要VC++生成工具，或者使用已编译的[wheel](https://www.lfd.uci.edu/~gohlke/pythonlibs/#annoy)安装）
``` shell
pip install -r requirements.txt
```

配置cqhttp，使用反向websocket连接，默认为8008端口。可以在main.py中修改。

[cqhttp使用反向websocket连接。](https://aiocqhttp.nonebot.dev/#/getting-started#%E4%BD%BF%E7%94%A8%E5%8F%8D%E5%90%91-websocket)

```python
run(port=port)
```

然后，运行。。。

```shell
python main.py
```

## 某些功能的配置

### bot的管理员

在main.py中运行add_su(qq号)，指定bot的*SUPERUSER*（可以有多人）。

### OSU!API

OSU!是是一款Windows平台上的同人音乐游戏。bot有OSU!查询用户信息的功能。[获取OSU!的OAuth App客户端信息](https://osu.ppy.sh/docs/index.html#registering-an-oauth-application)，将client_id、client_secret以json形式填写在/utils/osu/client_info.json中，bot的OSU!API才可正常工作。

### Pixiv

bot拥有Pixiv爬虫功能，在Chrome浏览器中登录pixiv，而后使用[EditThisCookie插件](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)导出cookie信息以登录。bot需要本地代理https://127.0.0.1:1081（在/utils/pyxyv.py中设定），请自备魔法上网（

而后*SUPERUSER*对bot发送一条pixiv插画链接后，爬虫将会获取与之相关的Pixiv插画，才可以使用*!色图*

***各种功能在plg_setu被导入后，都会考虑从中取色图作为背景，如果无法使用Pixiv爬虫，请在main.py中不要导入plg_setu***

