# How to install golang 1.16.2

1 First, download [go1.16.2.linux-amd64.tar.gz](https://golang.google.cn/dl/go1.16.2.linux-amd64.tar.gz) from the official website:

> We assume your installation path is `~/go/go1.16.2`

```shell
cd ~/go/go1.16.2
wget https://golang.google.cn/dl/go1.16.2.linux-amd64.tar.gz
tar -xzf go1.16.2.linux-amd64.tar.gz
mkdir goPath
```

Now you will see two directories `go` and `goPath` under `~/go/go1.16.2`

2 Second, add `GOROOT` and `GOPATH` to your environment variables:

```shell
# open ~/.bashrc, add the following commands at the end of the file:
export GOHOME=~/go/go1.16.2
export GOROOT=${GOHOME}/go
export GOPATH=${GOHOME}/goPath
export PATH=$PATH:$GOROOT/bin
export PATH=$PATH:$GOPATH/bin
```

3 Finally, execute `source ~/.bashrc`. Now your `golang` can work:

```shell
$ go version
go version go1.16.2 linux/amd64
```

