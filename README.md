## Log2MQ

一个将文本日志 tail 后转到 ZeroMQ 的工具。

## 安装依赖

在源代码目录下执行

```
$ python setup.py develop

# 或者
$ python setup.py develop
```

## 运行

```
$ python -m log2mq.run -c /path/to/config
```

## 配置文件

格式为 YAML 类型，如下

```
---
endpoint: 'tcp://*:9999'     # 绑定的服务端口
logfile: '/path/to/logfile'  # 需要传输的日志
```
