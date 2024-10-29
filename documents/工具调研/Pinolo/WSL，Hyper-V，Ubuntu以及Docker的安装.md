## VMWare中部署Docker

VMWare，在ubuntu16.4上安装的docker，始终无法成功拉取mysql镜像，故无法利用docker部署mysql。运行指令`docker pull mysql:8.0.30`时，总是报以下的错，在Docker配置文件 `/etc/docker/daemon.json`中换了很多源也解决不了。
```
error pulling image configuration: download failed after attempts=6: dial tcp 154.83.15.45:443: connect: connection refused
```

上述报错的原因是：VMware 和Hyper-V不兼容；但是如果卸载Hyper-V,Docker就不能使用了。因此，在window下Docker（必须有Hyper-V）和用VMware创建的虚拟机会产生冲突。由于两种虚拟化技术都是基于CPU等底层硬件的Hypervisor(虚拟机监视器)机制来实现的，所以考虑使用Window自带的WSL(Windows Subsystem for Linux)。

## 启用Hyper-V
1. 管理员模式运行PowerShell；  
2. 复制如下命令，输入、回车：  
`Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All`  
3. 如果是第一次安装，执行完成后，会询问是否重启系统，此时输入n，选择不重启，会看到打印内容有如下字样：RestartNeeded : True ；  
4. 如果之前已经开启，会直接看到如下字样：RestartNeeded : False ；


问题1：上述步骤2遇到如下报错。

```
Enable-WindowsOptionalFeature -Online -FeatureName:Microsoft-Hyper-V -All

Enable-WindowsOptionalFeature : 参数错误。  
所在位置 行:1 字符: 1  
+ Enable-WindowsOptionalFeature -Online -FeatureName:Microsoft-Hyper-V  ...  
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
    + CategoryInfo          : NotSpecified: (:) [Enable-WindowsOptionalFeature], PSArgumentException  
    + FullyQualifiedErrorId : Microsoft.Dism.Commands.EnableWindowsOptionalFeatureCommand
```
解决方法如下：[Hyper-v无法启动,安装了win10系统 - Microsoft Community](https://answers.microsoft.com/zh-hans/windows/forum/all/hyper/166d60f6-9e36-444b-9046-fb77ebe39eec)
```
您好！

您上述的命令错误，缺少了（“”）的字符，

建议您使用以下命令先查询您当前计算机内Hyper-V组件的应用名，

再套用到安装命令中进行安装。

dism /Online  /Get-Features

把-FeatureName修改一下
```

问题2：专业版在运行以上命令后可以完成开启。但家庭版和学生版开启时会报错(即使是管理员模式下也没用)。报错：`enable-windowsoptionalfeature : 功能名称 microsoft-hyper-v 未知`。
解决方法见：[windows 安装Docker步骤以及在每一个步骤遇到问题合集_windows docker-CSDN博客](https://blog.csdn.net/qq_39838607/article/details/127121690)


问题3：5. 开启Hyper-V，如下图所示，可能会遇到问题`win10错误代码0x80070057`
![[Pasted image 20240720161218.png|500]]
解决方法见：[win10错误代码0x80070057的解决方法 四种方法快速解决_windows10_Windows系列_操作系统_脚本之家 (jb51.net)](https://www.jb51.net/os/win10/729087.html)

## 启用WSL
1. 接着复制输入如下命令，回车：  
```
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -All
```

2. 如果是第一次安装会提示是否重启，此时输入y，选择重启；  
3. 如果之前已经开启，会直接看到如下字样：RestartNeeded : False ；
4. 开启服务
打开控制面板，选择程序 —— 启用或关闭Windows功能，勾选 适用于Linux的Windows子系统还有虚拟机平台选项
![[Pasted image 20240720162249.png|400]]
选择以下两项：

![[Pasted image 20240720162316.png]]

## 选择WSL2

1. 重启后，重新管理员模式运行PowerShell；  
2. 复制如下命令，输入、回车：
```
wsl --set-default-version 2  
```
3. 此时提示“操作成功完成”，即已切换成功。
4. 更新 wsl。（需要翻墙的情况下）
```
wsl --update
```

## 下载Docker
具体参考链接：
[在 Windows 中通过 WSL 2 高效使用 Docker_windows wsl2 docker-CSDN博客](https://blog.csdn.net/u012558210/article/details/131845638)

[windows 安装Docker步骤以及在每一个步骤遇到问题合集_windows docker-CSDN博客](https://blog.csdn.net/qq_39838607/article/details/127121690)

[Docker Desktop+WSL2安装到自定义路径-CSDN博客](https://blog.csdn.net/u011031430/article/details/137425929?csdn_share_tail=%7B%22type%22%3A%22blog%22%2C%22rType%22%3A%22article%22%2C%22rId%22%3A%22137425929%22%2C%22source%22%3A%22u011031430%22%7D&fromshare=blogdetail)
## 在WSL2安装Ubuntu22.04
具体参考链接：
[windows11 安装wsl2（子系统）并配置ubuntu20.04_win11 wsl2-CSDN博客](https://blog.csdn.net/Lastvil/article/details/130687053)

[使用Windows11自带的WSL安装Ubuntu Linux系统教程-CSDN博客](https://blog.csdn.net/bule_shake/article/details/135992375)

1. 打开Microsoft Store；  
2. 搜索Ubuntu，找到22.04版本，目前是22.04.1 LTS版本，点击“获取”；  
3. 下载完后点击打开，如果出现报错，继续管理员模式打开PowerShell，输入如下命令；  
```
wsl --update
```
4. 升级成功后，在开始菜单重新打开ubuntu22.04.1 LTS即可，即安装成功；其余就是ubuntu的基本用法了，  
5. 可以试着安装一个gedit，安装好后可以直接在开始菜单中打开执行图形化界面；  
6. 此外，在资源管理器中也可以直接访问到linux子系统的文件系统；
7. 迁移到D盘： 
* [在 Win11安装 Ubuntu20.04子系统 WSL2 到其他盘（此处为D盘，因为C盘空间实在不能放应用）_wsl2安装ubantu到d盘-CSDN博客](https://blog.csdn.net/orange1710/article/details/131904929)       特别注意：4.接下来。。。。中， 代码应该是wsl --export Ubuntu-20.04 D:/export.tar
* [在 Win系统安装 Ubuntu20.04子系统 WSL2 （默认是C盘，第7步开始迁移到D盘，也可以不迁移）_windows10 wsl2 ubuntu 安装位置-CSDN博客](https://blog.csdn.net/qq_51081700/article/details/139271938)
## 参考链接

[WIN11下的Linux子系统WSL2(hyperV)与VMware多虚拟机共存安装 - am7s - 博客园 (cnblogs.com)](https://www.cnblogs.com/am7s/p/17002921.html)
[启用 Hyper-V 以在 Windows 10 上创建虚拟机_window 10 开启hyper-CSDN博客](https://blog.csdn.net/g3202325878/article/details/136186233)

[windows11 安装wsl2（子系统）并配置ubuntu20.04_win11 wsl2-CSDN博客](https://blog.csdn.net/Lastvil/article/details/130687053)

[使用Windows11自带的WSL安装Ubuntu Linux系统教程-CSDN博客](https://blog.csdn.net/bule_shake/article/details/135992375)

[Win10 系统安装 Linux 子系统教程(WSL2 + Ubuntu 20.04 + Gnome 桌面 ）_wsl安装教程-CSDN博客](https://blog.csdn.net/FSKEps/article/details/118493578)


[Windows 11 Microsoft Store（微软商店）加载不出来，怎么办？_微软商店加载不出来-CSDN博客](https://blog.csdn.net/weixin_53187512/article/details/123529520)


配置阿里云镜像加速地址：
[windows 安装Docker步骤以及在每一个步骤遇到问题合集_windows docker-CSDN博客](https://blog.csdn.net/qq_39838607/article/details/127121690)


