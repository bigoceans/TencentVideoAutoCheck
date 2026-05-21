import requests
import requests.utils
import time
import json
import os
import sys

# 强制刷新输出，确保日志实时写入
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
    
    # 检查是否包含必要的字段
    required_fields = ['pgv_pvid', 'vqq_vusession', 'vqq_access_token']
    missing_fields = []
    
    for field in required_fields:
        if field not in cookie:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"{name} 缺少必要字段: {', '.join(missing_fields)}"
    
    # 检查 Cookie 长度（通常应该比较长）
    if len(cookie) < 100:
        return False, f"{name} 长度异常（{len(cookie)} 字符），可能不完整"
    
    return True, f"{name} 格式正常"

def tencent_video_sign_in():
    log_message("=" * 50)
    log_message("腾讯视频自动签到开始")
    log_message("=" * 50)
    
    millisecond_time = round(time.time() * 1000)
    
    # 从环境变量获取配置
    login_cookie = os.getenv('LOGIN_COOKIE', '').strip()
    auth_cookie = os.getenv('AUTH_COOKIE', '').strip()
    wxpusher_token = os.getenv('WXPUSHER_TOKEN', '').strip()
    wxpusher_uid = os.getenv('WXPUSHER_UID', '').strip()
    
    log_message(f"环境变量读取完成:")
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
    
    # 测试 Cookie 是否有效（访问用户信息接口）
    log_message("正在测试 Cookie 有效性...")
    test_url = "https://vip.video.qq.com/fcgi-bin/comm_cgi?name=hierarchical_task_system&cmd=2"
    test_headers = {
        'Referer': 'https://v.qq.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cookie': login_cookie
    }
    
    try:
        test_rsp = requests.get(test_url, headers=test_headers, timeout=30)
        log_message(f"测试请求状态码: {test_rsp.status_code}")
        log_message(f"测试响应: {test_rsp.text[:200]}...")  # 只显示前200字符
        
        # 检查是否包含登录页面重定向（未登录）
        if 'login' in test_rsp.text.lower() or '登录' in test_rsp.text:
            error_msg = "Cookie 已失效，需要重新登录获取"
            log_message(f"错误: {error_msg}")
            
            if wxpusher_token and wxpusher_uid:
                send_wxpusher_message(
                    wxpusher_token,
                    f"腾讯视频签到失败\n\n{error_msg}\n\n请重新获取 Cookie",
                    wxpusher_uid,
                    "签到失败：Cookie失效"
                )
            return
        
    except Exception as e:
        log_message(f"测试请求异常: {str(e)}")
    
    # 执行签到
    log_message("=" * 50)
    log_message("开始执行签到...")
    log_message("=" * 50)
    
    sign_in_url = f"https://vip.video.qq.com/fcgi-bin/comm_cgi?name=hierarchical_task_system&cmd=2&_={millisecond_time}"
    
    try:
        log_message(f"请求 URL: {sign_in_url}")
        log_message(f"请求 Headers: Referer={test_headers['Referer']}")
        log_message(f"请求 Cookie 长度: {len(login_cookie)} 字符")
        
        sign_rsp = requests.get(url=sign_in_url, headers=test_headers, timeout=30)
        sign_rsp_text = sign_rsp.text
        
        log_message(f"响应状态码: {sign_rsp.status_code}")
        log_message(f"响应内容: {sign_rsp_text}")
        
        # 解析响应
        if 'QZOutputJson=' in sign_rsp_text:
            try:
                start_idx = sign_rsp_text.find('(') + 1
                end_idx = sign_rsp_text.rfind(')')
                json_str = sign_rsp_text[start_idx:end_idx]
                rsp_dict = json.loads(json_str)
                
                log_message(f"解析后的响应: {json.dumps(rsp_dict, ensure_ascii=False)}")
                
                ret = rsp_dict.get('ret')
                checkin_score = rsp_dict.get('checkin_score', 0)
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
        else:
            log_message(f"⚠️ 响应格式异常，不包含 QZOutputJson: {sign_rsp_text[:500]}")
            
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
