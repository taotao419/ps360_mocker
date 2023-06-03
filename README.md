## 简介
PS360_Mocker Xero Workflow打开之后, 模拟PS360与之进行交换. 只需简单几个按键, 或简单一句命令行就可以实现[自动/手动]发送打开回执\发送各种Draft Preliminary Sign 等指令.

## 配置
打开文件config.ini , 修改你需要登录的用户与其密码. 修改对应的Xero workflow服务器的登录Url

## 指令
```
O              //手动发送已打开报告回执
AO             //等待XWF服务器打开某报告, 并自动发送已打开回执
send [status] [patient_id] [accession number]  //发送针对指定报告的某种状态
ex:  send cancelled PKODB44 20230529164440 针对报告[20230529164440] 发送取消状态

Q             //退出模拟器
```

## Comment
在XWF 打开某个报告后的30秒内, 记得发送已打开报告回执, 不然会在XWF弹窗显示未链接PS360. 你也可以使用命令AO, 让模拟器自动发送已打开报告回执.

## TODO
- 命令Link / Unlink
- 模拟器连接XWF 服务器不稳定. 总是崩溃退出.