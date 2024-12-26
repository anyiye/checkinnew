import requests
import json
import os
from time import sleep
from requests import post, get
from pypushdeer import PushDeer

# -------------------------------------------------------------------------------------------
# github workflows
# -------------------------------------------------------------------------------------------
if __name__ == '__main__':
    # pushdeer key 申请地址 https://www.pushdeer.com/product.html
    sckey = os.environ.get("SENDKEY", "")

    # 推送内容
    title = ""
    success, fail, repeats = 0, 0, 0        # 成功账号数量 失败账号数量 重复签到账号数量
    context = ""

    # glados账号cookie 直接使用数组 如果使用环境变量需要字符串分割一下
    cookies = os.environ.get("COOKIES", []).split("&")
    if cookies[0] != "":

        check_in_url = "https://glados.space/api/user/checkin"        # 签到地址
        status_url = "https://glados.space/api/user/status"          # 查看账户状态

        referer = 'https://glados.space/console/checkin'
        origin = "https://glados.space"
        useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        payload = {
            'token': 'glados.one'
        }
        
        for cookie in cookies:
            checkin = requests.post(check_in_url, headers={'cookie': cookie, 'referer': referer, 'origin': origin,
                                    'user-agent': useragent, 'content-type': 'application/json;charset=UTF-8'}, data=json.dumps(payload))
            state = requests.get(status_url, headers={
                                'cookie': cookie, 'referer': referer, 'origin': origin, 'user-agent': useragent})

            message_status = ""
            points = 0
            message_days = ""
            
            
            if checkin.status_code == 200:
                # 解析返回的json数据
                result = checkin.json()     
                # 获取签到结果
                check_result = result.get('message')
                points = result.get('points')

                # 获取账号当前状态
                result = state.json()
                # 获取剩余时间
                leftdays = int(float(result['data']['leftDays']))
                # 获取账号email
                email = result['data']['email']
                
                print(check_result)
                if "Checkin! Got" in check_result:
                    success += 1
                    message_status = "签到成功，会员点数 + " + str(points)
                elif "Checkin Repeats!" in check_result:
                    repeats += 1
                    message_status = "重复签到，明天再来"
                else:
                    fail += 1
                    message_status = "签到失败，请检查..."

                if leftdays is not None:
                    message_days = f"{leftdays} 天"
                else:
                    message_days = "error"
            else:
                email = ""
                message_status = "签到请求URL失败, 请检查..."
                message_days = "error"

            context += "账号: " + email + ", P: " + str(points) +", 剩余: " + message_days + " | "

        # 推送内容 
        title = f'Glados, 成功{success},失败{fail},重复{repeats}'
        print("Send Content:" + "\n", context)
        
    else:
        # 推送内容 
        title = f'# 未找到 cookies!'

    print("sckey:", sckey)
    print("cookies:", cookies)


    # 推送消息
    # 未设置 sckey 则不进行推送
    if not sckey:
        print("Not push")
        print ("Sever酱: 未配置sckey，无法进行消息推送。")
    else:
        #pushdeer = PushDeer(pushkey=sckey) 
        #pushdeer.send_text(title, desp=context) 
        #增加Sever酱推送
        print ("========================================")
        print ("Sever酱: 开始推送消息！")
        context = context.replace('\n', '\n\n')
        url = f'https://sctapi.ftqq.com/{sckey}.send'
        data = {'title': title, 'desp': context, 'channel': 9}
        rsp = post(url=url, data=data)
        pushid = rsp.json()['data']['pushid']
        readkey = rsp.json()['data']['readkey']
        state_url = f'https://sctapi.ftqq.com/push?id={pushid}&readkey={readkey}'

        count = 1
        while True:
            status_rsp = get(url=state_url)
            result = status_rsp.json()['data']['wxstatus']
            print ("查询消息推送是否成功ing : {count}")

        if result:
            print ("消息推送成功！")
        elif count >= 60:   # 防止程序一直运行
            print ("程序运行结束！推送结果未知！")
        count += 1
        sleep(1)





