## 简介
小工具名称是PS360_Mocker, 在Xero Workflow打开之后, 模拟PS360与之进行交换. 只需简单几个按键, 或简单一句命令行就可以实现[自动/手动]发送打开回执\发送各种Draft Preliminary Sign 等指令.

##安装
确认已安装Python3
安装如下组件
```
$ pip install requests
$ pip install websockets
```

## 配置
打开文件config.ini , 修改你需要登录的用户与其密码. 修改对应的Xero workflow服务器的登录Url

## 自动发送打开回执
打开一个新的Cmd窗口, 输入如下命令
```
$ python ps360_auto_opened.py 
```
此模拟器会在XWF打开每个报告的时候, 自动发送已打开的回执


## 指令
打开一个新的Cmd窗口, 输入如下命令
```bash
python ps360_mocker.py 
```
```
O              //手动发送已打开报告回执
send [status] [patient_id] [accession number]  //发送针对指定报告的某种状态
ex:  send cancelled PKODB44 20230529164440 针对报告[20230529164440] 发送取消状态

Q             //退出模拟器
```

## Comment
在XWF 打开每个报告的30秒内, 记得发送已打开报告回执, 不然会在XWF弹窗显示未链接PS360. 你也可以打开 ps360_auto_opened, 让模拟器自动发送已打开报告回执.

## TODO
- 命令Link / Unlink
- 模拟器连接XWF 服务器不稳定. 总是崩溃退出.