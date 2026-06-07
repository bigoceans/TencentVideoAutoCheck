#!/usr/bin/env python3
import requests
import json
import time
from urllib.parse import quote, unquote

# 用户提供的 Cookie
raw_cookie = """_qimei_h38=fdda8b2b9afafebc928a505b0000000021a50e;
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

# 整理Cookie
cookie = ' '.join([x.strip() for x in raw_cookie.split('\n') if x.strip()])

mobile_ua = ('Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; Mi Note 3 Build/OPM1.171019.019) '
             'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.128 '
             'Mobile Safari/537.36 XiaoMi/MiuiBrowser/10.0.2')

# 测试的API列表
test_apis = [
    {
        'name': 'CheckIn',
        'url': 'https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/CheckIn?rpc_data=%7B%7D',
        'headers': {
            'Referer': 'https://film.video.qq.com',
            'Origin': 'https://film.video.qq.com',
            'User-Agent': mobile_ua,
            'Accept': 'application/json, text/plain, */*',
            'Cookie': cookie
        }
    },
    {
        'name': 'ReadTaskList',
        'url': 'https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/ReadTaskList?rpc_data=%7B%22businessId%22%3A%221%22%2C%22platform%22%3A2%7D',
        'headers': {
            'Referer': 'https://film.video.qq.com/x/grade/',
            'Origin': 'https://film.video.qq.com',
            'User-Agent': mobile_ua,
            'Accept': 'application/json, text/plain, */*',
            'Cookie': cookie
        }
    },
    {
        'name': 'spp_MissionFaHuo',
        'url': 'https://vip.video.qq.com/fcgi-bin/comm_cgi?name=spp_MissionFaHuo&cmd=4&task_id=6',
        'headers': {
            'Referer': 'https://film.video.qq.com/x/autovue/grade/',
            'User-Agent': mobile_ua,
            'Cookie': cookie
        }
    },
    {
        'name': 'hierarchical_task_system',
        'url': 'https://vip.video.qq.com/fcgi-bin/comm_cgi?name=hierarchical_task_system&cmd=2',
        'headers': {
            'User-Agent': mobile_ua,
            'Cookie': cookie
        }
    },
    {
        'name': 'spp_vscore_user_mashup',
        'url': 'https://vip.video.qq.com/fcgi-bin/comm_cgi?name=spp_vscore_user_mashup&type=1&otype=xjson',
        'headers': {
            'User-Agent': mobile_ua,
            'Cookie': cookie
        }
    }
]

def log(msg):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {msg}")

def test_api(api):
    log(f"测试 {api['name']} 接口...")
    log(f"URL: {api['url']}")
    try:
        r = requests.get(api['url'], headers=api['headers'], timeout=30)
        log(f"状态码: {r.status_code}")
        log(f"响应: {r.text[:500]}")
        
        # 尝试解析JSON
        try:
            if r.text.startswith('QZOutputJson='):
                json_text = r.text[len('QZOutputJson='):].rstrip(';')
                data = json.loads(json_text)
                log(f"解析后: {json.dumps(data, ensure_ascii=False)}")
            else:
                data = r.json()
                log(f"解析后: {json.dumps(data, ensure_ascii=False)}")
        except Exception as e:
            log(f"JSON解析失败: {e}")
            
    except Exception as e:
        log(f"请求异常: {e}")
    log("-" * 60)

def main():
    log("=" * 60)
    log("开始测试腾讯视频API")
    log("=" * 60)
    
    for api in test_apis:
        test_api(api)
        time.sleep(1)  # 稍微间隔一下

if __name__ == '__main__':
    main()

