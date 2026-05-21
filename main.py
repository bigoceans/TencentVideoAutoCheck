import requests
import requests.utils
import time
import json
import os

def send_wxpusher_message(app_token, content, uids, summary=None):
    """
    使用 WxPusher 发送消息
    """
    if not app_token or not uids:
        print("WxPusher: 未配置 AppToken 或 UID，跳过推送")
        return None
    
    api_url = 'https://wxpusher.zjiecode.com/api/send/message'
    headers = {
        'Content-Type': 'application/json'
    }
    
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
            print(f"WxPusher: 消息推送成功")
            return result
        else:
            print(f"WxPusher: 推送失败 - {result.get('msg', '未知错误')}")
            return result
            
    except Exception as e:
        print(f"WxPusher: 推送异常 - {str(e)}")
        return None


def tencent_video_sign_in():
    millisecond_time = round(time.time() * 1000)
    
    # 从环境变量获取配置
    login_cookie = os.getenv('LOGIN_COOKIE')
    auth_cookie = os.getenv('AUTH_COOKIE')
    
    # WxPusher 配置（可选）
    wxpusher_token = os.getenv('WXPUSHER_TOKEN', '')
    wxpusher_uid = os.getenv('WXPUSHER_UID', '')
    
    # 检查必要的环境变量
    if not login_cookie or not auth_cookie:
        error_msg = "错误：请配置 LOGIN_COOKIE 和 AUTH_COOKIE 环境变量"
        print(error_msg)
        
        if wxpusher_token and wxpusher_uid:
            send_wxpusher_message(
                wxpusher_token,
                f"腾讯视频签到失败\n\n{error_msg}",
                wxpusher_uid,
                "签到失败：缺少配置"
            )
        return
    
    # 使用旧的签到接口（更稳定）
    sign_in_url = f"https://vip.video.qq.com/fcgi-bin/comm_cgi?name=hierarchical_task_system&cmd=2&_={millisecond_time}"
    
    sign_headers = {
        'Referer': 'https://v.qq.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cookie': login_cookie
    }
    
    try:
        print(f"正在签到...")
        sign_rsp = requests.get(url=sign_in_url, headers=sign_headers, timeout=30)
        sign_rsp_text = sign_rsp.text
        
        print(f"签到响应: {sign_rsp_text}")
        
        # 解析响应 QZOutputJson=({"ret": 0, "checkin_score": 5, "msg": "OK"});
        if 'QZOutputJson=' in sign_rsp_text:
            start_idx = sign_rsp_text.find('(') + 1
            end_idx = sign_rsp_text.rfind(')')
            json_str = sign_rsp_text[start_idx:end_idx]
            rsp_dict = json.loads(json_str)
            
            ret = rsp_dict.get('ret')
            checkin_score = rsp_dict.get('checkin_score', 0)
            msg = rsp_dict.get('msg', '')
            
            if ret == 0:
                result_msg = f"签到成功！获得 {checkin_score} V力值"
                print(result_msg)
                
                if wxpusher_token and wxpusher_uid:
                    push_content = f"腾讯视频签到成功！\n\n获得积分：{checkin_score}\n签到时间：{time.strftime('%Y-%m-%d %H:%M:%S')}"
                    send_wxpusher_message(
                        wxpusher_token,
                        push_content,
                        wxpusher_uid,
                        f"签到成功 +{checkin_score}分"
                    )
            elif ret == -10006:
                result_msg = "签到失败：Cookie 无效或已过期"
                print(result_msg)
                
                if wxpusher_token and wxpusher_uid:
                    send_wxpusher_message(
                        wxpusher_token,
                        f"腾讯视频签到失败\n\n{result_msg}\n请重新获取 Cookie",
                        wxpusher_uid,
                        "签到失败：Cookie失效"
                    )
            else:
                result_msg = f"签到失败：未知错误 (ret={ret}, msg={msg})"
                print(result_msg)
                
                if wxpusher_token and wxpusher_uid:
                    send_wxpusher_message(
                        wxpusher_token,
                        f"腾讯视频签到失败\n\n{result_msg}",
                        wxpusher_uid,
                        "签到失败"
                    )
        else:
            print(f"响应格式异常: {sign_rsp_text}")
            
    except requests.RequestException as e:
        error_msg = f"网络请求异常: {str(e)}"
        print(error_msg)
        
        if wxpusher_token and wxpusher_uid:
            send_wxpusher_message(
                wxpusher_token,
                f"腾讯视频签到异常\n\n{error_msg}",
                wxpusher_uid,
                "签到异常"
            )
            
    except Exception as e:
        error_msg = f"程序异常: {str(e)}"
        print(error_msg)
        
        if wxpusher_token and wxpusher_uid:
            send_wxpusher_message(
                wxpusher_token,
                f"腾讯视频签到异常\n\n{error_msg}",
                wxpusher_uid,
                "签到异常"
            )


if __name__ == '__main__':
    tencent_video_sign_in()
    print("10秒后自动关闭")
    time.sleep(10)
