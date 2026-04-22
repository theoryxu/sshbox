# sshbox

`sshbox` 是一个面向个人机器的轻量 SSH 工具，核心目标是把一组常用服务器配置集中到一个 JSON 文件里，然后用统一命令完成登录、上传、下载、端口转发和 SSH 公钥下发。

它适合这样的场景：

- 你维护少量固定服务器，不想每次都手敲 `user@host -p port`
- 你愿意用本地配置文件保存密码，并接受这个工具通过 `expect` 自动输入密码
- 你希望快速做一次性文件传输、临时端口转发或初始化远端 `authorized_keys`

## 功能概览

当前版本支持以下命令：

- `sshbox list`：列出已配置服务器
- `sshbox ocfg`：打开本地配置文件
- `sshbox connect <name>`：按配置连接目标服务器
- `sshbox put <name> <local_path> [remote_path]`：上传文件
- `sshbox get <name> <remote_path> [local_path]`：下载文件
- `sshbox forward <name> <local_port> <remote_port>`：把本地端口转发到远端 `127.0.0.1:<remote_port>`
- `sshbox forward <name> <local_port> <remote_host> <remote_port>`：把本地端口转发到远端指定主机和端口
- `sshbox push-ssh-pub <name> [pubkey_path]`：把本地公钥追加到远端 `~/.ssh/authorized_keys`
- `sshbox example`：打印示例配置文件路径

## 目录结构

- [sshbox](/Users/theoryxu/IdeaProjects/sshbox/sshbox:1)：主程序，Python 脚本
- [deploy.sh](/Users/theoryxu/IdeaProjects/sshbox/deploy.sh:1)：本地部署脚本
- [servers.example.json](/Users/theoryxu/IdeaProjects/sshbox/servers.example.json:1)：默认示例配置模板
- [tests/test_sshbox.py](/Users/theoryxu/IdeaProjects/sshbox/tests/test_sshbox.py:1)：主程序测试
- [tests/test_deploy.py](/Users/theoryxu/IdeaProjects/sshbox/tests/test_deploy.py:1)：部署脚本测试

## 依赖

运行 `sshbox` 前，机器上至少需要：

- `python3`
- `ssh`
- `scp`
- `expect`

其中：

- `connect`、`put`、`get`、`forward`、`push-ssh-pub` 都依赖 `expect` 自动输入密码
- `put`、`get` 依赖 `scp`
- `ocfg` 会优先使用 `EDITOR`，否则尝试 `open` 或 `xdg-open`

如果缺少关键命令，程序会直接报错退出。

## 安装与部署

仓库提供了一个本地部署脚本 [deploy.sh](/Users/theoryxu/IdeaProjects/sshbox/deploy.sh:1)。

默认部署方式是复制文件到 `~/.local/bin`：

```bash
./deploy.sh
```

如果你希望安装路径始终跟随仓库代码，可以使用软链接模式：

```bash
./deploy.sh link
```

### deploy.sh 做了什么

部署脚本会执行以下动作：

1. 把 `sshbox` 安装到 `~/.local/bin/sshbox`
2. 把测试文件安装到 `~/.local/bin/tests/test_sshbox.py`
3. 确保 `~/.config/sshbox` 存在
4. 如果 `~/.config/sshbox/servers.example.json` 不存在，就从仓库里的模板复制过去
5. 如果 `~/.config/sshbox/servers.json` 不存在，就用同一份模板初始化
6. 如果 `servers.json` 已存在，则保留现有内容，不覆盖

### 可覆盖的环境变量

`deploy.sh` 支持以下环境变量，方便测试或安装到自定义位置：

- `TARGET_BIN`：默认 `~/.local/bin/sshbox`
- `TARGET_TEST`：默认 `~/.local/bin/tests/test_sshbox.py`
- `TARGET_CONFIG_DIR`：默认 `~/.config/sshbox`
- `TARGET_CONFIG`：默认 `~/.config/sshbox/servers.json`
- `TARGET_EXAMPLE`：默认 `~/.config/sshbox/servers.example.json`

示例：

```bash
TARGET_BIN="$HOME/bin/sshbox" \
TARGET_CONFIG_DIR="$HOME/.sshbox" \
./deploy.sh
```

## 配置文件

`sshbox` 的配置目录默认为：

```text
~/.config/sshbox
```

默认会涉及两个文件：

- `servers.json`：真实使用的配置文件
- `servers.example.json`：示例模板

无论你是先运行 `deploy.sh`，还是第一次直接运行 `sshbox`，如果 `servers.json` 不存在，程序都会初始化一份默认模板。

### 默认模板

默认生成的 `servers.json` 内容如下：

```json
[
  {
    "name": "prod",
    "host": "192.168.1.10",
    "port": 22,
    "user": "root",
    "comment": "Production",
    "password": "replace-me"
  },
  {
    "name": "test",
    "host": "10.0.0.8",
    "port": 2222,
    "user": "ubuntu",
    "comment": "Testing",
    "password": "replace-me-too"
  }
]
```

你需要把里面的示例主机、用户名和密码替换成真实值。

### 字段说明

每条服务器配置是一个 JSON 对象，当前支持字段如下：

- `name`：服务名，命令行里用它来选择目标，例如 `prod`
- `host`：主机地址或 IP
- `port`：SSH 端口，可选，默认 `22`
- `user`：登录用户名
- `comment`：备注，可选，用于 `list` 展示
- `password`：登录密码，不能为空

### 配置约束

程序会在加载配置时做校验：

- 顶层必须是数组
- 每条记录必须是对象
- `name`、`host`、`user`、`password` 必填
- `port` 必须能转成整数

如果格式不对，`sshbox` 会报错退出，不会继续执行实际 SSH 操作。

## 使用说明

### 查看帮助

```bash
sshbox --help
```

### 列出所有服务器

```bash
sshbox list
```

输出会包含：

- `NAME`
- `USER`
- `HOST`
- `PORT`
- `COMMENT`

如果配置文件为空数组，程序会提示你先编辑配置。

### 打开配置文件

```bash
sshbox ocfg
```

行为顺序如下：

1. 如果设置了 `EDITOR`，使用 `EDITOR`
2. 否则在 macOS 上优先尝试 `open`
3. 再否则尝试 `xdg-open`
4. 如果都没有，就报错并打印配置文件路径

例如：

```bash
EDITOR="vim" sshbox ocfg
```

### 连接服务器

```bash
sshbox connect prod
```

该命令会根据 `prod` 对应的配置，执行等价于：

```bash
ssh -p <port> <user>@<host>
```

但密码输入由 `expect` 自动完成，同时会自动处理首次连接时的主机指纹确认提示。

### 上传文件

上传本地文件到远端当前目录：

```bash
sshbox put prod ./build.tar.gz
```

上传到指定远端目录或文件名：

```bash
sshbox put prod ./build.tar.gz /tmp/build.tar.gz
```

### 下载文件

把远端文件下载到当前目录：

```bash
sshbox get prod /tmp/build.tar.gz
```

下载到指定本地路径：

```bash
sshbox get prod /tmp/build.tar.gz ./downloads/build.tar.gz
```

### 本地端口转发

把本地 `15432` 转发到远端服务器自己的 `127.0.0.1:5432`：

```bash
sshbox forward prod 15432 5432
```

把本地 `13306` 转发到远端可见网络中的其他主机：

```bash
sshbox forward prod 13306 10.0.1.5 3306
```

这里的行为等价于：

```bash
ssh -N -L <local_port>:<remote_host>:<remote_port> -p <port> <user>@<host>
```

程序会加上 `ExitOnForwardFailure=yes`，如果端口绑定失败会立即退出。

### 推送 SSH 公钥

如果你想先用密码登录一次，再把本机公钥写到远端，可以执行：

```bash
sshbox push-ssh-pub prod
```

默认会按这个顺序寻找本地公钥：

1. `~/.ssh/id_ed25519.pub`
2. `~/.ssh/id_rsa.pub`

也可以显式指定路径：

```bash
sshbox push-ssh-pub prod ~/.ssh/custom_key.pub
```

这个命令会在远端执行以下逻辑：

- 创建 `~/.ssh`
- 确保目录权限为 `700`
- 创建 `~/.ssh/authorized_keys`
- 确保文件权限为 `600`
- 如果公钥不存在则追加
- 如果公钥已存在则不重复追加

### 查看示例文件路径

```bash
sshbox example
```

这个命令会输出本机正在使用的 `servers.example.json` 路径，方便你快速查看模板位置。

## 常见用法示例

### 示例 1：首次安装并连接

```bash
./deploy.sh
sshbox ocfg
sshbox list
sshbox connect prod
```

### 示例 2：上传构建产物并重启服务

```bash
sshbox put prod ./dist/app.tar.gz /tmp/app.tar.gz
sshbox connect prod
```

### 示例 3：转发数据库端口到本地

```bash
sshbox forward prod 15432 5432
psql -h 127.0.0.1 -p 15432
```

### 示例 4：先推送公钥，再改用密钥登录

```bash
sshbox push-ssh-pub prod
ssh prod
```

注意最后一行只是示意。实际是否能直接 `ssh prod` 取决于你的 `~/.ssh/config` 是否已经另外配置了 Host 别名。

## 安全说明

这个工具当前的设计很直接，也意味着有明显的安全边界：

- `servers.json` 里保存的是明文密码
- `expect` 会以环境变量方式把密码传给子进程
- 适合个人机器、临时环境或受控内网场景
- 不适合高安全等级环境，也不适合多人共享机器

如果你需要更严格的安全方案，更合理的方向通常是：

- 改用 SSH key 登录
- 把主机别名维护在 `~/.ssh/config`
- 使用密码管理器、系统钥匙串或专门的密钥分发方案

## 开发与测试

运行测试：

```bash
python3 -m unittest discover -s tests
```

如果只想跑部署相关测试：

```bash
python3 -m unittest tests.test_deploy
```

如果只想跑主程序测试：

```bash
python3 -m unittest tests.test_sshbox
```

## 已知限制

- 目前只支持密码登录流程，不支持直接读取 SSH 私钥配置
- 远端命令执行能力很有限，除了 `push-ssh-pub` 没有额外封装
- 配置文件路径当前是固定规则，不支持命令行参数切换 profile
- `ocfg` 依赖本机可用编辑器或系统打开命令

## 维护建议

如果你长期使用这个工具，建议至少做这几件事：

- 部署后第一时间修改 `servers.json` 默认密码占位符
- 给 `~/.config/sshbox/servers.json` 保持 `600` 权限
- 优先用 `push-ssh-pub` 切到公钥登录，减少密码使用频率
- 定期删除不再使用的服务器配置
