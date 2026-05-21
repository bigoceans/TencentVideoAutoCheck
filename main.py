import requests
import requests.utils
import time
import json
import os
import sys
import re

sys.stdout.flush()

def log_message(msg):
    """输出日志并立即刷新"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    sys.stdout.flush()
    return full_msg

def send_wxpusher_message(app_token, content, uids, summary=None):
    """使用 WxPusher 发送消息"""
    if not app_token or not uids:
        log_message("WxPusher: 未配置 AppToken 或 UID，跳过推送")
        return None
    
    api_url = 'https://wxpusher.zjiecode.com/api/send/message'
    headers = {'Content-Type': 'application/json'}
    
    data = {
        "appToken": app_token,
        "content": content,
        "contentType": 1,
        "uids": uids if isinstance(uids, list) else [uids]
    }
    
    if summary:
        data["summary"] = summary
    
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        result = response.json()
        
        if result.get('code') == 1000:
            log_message("WxPusher: 消息推送成功")
            return result
        else:
            log_message(f"WxPusher: 推送失败 - {result.get('msg', '未知错误')}")
            return result
    except Exception as e:
        log_message(f"WxPusher: 推送异常 - {str(e)}")
        return None

def send_wxpusher_notify(wxpusher_token, wxpusher_uid, content, summary):
    """安全发送 WxPusher 通知"""
    if wxpusher_token and wxpusher_uid:
        send_wxpusher_message(wxpusher_token, content, wxpusher_uid, summary)

def extract_cookie_field(cookie, field_name):
    """从 cookie 字符串中提取指定字段的值"""
    match = re.search(rf'{field_name}=([^;]*)', cookie)
    return match.group(1) if match else None

def tencent_video_sign_in():
    log_message("=" * 50)
    log_message("腾讯视频自动签到开始")
    log_message("=" * 50)
    
    # 从环境变量获取配置
    login_cookie = os.getenv('LOGIN_COOKIE', '').strip()
    auth_cookie = os.getenv('AUTH_COOKIE', '').strip()
    wxpusher_token = os.getenv('WXPUSHER_TOKEN', '').strip()
    wxpusher_uid = os.getenv('WXPUSHER_UID', '').strip()
    
    log_message("环境变量读取完成:")
    log_message(f"  - LOGIN_COOKIE: {'已配置' if login_cookie else '未配置'} ({len(login_cookie)} 字符)")
    log_message(f"  - AUTH_COOKIE: {'已配置' if auth_cookie else '未配置'} ({len(auth_cookie)} 字符)")
    log_message(f"  - WXPUSHER_TOKEN: {'已配置' if wxpusher_token else '未配置'}")
    log_message(f"  - WXPUSHER_UID: {'已配置' if wxpusher_uid else '未配置'}")
    
    if not login_cookie:
        log_message("❌ 错误：LOGIN_COOKIE 未配置")
        send_wxpusher_notify(wxpusher_token, wxpusher_uid,
            "腾讯视频签到失败\n\nLOGIN_COOKIE 未配置", "签到失败：缺少配置")
        return
    
    # ========== 第一步：auth_refresh 获取新的 vqq_vusession ==========
    log_message("-" * 50)
    log_message("第一步：auth_refresh 刷新 session")
    log_message("-" * 50)
    
    millisecond_time = round(time.time() * 1000)
    
    # 从 login_cookie 中提取 auth_refresh 所需参数
    vqq_vuserid = extract_cookie_field(login_cookie, 'vqq_vuserid')
    vqq_openid = extract_cookie_field(login_cookie, 'vqq_openid')
    vqq_access_token = extract_cookie_field(login_cookie, 'vqq_access_token')
    vqq_vusession = extract_cookie_field(login_cookie, 'vqq_vusession')
    
    log_message(f"提取到的 Cookie 字段:")
    log_message(f"  - vqq_vuserid: {'有' if vqq_vuserid else '缺失'}")
    log_message(f"  - vqq_openid: {'有' if vqq_openid else '缺失'}")
    log_message(f"  - vqq_access_token: {'有' if vqq_access_token else '缺失'}")
    log_message(f"  - vqq_vusession: {'有' if vqq_vusession else '缺失'}")
    
    if not all([vqq_vuserid, vqq_openid, vqq_access_token]):
        log_message("❌ LOGIN_COOKIE 缺少必要字段（vqq_vuserid/vqq_openid/vqq_access_token）")
        log_message("💡 请重新获取 Cookie，确保在腾讯视频网页已登录状态下抓取")
        send_wxpusher_notify(wxpusher_token, wxpusher_uid,
            "腾讯视频签到失败\n\nCookie 缺少必要字段，请重新获取",
            "签到失败：Cookie不完整")
        return
    
    # 构建 auth_refresh 请求
    # 从 login_cookie 中提取 vappid 和 vsecret（如果有 auth_cookie 则使用）
    vappid = extract_cookie_field(login_cookie, 'vqq_appid') or ''
    vsecret = ''
    g_vstk = ''
    g_actk = ''
    
    # 如果有 auth_cookie，尝试从中提取参数
    if auth_cookie:
        log_message("检测到 AUTH_COOKIE，尝试提取认证参数...")
        # auth_refresh URL 可能包含在 auth_cookie 的来源中
        # 这里使用通用的 auth_refresh 接口
        pass
    
    # 使用 auth_refresh 接口刷新 session
    auth_refresh_url = (
        f"https://access.video.qq.com/user/auth_refresh"
        f"?vappid={vappid}"
        f"&vsecret={vsecret}"
        f"&type=qq"
        f"&g_tk="
        f"&g_vstk={g_vstk}"
        f"&g_actk={g_actk}"
        f"&_={millisecond_time}"
    )
    
    # 构建 auth_refresh 的 cookie（只需要关键字段）
    refresh_cookie = (
        f"main_login=qq; "
        f"vqq_vuserid={vqq_vuserid}; "
        f"vqq_openid={vqq_openid}; "
        f"vqq_access_token={vqq_access_token}; "
        f"vqq_vusession={vqq_vusession or ''}; "
    )
    
    refresh_headers = {
        'Referer': 'https://v.qq.com',
        'Cookie': refresh_cookie
    }
    
    log_message(f"请求 auth_refresh...")
    
    try:
        login_rsp = requests.get(url=auth_refresh_url, headers=refresh_headers, timeout=30)
        log_message(f"auth_refresh 状态码: {login_rsp.status_code}")
        
        login_rsp_cookie = requests.utils.dict_from_cookiejar(login_rsp.cookies)
        log_message(f"auth_refresh 返回的 Cookie: {login_rsp_cookie}")
        
        if login_rsp.status_code != 200 or not login_rsp_cookie:
            log_message(f"⚠️ auth_refresh 未返回新 Cookie，尝试直接签到...")
            new_vusession = vqq_vusession
        else:
            new_vusession = login_rsp_cookie.get('vqq_vusession', vqq_vusession or '')
            new_access_token = login_rsp_cookie.get('vqq_access_token', vqq_access_token)
            log_message(f"✅ 获取到新的 vqq_vusession: {new_vusession[:20]}...")
    except Exception as e:
        log_message(f"⚠️ auth_refresh 异常: {str(e)}，尝试直接签到...")
        new_vusession = vqq_vusession or ''
        new_access_token = vqq_access_token
    
    # ========== 第二步：使用新 session 签到 ==========
    log_message("-" * 50)
    log_message("第二步：执行签到")
    log_message("-" * 50)
    
    # 构建签到用的 cookie（auth_cookie 基础 + 新的 vusession）
    sign_cookie = auth_cookie.rstrip(';') + f';vqq_vusession={new_vusession};'
    
    # 如果 auth_cookie 为空，用 login_cookie 关键字段构建
    if not auth_cookie.strip():
        sign_cookie = (
            f"main_login=qq; "
            f"vqq_appid={vappid}; "
            f"vqq_openid={vqq_openid}; "
            f"vqq_access_token={new_access_token}; "
            f"vqq_vuserid={vqq_vuserid}; "
            f"vqq_refresh_token={extract_cookie_field(login_cookie, 'vqq_refresh_token') or ''}; "
            f"vqq_vusession={new_vusession}; "
        )
    
    sign_in_url = "https://vip.video.qq.com/fcgi-bin/comm_cgi?name=hierarchical_task_system&cmd=2"
    
    sign_headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; Mi Note 3 Build/OPM1.171019.019) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.128 '
                      'Mobile Safari/537.36 XiaoMi/MiuiBrowser/10.0.2',
        'Cookie': sign_cookie
    }
    
    log_message(f"签到 URL: {sign_in_url}")
    log_message(f"签到 Cookie 长度: {len(sign_cookie)} 字符")
    
    try:
        sign_rsp = requests.get(url=sign_in_url, headers=sign_headers, timeout=30)
        sign_rsp_text = sign_rsp.text
        
        log_message(f"签到状态码: {sign_rsp.status_code}")
        log_message(f"签到响应: {sign_rsp_text}")
        
        # 解析 QZOutputJson=({...});
        if 'QZOutputJson=' in sign_rsp_text:
            try:
                start_idx = sign_rsp_text.index('(') + 1
                end_idx = sign_rsp_text.rindex(')')
                json_str = sign_rsp_text[start_idx:end_idx]
                rsp_dict = json.loads(json_str)
                
                log_message(f"解析结果: {json.dumps(rsp_dict, ensure_ascii=False)}")
                
                ret = rsp_dict.get('ret')
                checkin_score = rsp_dict.get('checkin_score', 0)
                msg = rsp_dict.get('msg', '')
                
                if ret == 0:
                    result_msg = f"签到成功！获得 {checkin_score} V力值"
                    log_message(f"✅ {result_msg}")
                    send_wxpusher_notify(wxpusher_token, wxpusher_uid,
                        f"腾讯视频签到成功！\n\n获得积分：{checkin_score}\n签到时间：{time.strftime('%Y-%m-%d %H:%M:%S')}",
                        f"签到成功 +{checkin_score}分")
                        
                elif ret == -10006:
                    result_msg = "签到失败：Cookie 无效或已过期 (Account Verify Error)"
                    log_message(f"❌ {result_msg}")
                    send_wxpusher_notify(wxpusher_token, wxpusher_uid,
                        f"腾讯视频签到失败\n\n{result_msg}\n\n请重新获取 Cookie",
                        "签到失败：Cookie失效")
                        
                elif ret == -110009:
                    security_info = rsp_dict.get('security_verify', {})
                    user_msg = security_info.get('usermg', '需要图形验证')
                    result_msg = f"签到失败：安全验证未通过 - {user_msg}"
                    log_message(f"❌ {result_msg}")
                    log_message("💡 解决方案：请在手机腾讯视频APP中手动签到一次，通过图形验证后重新获取 Cookie")
                    send_wxpusher_notify(wxpusher_token, wxpusher_uid,
                        f"腾讯视频签到失败\n\n{result_msg}\n\n解决方案：\n1. 打开手机腾讯视频APP\n2. 手动签到一次（完成图形验证）\n3. 重新抓取 Cookie 并更新 Secrets",
                        "签到失败：需要验证")
                else:
                    result_msg = f"签到失败：未知错误 (ret={ret}, msg={msg})"
                    log_message(f"❌ {result_msg}")
                    send_wxpusher_notify(wxpusher_token, wxpusher_uid,
                        f"腾讯视频签到失败\n\n{result_msg}",
                        "签到失败")
            except (ValueError, json.JSONDecodeError) as e:
                log_message(f"❌ 响应解析失败: {str(e)}")
                log_message(f"原始响应: {sign_rsp_text}")
        else:
            # 可能是新的接口格式，尝试直接解析 JSON
            log_message("⚠️ 响应不是 QZOutputJson 格式，尝试直接解析 JSON...")
            try:
                rsp_dict = sign_rsp.json()
                log_message(f"JSON 响应: {json.dumps(rsp_dict, ensure_ascii=False)}")
                
                ret = rsp_dict.get('ret')
                checkin_score = rsp_dict.get('check_in_score', 0)
                msg = rsp_dict.get('msg', '')
                
                if ret == 0:
                    result_msg = f"签到成功！获得 {checkin_score} V力值"
                    log_message(f"✅ {result_msg}")
                    send_wxpusher_notify(wxpusher_token, wxpusher_uid,
                        f"腾讯视频签到成功！\n\n获得积分：{checkin_score}\n签到时间：{time.strftime('%Y-%m-%d %H:%M:%S')}",
                        f"签到成功 +{checkin_score}分")
                else:
                    result_msg = f"签到失败 (ret={ret}, msg={msg})"
                    log_message(f"❌ {result_msg}")
                    send_wxpusher_notify(wxpusher_token, wxpusher_uid,
                        f"腾讯视频签到失败\n\n{result_msg}",
                        "签到失败")
            except:
                log_message(f"❌ 无法解析响应: {sign_rsp_text[:500]}")
                
    except requests.RequestException as e:
        error_msg = f"网络请求异常: {str(e)}"
        log_message(f"❌ {error_msg}")
        send_wxpusher_notify(wxpusher_token, wxpusher_uid,
            f"腾讯视频签到异常\n\n{error_msg}", "签到异常")
    except Exception as e:
        error_msg = f"程序异常: {str(e)}"
        log_message(f"❌ {error_msg}")
        import traceback
        log_message(f"错误堆栈: {traceback.format_exc()}")
        send_wxpusher_notify(wxpusher_token, wxpusher_uid,
            f"腾讯视频签到异常\n\n{error_msg}", "签到异常")
    
    log_message("=" * 50)
    log_message("签到流程结束")
    log_message("=" * 50)

if __name__ == '__main__':
    tencent_video_sign_in()
    log_message("程序即将退出...")
    time.sleep(2)
