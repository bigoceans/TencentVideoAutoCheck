import requests
import requests.utils
import time
import json
import os
import sys

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

def validate_cookie(cookie, name):
    """验证 Cookie 格式"""
    if not cookie:
        return False, f"{name} 为空"
    
    required_fields = ['pgv_pvid', 'vqq_vusession', 'vqq_access_token']
    missing_fields = []
    
    for field in required_fields:
        if field not in cookie:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"{name} 缺少必要字段: {', '.join(missing_fields)}"
    
    if len(cookie) < 100:
        return False, f"{name} 长度异常（{len(cookie)} 字符），可能不完整"
    
    return True, f"{name} 格式正常"

def refresh_session(login_cookie):
    """
    刷新 vqq_vusession，解决 security check 问题
    使用 NewRefresh 接口获取新的 session
    """
    log_message("正在刷新 session（解决图形验证问题）...")
    
    refresh_url = "https://pbaccess.video.qq.com/trpc.video_account_login.web_login_trpc.WebLoginTrpc/NewRefresh"
    
    refresh_headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'text/plain;charset=utf-8',
        'Origin': 'https://v.qq.com',
        'Referer': 'https://v.qq.com/',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 15; 23127PN0CC Build/AQ3A.240627.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.86 Mobile Safari/537.36 QQLiveBrowser/9.01.01.29867',
        'Cookie': login_cookie
    }
    
    # 从 login_cookie 中提取构建 refresh body 所需的参数
    refresh_body = '{"type":"qq","si":{"q36":"","h38":"","o_data":"","s":""}}'
    
    try:
        rsp = requests.post(refresh_url, headers=refresh_headers, data=refresh_body, timeout=30)
        log_message(f"NewRefresh 状态码: {rsp.status_code}")
        log_message(f"NewRefresh 响应: {rsp.text[:500]}")
        
        if rsp.status_code == 200:
            try:
                data = rsp.json()
                # 尝试提取新的 vusession
                vusession = None
                if 'data' in data:
                    vusession = data['data'].get('vusession')
                elif 'vusession' in str(data):
                    # 尝试从响应中提取
                    import re
                    match = re.search(r'vusession["\s:]+([^",}]+)', rsp.text)
                    if match:
                        vusession = match.group(1)
                
                if vusession:
                    log_message(f"✅ 获取到新的 vusession: {vusession[:20]}...")
                    # 替换 cookie 中的 vusession
                    import re
                    new_cookie = re.sub(r'vqq_vusession=[^;]*', f'vqq_vusession={vusession}', login_cookie)
                    return new_cookie
                else:
                    log_message("⚠️ 未能提取新 vusession，使用原始 Cookie 继续")
                    return login_cookie
            except json.JSONDecodeError:
                log_message("⚠️ NewRefresh 响应非 JSON，使用原始 Cookie 继续")
                return login_cookie
        else:
            log_message(f"⚠️ NewRefresh 请求失败，使用原始 Cookie 继续")
            return login_cookie
            
    except Exception as e:
        log_message(f"⚠️ NewRefresh 异常: {str(e)}，使用原始 Cookie 继续")
        return login_cookie

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
    
    # 验证 LOGIN_COOKIE
    is_valid, msg = validate_cookie(login_cookie, "LOGIN_COOKIE")
    log_message(f"Cookie 验证: {msg}")
    
    if not is_valid:
        error_msg = f"Cookie 验证失败: {msg}"
        log_message(f"错误: {error_msg}")
        
        if wxpusher_token and wxpusher_uid:
            send_wxpusher_message(
                wxpusher_token,
                f"腾讯视频签到失败\n\n{error_msg}\n\n请检查 Secrets 配置",
                wxpusher_uid,
                "签到失败：Cookie无效"
            )
        return
    
    # 刷新 session
    log_message("-" * 50)
    refreshed_cookie = refresh_session(login_cookie)
    if refreshed_cookie != login_cookie:
        log_message("✅ Cookie 已刷新，使用新 Cookie 签到")
    else:
        log_message("使用原始 Cookie 签到")
    
    # 执行签到
    log_message("=" * 50)
    log_message("开始执行签到...")
    log_message("=" * 50)
    
    sign_in_url = "https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/CheckIn?rpc_data=%7B%7D"
    
    sign_headers = {
        'Referer': 'https://film.video.qq.com',
        'Origin': 'https://film.video.qq.com',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 QQLiveBrowser/8.8.10 AppType/HD WebKitCore/WKWebView iOS',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': refreshed_cookie
    }
    
    try:
        log_message(f"请求 URL: {sign_in_url}")
        log_message(f"请求 Cookie 长度: {len(refreshed_cookie)} 字符")
        
        sign_rsp = requests.get(url=sign_in_url, headers=sign_headers, timeout=30)
        sign_rsp_text = sign_rsp.text
        
        log_message(f"响应状态码: {sign_rsp.status_code}")
        log_message(f"响应内容: {sign_rsp_text}")
        
        # 解析响应
        try:
            rsp_dict = sign_rsp.json()
            
            log_message(f"解析后的响应: {json.dumps(rsp_dict, ensure_ascii=False)}")
            
            ret = rsp_dict.get('ret')
            checkin_score = rsp_dict.get('check_in_score', 0)
            msg = rsp_dict.get('msg', '')
            
            if ret == 0:
                result_msg = f"签到成功！获得 {checkin_score} V力值"
                log_message(f"✅ {result_msg}")
                
                if wxpusher_token and wxpusher_uid:
                    push_content = f"腾讯视频签到成功！\n\n获得积分：{checkin_score}\n签到时间：{time.strftime('%Y-%m-%d %H:%M:%S')}"
                    send_wxpusher_message(
                        wxpusher_token,
                        push_content,
                        wxpusher_uid,
                        f"签到成功 +{checkin_score}分"
                    )
                    
            elif ret == -110009:
                # security check not pass - 图形验证
                security_info = rsp_dict.get('security_verify', {})
                user_msg = security_info.get('usermg', '需要图形验证')
                result_msg = f"签到失败：安全验证未通过 - {user_msg}"
                log_message(f"❌ {result_msg}")
                log_message("💡 解决方案：请在手机腾讯视频APP中手动签到一次，通过图形验证后重新获取 Cookie")
                
                if wxpusher_token and wxpusher_uid:
                    send_wxpusher_message(
                        wxpusher_token,
                        f"腾讯视频签到失败\n\n{result_msg}\n\n解决方案：\n1. 打开手机腾讯视频APP\n2. 手动签到一次（完成图形验证）\n3. 重新抓取 Cookie 并更新 Secrets",
                        wxpusher_uid,
                        "签到失败：需要验证"
                    )
                    
            elif ret == -10006:
                result_msg = "签到失败：Cookie 无效或已过期 (Account Verify Error)"
                log_message(f"❌ {result_msg}")
                
                if wxpusher_token and wxpusher_uid:
                    send_wxpusher_message(
                        wxpusher_token,
                        f"腾讯视频签到失败\n\n{result_msg}\n\n请重新获取 Cookie",
                        wxpusher_uid,
                        "签到失败：Cookie失效"
                    )
            else:
                result_msg = f"签到失败：未知错误 (ret={ret}, msg={msg})"
                log_message(f"❌ {result_msg}")
                
                if wxpusher_token and wxpusher_uid:
                    send_wxpusher_message(
                        wxpusher_token,
                        f"腾讯视频签到失败\n\n{result_msg}",
                        wxpusher_uid,
                        "签到失败"
                    )
        except json.JSONDecodeError as e:
            error_msg = f"JSON 解析失败: {str(e)}"
            log_message(f"❌ {error_msg}")
            log_message(f"原始响应: {sign_rsp_text}")
            
    except requests.RequestException as e:
        error_msg = f"网络请求异常: {str(e)}"
        log_message(f"❌ {error_msg}")
        
        if wxpusher_token and wxpusher_uid:
            send_wxpusher_message(
                wxpusher_token,
                f"腾讯视频签到异常\n\n{error_msg}",
                wxpusher_uid,
                "签到异常"
            )
    except Exception as e:
        error_msg = f"程序异常: {str(e)}"
        log_message(f"❌ {error_msg}")
        import traceback
        log_message(f"错误堆栈: {traceback.format_exc()}")
        
        if wxpusher_token and wxpusher_uid:
            send_wxpusher_message(
                wxpusher_token,
                f"腾讯视频签到异常\n\n{error_msg}",
                wxpusher_uid,
                "签到异常"
            )
    
    log_message("=" * 50)
    log_message("签到流程结束")
    log_message("=" * 50)

if __name__ == '__main__':
    tencent_video_sign_in()
    log_message("程序即将退出...")
    time.sleep(2)
