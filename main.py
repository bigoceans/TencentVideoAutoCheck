import requests
import requests.utils
import time
import json
import os
from urllib.parse import quote

def send_wxpusher_message(app_token, content, uids, summary=None):
    """
    使用 WxPusher 发送消息
    
    参数:
        app_token: WxPusher 应用的 AppToken
        content: 消息内容
        uids: 接收消息的用户 UID 列表，如 ["UID_xxxxxxxxxxxxxxxx"]
        summary: 消息摘要（可选），显示在微信通知栏
    
    返回:
        dict: API 响应结果
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
        "contentType": 1,  # 1=纯文本, 2=HTML, 3=Markdown
        "uids": uids if isinstance(uids, list) else [uids]
    }
    
    # 如果提供了摘要，添加到请求中
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
        
        # 发送错误通知（如果配置了 WxPusher）
        if wxpusher_token and wxpusher_uid:
            send_wxpusher_message(
                wxpusher_token,
                f"腾讯视频签到失败\n\n{error_msg}",
                wxpusher_uid,
                "签到失败：缺少配置"
            )
        return
    
    # 认证刷新 URL（需要替换 XX 为实际值）
    login_url = "https://access.video.qq.com/user/auth_refresh?vappid=XX&vsecret=XX&type=qq&g_tk=&g_vstk=XX&g_actk=XX"
    
    login_headers = {
        'Referer': 'https://v.qq.com',
        'Cookie': login_cookie
    }
    
    try:
        # 发送认证刷新请求
        login_rsp = requests.get(url=login_url, headers=login_headers, timeout=30)
        print(f"认证刷新响应: {login_rsp.status_code}")
        
        login_rsp_cookie = requests.utils.dict_from_cookiejar(login_rsp.cookies)
        
        if login_rsp.status_code == 200 and login_rsp_cookie:
            # 构建新的 auth_cookie
            auth_cookie = auth_cookie + 'vqq_vusession=' + login_rsp_cookie['vqq_vusession'] + ';' + \
                         'vqq_access_token=' + login_rsp_cookie['vqq_access_token'] + ';' + \
                         'vqq_appid=' + login_rsp_cookie['vqq_appid'] + ';' + \
                         'vqq_openid=' + login_rsp_cookie['vqq_openid'] + ';' + \
                         'vqq_refresh_token=' + login_rsp_cookie['vqq_refresh_token'] + ';' + \
                         'vqq_vuserid=' + login_rsp_cookie['vqq_vuserid'] + ';'
            
            print(f"构建的 Cookie: {auth_cookie[:100]}...")
            
            # 签到请求
            sign_in_url = "https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/CheckIn?rpc_data={}"
            referer = 'https://film.video.qq.com/x/grade/?ovscroll=0&ptag=Vgrade.card&source=page_id=default&ztid=default&pgid=page_personal_center&page_type=personal&is_interactive_flag=1&pg_clck_flag=1&styletype=201&mod_id=sp_mycntr_vip&sectiontype=2&business=hollywood&layouttype=1000&section_idx=0&mod_title=会员资产&blocktype=6001&vip_id=userCenter_viplevel_entry&mod_idx=11&item_idx=4&eid=button_mycntr&action_pos=jump&hidetitlebar=1&isFromJump=1&isDarkMode=1&uiType=HUGE'
            referer = referer.encode("utf-8").decode("latin1")
            
            sign_headers = {
                'Referer': referer,
                'Host': 'vip.video.qq.com',
                'Origin': 'https://film.video.qq.com',
                'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 16_2 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Mobile/11A465 QQLiveBrowser/8.8.10 AppType/HD WebKitCore/WKWebView iOS GDTTangramMobSDK/4.370.6 GDTMobSDK/4.370.6 cellPhone/Unknown iPad AppBuild/25828',
                'Accept-Encoding': 'gzip, deflate, br',
                "Cookie": auth_cookie
            }
            
            sign_rsp = requests.get(url=sign_in_url, headers=sign_headers, timeout=30)
            sign_rsp_json = sign_rsp.json()
            
            print(f"签到响应: {sign_rsp_json}")
            
            rsp_ret = sign_rsp_json.get('ret')
            rsp_score = sign_rsp_json.get('check_in_score', 0)
            
            if rsp_ret == 0:
                success_msg = f"本次签到积分：{rsp_score}"
                print(success_msg)
                
                # 发送 WxPusher 通知
                if wxpusher_token and wxpusher_uid:
                    push_content = f"腾讯视频签到成功！\n\n获得积分：{rsp_score}\n签到时间：{time.strftime('%Y-%m-%d %H:%M:%S')}"
                    send_wxpusher_message(
                        wxpusher_token,
                        push_content,
                        wxpusher_uid,
                        f"签到成功 +{rsp_score}分"
                    )
            else:
                error_msg = f"签到失败，返回码: {rsp_ret}"
                print(error_msg)
                
                if wxpusher_token and wxpusher_uid:
                    send_wxpusher_message(
                        wxpusher_token,
                        f"腾讯视频签到失败\n\n错误信息：{error_msg}\n响应：{sign_rsp_json}",
                        wxpusher_uid,
                        "签到失败"
                    )
        else:
            error_msg = f"认证刷新失败，状态码: {login_rsp.status_code}"
            print(error_msg)
            
            if wxpusher_token and wxpusher_uid:
                send_wxpusher_message(
                    wxpusher_token,
                    f"腾讯视频签到失败\n\n{error_msg}",
                    wxpusher_uid,
                    "签到失败：认证错误"
                )
                
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
