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
        else:
            log_message(f"WxPusher: 推送失败 - {result.get('msg', '未知错误')}")
        return result
    except Exception as e:
        log_message(f"WxPusher: 推送异常 - {str(e)}")
        return None

def notify(wxpusher_token, wxpusher_uid, content, summary):
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
    auth_refresh_url = os.getenv('AUTH_REFRESH_URL', '').strip()
    wxpusher_token = os.getenv('WXPUSHER_TOKEN', '').strip()
    wxpusher_uid = os.getenv('WXPUSHER_UID', '').strip()
    
    log_message("环境变量读取完成:")
    log_message(f"  - LOGIN_COOKIE: {'已配置' if login_cookie else '未配置'} ({len(login_cookie)} 字符)")
    log_message(f"  - AUTH_REFRESH_URL: {'已配置' if auth_refresh_url else '未配置'} ({len(auth_refresh_url)} 字符)")
    log_message(f"  - WXPUSHER_TOKEN: {'已配置' if wxpusher_token else '未配置'}")
    log_message(f"  - WXPUSHER_UID: {'已配置' if wxpusher_uid else '未配置'}")
    
    if not login_cookie:
        log_message("❌ 错误：LOGIN_COOKIE 未配置")
        notify(wxpusher_token, wxpusher_uid, "腾讯视频签到失败\n\nLOGIN_COOKIE 未配置", "签到失败")
        return
    
    # ========== 第一步：auth_refresh 获取新的 vqq_vusession ==========
    log_message("-" * 50)
    log_message("第一步：auth_refresh 刷新 session")
    log_message("-" * 50)
    
    # 从 login_cookie 中提取关键字段
    vqq_vuserid = extract_cookie_field(login_cookie, 'vqq_vuserid')
    vqq_openid = extract_cookie_field(login_cookie, 'vqq_openid')
    vqq_access_token = extract_cookie_field(login_cookie, 'vqq_access_token')
    vqq_vusession = extract_cookie_field(login_cookie, 'vqq_vusession')
    
    log_message(f"Cookie 字段检查:")
    log_message(f"  - vqq_vuserid: {'✅' if vqq_vuserid else '❌ 缺失'}")
    log_message(f"  - vqq_openid: {'✅' if vqq_openid else '❌ 缺失'}")
    log_message(f"  - vqq_access_token: {'✅' if vqq_access_token else '❌ 缺失'}")
    log_message(f"  - vqq_vusession: {'✅' if vqq_vusession else '❌ 缺失'}")
    
    if not all([vqq_vuserid, vqq_openid, vqq_access_token]):
        log_message("❌ LOGIN_COOKIE 缺少必要字段")
        log_message("💡 获取方法：浏览器登录 v.qq.com → F12 → Network → 找到任意 v.qq.com 请求 → 复制 Cookie")
        notify(wxpusher_token, wxpusher_uid,
            "腾讯视频签到失败\n\nCookie 缺少必要字段\n\n获取方法：\n1. 浏览器登录 v.qq.com\n2. F12 打开开发者工具\n3. 切换到 Network 标签\n4. 刷新页面\n5. 找到任意 v.qq.com 请求\n6. 复制 Request Headers 中的完整 Cookie",
            "签到失败：Cookie不完整")
        return
    
    # 构建 auth_refresh 请求
    # 优先使用 AUTH_REFRESH_URL（包含完整的 vappid/vsecret/g_vstk/g_actk）
    if auth_refresh_url:
        log_message("使用 AUTH_REFRESH_URL（推荐方式）")
        refresh_url = auth_refresh_url
        # 添加时间戳防缓存
        if '?' in refresh_url:
            refresh_url += f"&_={round(time.time() * 1000)}"
        else:
            refresh_url += f"?_={round(time.time() * 1000)}"
    else:
        log_message("⚠️ 未配置 AUTH_REFRESH_URL，使用简化方式（可能失败）")
        vqq_appid = extract_cookie_field(login_cookie, 'vqq_appid') or ''
        refresh_url = (
            f"https://access.video.qq.com/user/auth_refresh"
            f"?vappid={vqq_appid}&vsecret=&type=qq&g_tk=&g_vstk=&g_actk="
            f"&_={round(time.time() * 1000)}"
        )
    
    # 构建 auth_refresh 的 cookie
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
    
    new_vusession = vqq_vusession or ''
    new_access_token = vqq_access_token
    
    try:
        login_rsp = requests.get(url=refresh_url, headers=refresh_headers, timeout=30)
        log_message(f"auth_refresh 状态码: {login_rsp.status_code}")
        
        if login_rsp.status_code == 401:
            log_message("❌ auth_refresh 返回 401，认证参数无效")
            log_message("💡 解决方案：请配置 AUTH_REFRESH_URL 环境变量")
            log_message("   获取方法：浏览器 F12 → Network → 搜索 auth_refresh → 复制完整 URL")
            notify(wxpusher_token, wxpusher_uid,
                "腾讯视频签到失败\n\nauth_refresh 返回 401\n\n请配置 AUTH_REFRESH_URL：\n1. 浏览器登录 v.qq.com\n2. F12 → Network\n3. 搜索 auth_refresh\n4. 复制完整的 Request URL\n5. 添加到 Secrets: AUTH_REFRESH_URL",
                "签到失败：需要AUTH_REFRESH_URL")
            return
        
        login_rsp_cookie = requests.utils.dict_from_cookiejar(login_rsp.cookies)
        log_message(f"auth_refresh 返回的 Cookie: {login_rsp_cookie}")
        
        if login_rsp.status_code == 200 and login_rsp_cookie:
            new_vusession = login_rsp_cookie.get('vqq_vusession', vqq_vusession or '')
            new_access_token = login_rsp_cookie.get('vqq_access_token', vqq_access_token)
            log_message(f"✅ 获取到新的 vqq_vusession: {new_vusession[:20]}...")
        else:
            log_message(f"⚠️ auth_refresh 未返回新 Cookie (状态码: {login_rsp.status_code})，使用原始 Cookie 继续")
    except Exception as e:
        log_message(f"⚠️ auth_refresh 异常: {str(e)}，使用原始 Cookie 继续")
    
    # ========== 第二步：使用新 session 签到 ==========
    log_message("-" * 50)
    log_message("第二步：执行签到")
    log_message("-" * 50)
    
    # 构建签到用的完整 cookie
    sign_cookie = (
        f"main_login=qq; "
        f"vqq_appid={extract_cookie_field(login_cookie, 'vqq_appid') or ''}; "
        f"vqq_openid={vqq_openid}; "
        f"vqq_access_token={new_access_token}; "
        f"vqq_vuserid={vqq_vuserid}; "
        f"vqq_refresh_token={extract_cookie_field(login_cookie, 'vqq_refresh_token') or ''}; "
        f"vqq_vusession={new_vusession}; "
    )
    
    mobile_ua = ('Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; Mi Note 3 Build/OPM1.171019.019) '
                 'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.128 '
                 'Mobile Safari/537.36 XiaoMi/MiuiBrowser/10.0.2')
    
    # 获取用户信息和V力值（用于展示）
    try:
        info_url = 'https://vip.video.qq.com/fcgi-bin/comm_cgi?name=spp_vscore_user_mashup&type=1&otype=xjson'
        info_headers = {
            'User-Agent': mobile_ua,
            'Cookie': sign_cookie
        }
        info_rsp = requests.get(info_url, headers=info_headers, timeout=30)
        if info_rsp.status_code == 200:
            info_data = info_rsp.json()
            if info_data.get('ret') == 0:
                score_info = info_data.get('cscore_info', {})
                vscore_total = score_info.get('vip_score_total', 0)
                level_info = info_data.get('lscore_info', {})
                level = level_info.get('level', 0)
                log_message(f"用户信息: V力值总计={vscore_total}, 会员等级=V{level}")
    except Exception as e:
        log_message(f"⚠️ 获取用户信息失败: {e}")
    
    # 尝试多个签到接口
    sign_urls = [
        {
            'url': 'https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/CheckIn?rpc_data=%7B%7D',
            'headers': {
                'Referer': 'https://film.video.qq.com',
                'Origin': 'https://film.video.qq.com',
                'User-Agent': mobile_ua,
                'Accept': 'application/json, text/plain, */*',
                'Cookie': sign_cookie
            },
            'name': 'trpc CheckIn',
            'parse_mode': 'json'
        },
        {
            'url': 'https://vip.video.qq.com/fcgi-bin/comm_cgi?name=hierarchical_task_system&cmd=2',
            'headers': {
                'User-Agent': mobile_ua,
                'Cookie': sign_cookie
            },
            'name': 'hierarchical_task_system',
            'parse_mode': 'qzoutput'
        }
    ]
    
    sign_success = False
    
    for api_info in sign_urls:
        log_message(f"尝试 {api_info['name']}: {api_info['url']}")
        
        try:
            sign_rsp = requests.get(url=api_info['url'], headers=api_info['headers'], timeout=30)
            sign_rsp_text = sign_rsp.text
            
            log_message(f"  状态码: {sign_rsp.status_code}")
            log_message(f"  响应: {sign_rsp_text[:300]}")
            
            rsp_dict = None
            
            if api_info['parse_mode'] == 'qzoutput' and 'QZOutputJson=' in sign_rsp_text:
                try:
                    start_idx = sign_rsp_text.index('(') + 1
                    end_idx = sign_rsp_text.rindex(')')
                    rsp_dict = json.loads(sign_rsp_text[start_idx:end_idx])
                except (ValueError, json.JSONDecodeError):
                    pass
            else:
                try:
                    rsp_dict = sign_rsp.json()
                except:
                    pass
            
            if rsp_dict:
                log_message(f"  解析结果: {json.dumps(rsp_dict, ensure_ascii=False)}")
                
                # 获取返回码，兼容多种格式
                ret = rsp_dict.get('ret')
                if ret is None:
                    ret = rsp_dict.get('code')
                
                # 获取积分，兼容多种格式
                checkin_score = rsp_dict.get('check_in_score') or rsp_dict.get('checkin_score', 0)
                if checkin_score == 0 and 'data' in rsp_dict:
                    data = rsp_dict.get('data', {})
                    checkin_score = data.get('check_in_score') or data.get('checkin_score', 0)
                
                msg = rsp_dict.get('msg', '')
                
                # 处理成功响应
                if ret == 0:
                    result_msg = f"签到成功！获得 {checkin_score} V力值"
                    log_message(f"✅ {result_msg}")
                    notify(wxpusher_token, wxpusher_uid,
                        f"腾讯视频签到成功！\n\n获得积分：{checkin_score}\n签到时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n使用接口：{api_info['name']}",
                        f"签到成功 +{checkin_score}分")
                    sign_success = True
                    break
                
                # 处理错误响应
                if ret:
                    if ret == -10006 or str(ret) == "-10006":
                        result_msg = "Cookie 无效或已过期 (Account Verify Error)"
                        log_message(f"❌ {result_msg}")
                        notify(wxpusher_token, wxpusher_uid,
                            f"腾讯视频签到失败\n\n{result_msg}\n\n请重新获取 Cookie",
                            "签到失败：Cookie失效")
                        break
                        
                    elif ret == -110009 or str(ret) == "-110009":
                        security_info = rsp_dict.get('security_verify', {})
                        user_msg = security_info.get('usermg', security_info.get('userMsg', '需要图形验证'))
                        result_msg = f"安全验证未通过 - {user_msg}"
                        log_message(f"❌ {result_msg}")
                        log_message("💡 解决方案：请在手机腾讯视频APP中手动签到一次，通过图形验证后重新获取 Cookie")
                        notify(wxpusher_token, wxpusher_uid,
                            f"腾讯视频签到失败\n\n{result_msg}\n\n解决方案：\n1. 打开手机腾讯视频APP\n2. 手动签到一次（完成图形验证）\n3. 重新抓取 Cookie 和 AUTH_REFRESH_URL",
                            "签到失败：需要验证")
                        break
                        
                    elif ret == -10 or str(ret) == "-10" or 'no match route' in str(msg):
                        log_message(f"  ⚠️ 接口已失效，尝试下一个...")
                        continue
                    else:
                        result_msg = f"未知错误 (ret={ret}, msg={msg})"
                        log_message(f"❌ {result_msg}")
                        # 如果不是严重错误，尝试下一个接口
                        if str(ret) == "-10":
                            continue
                        notify(wxpusher_token, wxpusher_uid,
                            f"腾讯视频签到失败\n\n{result_msg}",
                            "签到失败")
                        break
            else:
                log_message(f"  ⚠️ 无法解析响应，尝试下一个接口...")
                continue
                
        except requests.RequestException as e:
            log_message(f"  ⚠️ 请求异常: {str(e)}，尝试下一个接口...")
            continue
    
    if not sign_success:
        log_message("❌ 所有签到接口均失败")
        notify(wxpusher_token, wxpusher_uid,
            "腾讯视频签到失败\n\n所有接口均失败\n\n建议：\n1. 配置 AUTH_REFRESH_URL\n2. 重新获取 Cookie\n3. 在手机APP手动签到一次",
            "签到失败")
    
    log_message("=" * 50)
    log_message("签到流程结束")
    log_message("=" * 50)

if __name__ == '__main__':
    tencent_video_sign_in()
    log_message("程序即将退出...")
    time.sleep(2)
