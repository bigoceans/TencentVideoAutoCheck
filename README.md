# 停止维护


# 腾讯视频签到Github Action版

## 今日签到状态

[![Baidu Tieba Auto Sign](https://github.com/bigoceans/TencentVideoAutoCheck/actions/workflows/main.yml/badge.svg)](https://github.com/bigoceans/TencentVideoAutoCheck/actions/workflows/main.yml)

## 使用说明
### 配置流程

1. Fork 本仓库，然后点击你的仓库右上角的 Settings，找到 Secrets 这一项，添加 LOGIN_COOKIE 和 AUTH_COOKIE 两个变量。

2. 设置好环境变量后点击你的仓库上方的 `Actions` 选项，第一次打开需要点击 `I understand...` 按钮，确认在 Fork 的仓库上启用 GitHub Actions 。

3. 任意发起一次commit，可以参考下图流程修改readme文件。

- 打开`README.md`，点击修改按钮
- 修改任意内容，这里在末尾插入了空格。移动到最下面，点击提交。

4. 至此自动签到就搭建完毕了。

### login_cookie、auth_cookie的获取
1. 网页登录 腾讯视频

2. 进入该网页：https://vip.video.qq.com/fcgi-bin/comm_cgi?name=hierarchical_task_system&cmd=2

3. F12 输入 document.cookie然后回车，得到的全部信息就是login_cookie；
4. auth_cookie是login_cookie的一部分，找到login_cookie中内容为`vqq_vusession=`的地方，将等号之后的内容全部删掉。之前的全部内容就是auth_cookie了。
5. 获取配置信息的效果图如下：
![获取配置信息](https://github.com/bigoceans/TencentVideoAutoCheck/blob/main/img/1.jpg?raw=true)

### 配置workflow执行信息写入到run.log
1. 仓库左上方settings
![配置workflow执行信息写入到run.log](https://github.com/bigoceans/TencentVideoAutoCheck/blob/main/img/2.jpg?raw=true)
2. 如图
![配置workflow执行信息写入到run.log](https://github.com/bigoceans/TencentVideoAutoCheck/blob/main/img/3.jpg?raw=true)
3. 如图，保存
![配置workflow执行信息写入到run.log](https://github.com/bigoceans/TencentVideoAutoCheck/blob/main/img/4.jpg?raw=true)



