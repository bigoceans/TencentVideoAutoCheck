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

# 测试不同参数的API
rpc_datas = [
    "{}",
    '{"task_id":101}',
    '{"task_id":104}', 
    '{"task_source":104}',
    '{"business_id":1}',
    '{"businessId":1,"platform":2}',
    '{"task_id":101,"platform":2}'
]

def log(msg):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {msg}")

def test_checkin_with_params(rpc_data):
    encoded_rpc_data = quote(rpc_data)
    url = f"https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/CheckIn?rpc_data={encoded_rpc_data}"
    log(f"测试参数: {rpc_data}")
    try:
        headers = {
            'Referer': 'https://film.video.qq.com/x/grade/',
            'Origin': 'https://film.video.qq.com',
            'User-Agent': mobile_ua,
            'Accept': 'application/json, text/plain, */*',
            'Cookie': cookie
        }
        r = requests.get(url, headers=headers, timeout=30)
        log(f"响应: {r.text}")
        if r.text:
            try:
                data = r.json()
                log(f"解析: {json.dumps(data, ensure_ascii=False)}")
            except Exception as e:
                pass
    except Exception as e:
        log(f"异常: {e}")
    log("-" * 60)

# 测试其他可能的接口
other_apis = [
    {
        'name': 'ReceiveScore',
        'url': 'https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/ReceiveScore?rpc_data=%7B%22task_id%22%3A101%2C%22task_source%22%3A104%7D',
    },
    {
        'name': 'ReceiveTaskReward',
        'url': 'https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/ReceiveTaskReward?rpc_data=%7B%22task_id%22%3A101%7D',
    },
    {
        'name': 'CompleteTask',
        'url': 'https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/CompleteTask?rpc_data=%7B%22task_id%22%3A101%7D',
    },
    {
        'name': 'DailyCheckin',
        'url': 'https://vip.video.qq.com/rpc/trpc.new_task_system.task_system.TaskSystem/DailyCheckin?rpc_data=%7B%7D',
    }
]

def test_other_api(api):
    log(f"测试 {api['name']} 接口...")
    try:
        headers = {
            'Referer': 'https://film.video.qq.com',
            'Origin': 'https://film.video.qq.com',
            'User-Agent': mobile_ua,
            'Accept': 'application/json, text/plain, */*',
            'Cookie': cookie
        }
        r = requests.get(api['url'], headers=headers, timeout=30)
        log(f"响应: {r.text}")
        try:
            data = r.json()
            log(f"解析: {json.dumps(data, ensure_ascii=False)}")
        except Exception as e:
            pass
    except Exception as e:
        log(f"异常: {e}")
    log("-" * 60)

def main():
    log("=" * 60)
    log("测试CheckIn接口的不同参数")
    log("=" * 60)
    for rpc_data in rpc_datas:
        test_checkin_with_params(rpc_data)
        time.sleep(0.5)
    
    log("\n" + "=" * 60)
    log("测试其他可能的接口")
    log("=" * 60)
    for api in other_apis:
        test_other_api(api)
        time.sleep(0.5)

if __name__ == '__main__':
    main()

