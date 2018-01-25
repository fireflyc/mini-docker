###A mini container
一个模拟Docker的container系统

![截图](./screenshot/jietu-hd.gif)


```mkdir /tmp/rootfs && tar -Jxf centos-7-docker.tar.xz -C /tmp/rootfs && git clone https://github.com/fireflyc/mini-docker.git
cd mini-docker/ && pipenv shell && python setup.py develop
```