# Proxy pool all in one

在实际使用中发现，免费的代理池服务主要有几点问题：

* 代理的可用性不高，尤其是https代理几乎没有可用的代理服务器，http代理虽然有不少可用的代理服务器，但是混杂在大量不可用服务器之中。
* 代理池无法整合为一个代理地址，导致很多工具使用不方便，例如我希望工具sqlmap能够使用代理池，我希望提供给sqlmap一个代理地址，让sqlmap以为只有一个代理服务器，而该代理服务器背后会使用代理池来访问。

[proxy_pool项目](https://github.com/jhao104/proxy_pool)提供了一个增强免费代理池可用性的解决方案，但是在实际使用下来，即使是经过proxy_pool挑选的代理，依然存在很大一部分是不可用的。

本项目在proxy_pool项目的基础上进行改造，主要实现了以下功能：

* 考虑到免费代理池中几乎无可用的https代理，故放弃https代理，专注于http代理。
* 对http代理的可用性验证进一步改造，使得我们构造的代理池中的代理可用性极强。
* 通过proxyHelper模块，实现对外只需提供一个代理地址，任何应用只需要简单地设置代理为该地址，实际上的请求会随机从代理池中找代理服务器发送。
* proxyHelper模块也会对可用性作进一步验证，如果为当前接收到的请求选取的代理服务器没有成功完成代理，那么proxyHelper会自动尝试寻找代理池中其他可用的代理服务器尝试发送该请求，这一切都是被封装好的，在设置代理为proxyHelper地址的应用看来，它的代理访问直接就是成功的。
* proxyHelper模块可以单独使用，如果你有稳定的付费代理池，也可以通过proxyHelper将该代理池封装为一个代理地址。

# 安装

```
pip install -r requirements.txt
sudo docker pull redis
sudo docker run -d --name redis -p 6379:6379 redis --requirepass "password"
```

然后将setting.py中的DB_CONN设置为redis的url即可。

# 使用

为了保证http代理的可用性，本项目验证http代理可用性的方案是设置访问目标的url及其网页上的任意关键词，项目会自动通过代理访问该网页，如果关键词出现在返回报文中，则认为http代理可用，并且项目会每间隔1分钟验证一次所有http代理的可用性。

因此，当我们需要使用代理池访问目标时，首先需要在setting.py中配置目标的url及其关键词：

```python
URL = "httpbin.org"
KEYWORD = "A simple HTTP"
```

设置完成之后执行下面的命令运行项目：

```shell
python3 proxyPool.py schedule
python proxyPool.py server
```

此时项目会在本地的5010开启web服务，访问`http://localhost:5010/all/`可以看到当前抓取并验证之后得到的所有可用http代理服务器。

接下来只需要简单地执行下面地命令，即可打开proxyHelper:

```shell
python3 proxyHelper.py
```

执行之后，proxyHelper模块会在本机的8080开启http代理服务，并从本机的5010端口获取代理池信息，处理接收到的代理信息，并从代理池中获取代理服务器，尝试使用代理服务器发送请求，若发送失败则会选择其他代理服务器再次尝试发送请求，直到请求发送成功或达到最大尝试次数。

接下来只需要将应用的代理设置为本机的8080即可使用代理池了。