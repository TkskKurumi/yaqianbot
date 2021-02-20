# 千千bot

## 开始

安装依赖库[^注]
[^注]: 其中AnnoyIndex在Windows下安装需要VC++生成工具，或者使用已编译的[wheel](https://www.lfd.uci.edu/~gohlke/pythonlibs/#annoy)安装。

``` shell
pip install -r requirements.txt
```


配置cqhttp，使用反向websocket连接，默认为8008端口。可以在main.py中修改。[aiocqhttp使用反向websocket连接的文档。](https://aiocqhttp.nonebot.dev/#/getting-started#%E4%BD%BF%E7%94%A8%E5%8F%8D%E5%90%91-websocket)

```python
run(port=port)
```

然后，运行。。。

```shell
python main.py
```
