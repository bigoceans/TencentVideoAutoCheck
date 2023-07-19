import requests
import requests.utils
import time
import json
import os
from urllib.parse import quote

def tencent_video_sign_in():
    millisecond_time = round(time.time() * 1000)

    login_url = "https://access.video.qq.com/user/auth_refresh?vappid=XX&vsecret=XX&type=qq&g_tk=&g_vstk=XX&g_actk=XX"  # 替换成自己的

    # 从环境变量获取 LOGIN_COOKIE 的值
    login_cookie = os.getenv('LOGIN_COOKIE')

    # 从环境变量获取 AUTH_COOKIE 的值
    auth_cookie = os.getenv('AUTH_COOKIE')

    login_headers = {
        'Referer': 'https://v.qq.com',
        'Cookie': login_cookie
    }

    login_rsp = requests.get(url=login_url, headers=login_headers)
    print(login_rsp)
    login_rsp_cookie = requests.utils.dict_from_cookiejar(login_rsp.cookies)

    if login_rsp.status_code == 200 and login_rsp_cookie:
        auth_cookie = auth_cookie + 'vqq_vusession=' + login_rsp_cookie['vqq_vusession'] + ';' + 'vqq_access_token=' + login_rsp_cookie['vqq_access_token'] + ';' + 'vqq_appid=' + login_rsp_cookie['vqq_appid'] + ';' + 'vqq_openid=' + login_rsp_cookie['vqq_openid'] + ';' + 'vqq_refresh_token=' + login_rsp_cookie['vqq_refresh_token'] + ';' + 'vqq_vuserid=' + login_rsp_cookie['vqq_vuserid'] + ';'
        print(auth_cookie)

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
        sign_rsp = requests.get(url=sign_in_url, headers=sign_headers)

        sign_rsp_json = sign_rsp.json()
        print(sign_rsp_json)

        rsp_ret = sign_rsp_json['ret']
        rsp_score = sign_rsp_json['check_in_score']

        print("本次签到积分："+str(rsp_score))
        requests.get('https://sc.ftqq.com/自己的sever酱号.send?text=' + quote('签到积分：'+str(rsp_score)))


if __name__ == '__main__':
    tencent_video_sign_in()
    print("10秒后自动关闭")
    time.sleep(10)
