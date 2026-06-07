#!/usr/bin/env python3
import requests
import json
import time
import sys
sys.path.insert(0, '/workspace')

# 用户提供的 Cookie
USER_COOKIE = """_qimei_h38=fdda8b2b9afafebc928a505b0000000021a50e;
_qimei_q36=;
last_refresh_time=1780818740871;
last_refresh_vuserid=436206801;
qq_head=https%3A%2F%2Fcommunity.image.video.qpic.cn%2Fapp_community_42f1e-8_6930052679_1756726214935307;
qq_nick=%E6%A9%A1%E7%9A%AE%E7%B3%96YuYu;
main_login=qq;
p_vuserid=0;
role=0;
v_login_time_init=1780818740;
v_main_login=qq;
v_next_refresh_time=7200;
v_p_vuserid=0;
v_role=0;
v_t_access_token=37492EB956F230D9444F4DBF5525D2B6;
v_t_appid=101527197;
v_t_openid=C0EB384ADC9AE93D0B074ECE3521568C;
v_t_refresh_token=MBS;
v_vurefresh=BYOHg0Y1MsXWDOmLBShKKhLrn-7-x--aQ4CjpDTxI5DKqDD4_LFcnw92yf4NWRN_OJ6cJk6dKlnYbKpoGA8A9O__Vnc;
v_vuserid=436206801;
v_vusession=BTnL3hcJPagx8GGFJcIfjFaRddiEVNm61e0tvNb7OyGVNN2g1aw_wLwO7sWkixwDVpclne0wG_nzmuTbhuCrMJWVdsfNQUWK9MZUpIKTsgUGfcoVu46Log11Xy_e9vVECwsS7EHRE6PFzxYL51lEaUHJEfkKn3mpScFWreBYm-VMvlWqCMjQnbz3Q34.O;
video_platform=2;
vqq_access_token=37492EB956F230D9444F4DBF5525D2B6;
vqq_appid=101527197;
vqq_login_time_init=1780818740;
vqq_next_refresh_time=7200;
vqq_openid=C0EB384ADC9AE93D0B074ECE3521568C;
vqq_refresh_token=MBS;
vqq_vuserid=436206801;
vqq_vusession=BTnL3hcJPagx8GGFJcIfjFaRddiEVNm61e0tvNb7OyGVNN2g1aw_wLwO7sWkixwDVpclne0wG_nzmuTbhuCrMJWVdsfNQUWK9MZUpIKTsgUGfcoVu46Log11Xy_e9vVECwsS7EHRE6PFzxYL51lEaUHJEfkKn3mpScFWreBYm-VMvlWqCMjQnbz3Q34.O;
a_pk__04=fdda8b2b9afafebc928a505b0000000021a50e;
a_sk__07__15d45fa36b498329=01546563636c63676d666362;
a_sk__05=01546335646c3236626535606531313261366c32606062323031676c636d356c3636;
a_sk__10=01546364356661366d30666d3731646135326337316666306c30376d656c356c656760666464;
_qimei_fingerprint=e819a7065d06fe1da69ff2c0668fef08;
_qimei_uuid42=1a60707321e100113d8fbb2f866363550243771ff1;
pgv_pvid=4416315478;
video_guid=1771e672b8c6fd7a;
qq_domain_video_guid_verify=1771e672b8c6fd7a;"""

def log_message(msg):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {msg}")

def test_tencent_video():
    log_message("=" * 60)
    log_message("腾讯视频签到测试（使用用户提供的Cookie）")
    log_message("=" * 60)
    
    # 整理Cookie
    cookie = ' '.join([x.strip() for x in USER_COOKIE.split('\n') if x.strip()])
    
    mobile_ua = ('Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; Mi Note 3 Build/OPM1.171019.019) '
                 'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.128 '
                 'Mobile Safari/537.36 XiaoMi/MiuiBrowser/10.0.2')
    
    # 1. 获取用户信息
    log_message("\n--- 第一步：获取用户信息 ---")
    try:
        info_url = 'https://vip.video.qq.com/fcgi-bin/comm_cgi?name=spp_vscore_user_mashup&type=1&otype=xjson'
        headers = {'User-Agent': mobile_ua, 'Cookie': cookie}
        rsp = requests.get(info_url, headers=headers, timeout=30)
        if rsp.status_code == 200:
            data = rsp.json()
            if data.get('ret') == 0:
                score_info = data.get('cscore_info', {})
                level_info = data.get('lscore_info', {})
                log_message(f"✅ 用户信息获取成功！")
                log_message(f"   - V力值总计: {score_info.get('vip_score_total', 0)}")
                log_message(f"   - 会员等级: V{level_info.get('level', 0)}")
                log_message(f"   - 等级积分: {level_info.get('score', 0)}")
            else:
                log_message(f"❌ 获取用户信息失败: {data}")
    except Exception as e:
        log_message(f"❌ 获取用户信息异常: {e}")
    
    # 2. 尝试签到
    log_message("\n--- 第二步：尝试签到 ---")
    
    sign_urls = [
        {
            'name': 'trpc CheckIn',
            'url': 'https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/CheckIn?rpc_data=%7B%7D',
            'headers': {
                'Referer': 'https://film.video.qq.com',
                'Origin': 'https://film.video.qq.com',
                'User-Agent': mobile_ua,
                'Accept': 'application/json, text/plain, */*',
                'Cookie': cookie
            }
        }
    ]
    
    for api in sign_urls:
        log_message(f"\n尝试接口: {api['name']}")
        try:
            rsp = requests.get(api['url'], headers=api['headers'], timeout=30)
            log_message(f"  状态码: {rsp.status_code}")
            log_message(f"  响应: {rsp.text}")
            
            try:
                data = rsp.json()
                ret = data.get('ret')
                msg = data.get('msg', '')
                
                if ret == 0:
                    log_message("✅ 签到成功！")
                    checkin_score = data.get('check_in_score', 0) or data.get('checkin_score', 0)
                    if checkin_score:
                        log_message(f"   获得 {checkin_score} V力值")
                elif ret == -10006:
                    log_message("❌ Cookie已过期！")
                elif ret == -110009:
                    security_info = data.get('security_verify', {})
                    user_msg = security_info.get('sUserMsg', '需要图形验证')
                    log_message(f"❌ 安全验证未通过: {user_msg}")
                    log_message("💡 这是正常的，因为腾讯视频现在需要图形验证码。")
                    log_message("💡 建议：在手机APP中手动签到，完成验证后再试。")
                elif ret == -10:
                    log_message(f"⚠️ 接口已失效: {msg}")
                else:
                    log_message(f"❌ 未知错误 (ret={ret}): {msg}")
            except Exception as e:
                log_message(f"❌ 解析响应失败: {e}")
                
        except Exception as e:
            log_message(f"❌ 请求失败: {e}")
    
    log_message("\n" + "=" * 60)
    log_message("测试完成！")
    log_message("=" * 60)

if __name__ == '__main__':
    test_tencent_video()
