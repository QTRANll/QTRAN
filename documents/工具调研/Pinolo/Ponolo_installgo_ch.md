# How to install golang 1.16.2

1首先，从官方网站下载[go1.16.2.linux-amd64.tar.gz](https://golang.google.cn/dl/go1.16.2.linux-amd64.tar.gz):

> 我们假设您的安装路径是`~/go/go1.16.2`。

```shell
cd ~/go/go1.16.2
wget https://golang.google.cn/dl/go1.16.2.linux-amd64.tar.gz
tar -xzf go1.16.2.linux-amd64.tar.gz
mkdir goPath
```

现在你会看到两个目录`go`和`goPath`在`~/go/go1.16.2`下。

2 其次，在你的环境变量中添加`GOROOT`和`GOPATH`:
![[Pasted image 20240719145210.png|400]]

```shell
# open ~/.bashrc, add the following commands at the end of the file:
export GOHOME=~/go/go1.16.2
export GOROOT=${GOHOME}/go
export GOPATH=${GOHOME}/goPath
export PATH=$PATH:$GOROOT/bin
export PATH=$PATH:$GOPATH/bin
```

3 最后，在home目录下执行`source ~/.bashrc`。现在你的`golang`可以工作了:

```shell
$ go version
go version go1.16.2 linux/amd64
```

