# 墨水屏相框

### 效果展示
![avatar](./docs/images/img1.png)
![avatar](./docs/images/img2.png)
![avatar](./docs/images/back.png)


### 材料清单
1. 树莓派\*1  
2. SD卡(树莓派用)\*1  
3. 电源适配器\*1    
4. 网线\*1  
5. 墨水屏(我用的是7.5寸微雪墨水屏)\*1  
6. 能装得下墨水屏的相框\*1 

### 准备树莓派
1. sd卡安装操作系统(我用的是Raspberry Pi OS lite版本, 在sd卡中新建一个名为SSH的文件可以默认开启ssh连接)
2. 将sd卡装到树莓派上, 插上网线, 并连接电源开机, 在路由器后台可以看到树莓派ip
3. ssh到树莓派, 传文件可用scp命令或其他图形化工具

### 安装墨水屏
1. 连接驱动板与树莓派
2. 连接驱动板与屏幕
3. 驱动这个屏幕需要启用树莓派的SPI接口  
    sudo raspi-config  
    选择Interfacing Options -> SPI -> Yes 开启SPI接口
4. 安装驱动
    git clone https://github.com/TomWhitwell/SlowMovie/  
    cd SlowMovie/e-paper/RaspberryPi&JetsonNano/python  
    sudo python3 setup.py install (python版本问题请自行查阅资料)
5. 测试  
    python3 examples/epd_7in5_V2_test.py (选择对应屏幕的测试程序)