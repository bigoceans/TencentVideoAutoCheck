# 腾讯视频签到Github Action版

> **当前版本：v1.1**  
> **更新日期：2026-05-21**

## 版本更新说明

### v1.1 (2026-05-21)
- ✅ 移除 Server酱 推送，改为 **WxPusher 微信推送**
- ✅ 新增完善的异常处理机制
- ✅ 支持签到成功/失败微信通知
- ✅ 更新 GitHub Actions 组件到最新版本
- ✅ WxPusher 配置可选，不配置也能正常运行

### v1.0
- 基础签到功能
- Server酱 推送支持

---

## 今日签到状态

[![Tencent Video Auto Check-in](https://github.com/Hayfan-wu/TencentVideoAutoCheck/actions/workflows/main.yml/badge.svg)](https://github.com/Hayfan-wu/TencentVideoAutoCheck/actions/workflows/main.yml)

---

## 使用说明

### 配置流程

1. **Fork 本仓库**，然后点击你的仓库右上角的 Settings，找到 Secrets 这一项，添加以下变量：
   - `LOGIN_COOKIE` - 腾讯视频登录 Cookie
   - `AUTH_COOKIE` - 腾讯视频认证 Cookie
   - `WXPUSHER_TOKEN`（可选）- WxPusher 应用 Token
   - `WXPUSHER_UID`（可选）- WxPusher 用户 UID

2. 设置好环境变量后点击你的仓库上方的 `Actions` 选项，第一次打开需要点击 `I understand...` 按钮，确认在 Fork 的仓库上启用 GitHub Actions。

3. 任意发起一次 commit，可以参考下图流程修改 readme 文件：
   - 打开 `README.md`，点击修改按钮
   - 修改任意内容，这里在末尾插入了空格。移动到最下面，点击提交。

4. 至此自动签到就搭建完毕了。

---

## Cookie 获取方法

### login_cookie、auth_cookie 的获取

1. 网页登录 [腾讯视频](https://v.qq.com/)

2. 进入该网页：https://vip.video.qq.com/fcgi-bin/comm_cgi?name=hierarchical_task_system&cmd=2

3. F12 输入 `document.cookie` 然后回车，得到的全部信息就是 **login_cookie**

4. **auth_cookie** 是 login_cookie 的一部分，找到 login_cookie 中内容为 `vqq_vusession=` 的地方，将等号之后的内容全部删掉。之前的全部内容就是 auth_cookie 了。

5. 获取配置信息的效果图如下：
   
   ![获取配置信息](https://github.com/bigoceans/TencentVideoAutoCheck/blob/main/img/1.jpg?raw=true)

---

## WxPusher 推送配置（可选）

如果你想在签到成功或失败时收到微信通知，可以配置 WxPusher：

### 1. 注册 WxPusher
- 访问 [WxPusher 官网](https://wxpusher.zjiecode.com/)
- 微信扫码登录

### 2. 创建应用
- 进入「应用管理」→「创建应用」
- 填写应用名称，创建后复制 **AppToken**

### 3. 获取 UID
- 在应用详情页点击「生成二维码」
- 微信扫码关注
- 在「我的」→「我的UID」中查看 **UID**

### 4. 配置 Secrets
在 GitHub 仓库 Settings → Secrets → Actions 中添加：
- `WXPUSHER_TOKEN`：你的 AppToken（如 `AT_xxxxxxxxxxxxxxxx`）
- `WXPUSHER_UID`：你的 UID（如 `UID_xxxxxxxxxxxxxxxx`）

> **注意**：如果不配置 WxPusher，签到功能仍然可以正常运行，只是不会收到微信推送通知。

---

## 配置 workflow 执行信息写入到 run.log

1. 仓库左上方 settings
   
   ![配置workflow](https://github.com/bigoceans/TencentVideoAutoCheck/blob/main/img/2.jpg?raw=true)

2. 如图
   
   ![配置workflow](https://github.com/bigoceans/TencentVideoAutoCheck/blob/main/img/3.jpg?raw=true)

3. 如图，保存
   
   ![配置workflow](https://github.com/bigoceans/TencentVideoAutoCheck/blob/main/img/4.jpg?raw=true)

---

## 推送消息示例

### 签到成功
```
腾讯视频签到成功！

获得积分：5
签到时间：2024-01-15 08:15:32
```

### 签到失败
```
腾讯视频签到失败

错误信息：签到失败，返回码: -1
```

---

## 相关链接

- [WxPusher 官网](https://wxpusher.zjiecode.com/)
- [WxPusher 文档](https://wxpusher.zjiecode.com/docs/)
- [原项目地址](https://github.com/bigoceans/TencentVideoAutoCheck)
