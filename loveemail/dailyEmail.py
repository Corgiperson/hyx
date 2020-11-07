import time
import datetime
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from lxml import etree

class DailyGreeting(object):

    def __init__(self, friend_list):
        self.cb_link = 'http://open.iciba.com/dsapi/'                       # 金山词霸api提供的每日一句
        self.whether_link = 'http://wthrcdn.etouch.cn/weather_mini?city='   # 天气api
        self.friend_list = friend_list

    def get_whether(self, city, name):
        """
        获取天气信息
        :param city: 城市
        :return: msg
        """
        url = self.whether_link + city
        r = requests.get(url).json()
        week = r['data']['forecast'][0]['date'][-3:]            # 周几
        weather = r['data']['forecast'][0]['type']              # 天气
        low_temp = r['data']['forecast'][0]['low'][3:]          # 最低气温
        high_temp = r['data']['forecast'][0]['high'][3:]        # 最高气温
        wind_dir = r['data']['forecast'][0]['fengxiang']        # 风向
        wind_force = r['data']['forecast'][0]['fengli'][9:-3]   # 风力
        warn = r['data']['ganmao']                              # 感冒预提醒
        # 填充天气信息模板
        msg = '<br>{}，'.format(name) + '今天 ' + week + '<br>' + \
              '<br><font size=3 color=#0081ff><strong>天气：</strong></font>' + city + ' ' + weather + \
              '<br><font size=3 color=#0081ff><strong>温度：</strong></font>' + low_temp + '~' + high_temp + \
              '<br><font size=3 color=#0081ff><strong>风向：</strong></font>' + wind_dir + '，' + wind_force + \
              '<br><br><font size=3 color=red><strong>注意：</strong></font>' + warn + '<br>'
        return str(msg)

    def get_word(self):
        """
        获取金山词霸每日一句
        :return: msg
        """
        r = requests.get(self.cb_link).json()
        en = r['content']
        cn = r['note']
        indent = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' \
                 '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
        # 填充每日一句模板
        msg = '<br><font size=3 color=lightpink><strong><i>' + en + '<br>' + cn + '</strong></font><br>' + \
              '<br>' + indent + '<font size=3 color=#a5673f>—— 至少有一个人在记挂你~' + \
              '</font><br><html><body><img src={}></body></html><br><br>'.format(r['fenxiang_img'])
        return str(msg)

    def get_weibo_news(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'}
        url = 'https://s.weibo.com/top/summary?cate=socialevent'
        html = requests.get(url, headers=headers)
        html.encoding = 'utf-8'
        time.sleep(1)
        selector = etree.HTML(html.text)
        news_list = selector.xpath('/html/body/div[1]/div[2]/div[2]/table/tbody/tr')
        msg = ''
        for news in news_list:
            news_name = news.xpath('td[2]/a/text()')[0]
            news_url = 'https://s.weibo.com' + news.xpath('td[2]/a/@href')[0]
            msg += '<li><a href={} target="_blank">'.format(news_url) + '<font color="#5151A2">' + news_name + '</font>' + '</a></li><br>'
        return msg

    def get_weiboHotNews(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'}
        url = 'https://s.weibo.com/top/summary?cate=realtimehot'
        html = requests.get(url, headers=headers)
        html.encoding = 'utf-8'
        time.sleep(1)
        selector = etree.HTML(html.text)
        news_list = selector.xpath('/html/body/div[1]/div[2]/div[2]/table/tbody/tr')
        msg = ''
        flag = True
        for news in news_list:
            if flag:
                new_id = 'top'
                new_name = news.xpath('td[2]/a/text()')[0]
                new_url = 'https://s.weibo.com' + news.xpath('td[2]/a/@href')[0]
                new_label = news.xpath('td[3]/i/text()')[0]
                flag = False
                msg += '<font color="#FFA042"><strong>' + new_id + '</strong></font>&nbsp;&nbsp;&nbsp;<a href={} target="_blank">'.format(new_url) + '<font color="#46A3FF">' + new_name + '</font>' + '</a>&nbsp;&nbsp;&nbsp;&nbsp;<font color="5CADAD"><strong>{}</strong></font><br>'.format(new_label)
                continue
            new_id = news.xpath('td[1]/text()')[0]
            new_name = news.xpath('td[2]/a/text()')[0]
            new_url = 'https://s.weibo.com' + news.xpath('td[2]/a/@href')[0]
            new_searchNum = news.xpath('td[2]/span/text()')[0]
            new_label = news.xpath('td[3]/i/text()')[0] if len(news.xpath('td[3]/i/text()')) != 0 else ''
            # print(new_label)
            msg += '<font color="#FFA042"><strong>' + new_id + '</strong></font>&nbsp;&nbsp;&nbsp;<a href={} target="_blank">'.format(
                new_url) + '<font color="#46A3FF">' + new_name + '</font></a>&nbsp;&nbsp;&nbsp;&nbsp;' + new_searchNum
            if not new_label: msg += '<br>'
            else: msg += '&nbsp;&nbsp;&nbsp;&nbsp;<font color="5CADAD"><strong>{}</strong></font><br>'.format(new_label)
        return msg

    @staticmethod
    def send_email_message(email, message):
        """
        完成发送邮件功能
        :param email: 收件人
        :param message: 邮件发送内容
        :return:
        """
        # 发件人邮箱地址
        sender = 'chen_tang1999@163.com'
        # 客户端授权码：需要在注册邮箱后，登录进入->设置->常规设置->客户端授权码 里面进行设置
        auth_code = 'DTBZRZLOCYPGKEXR'
        messageObj = MIMEText(message, "html", "utf-8")
        # 设置主题
        messageObj['Subject'] = Header("每日温馨提醒！（刚起床，虽迟但到！）", "utf-8")
        # 设置发件人
        messageObj['From'] = sender
        # 设置收件人
        messageObj['To'] = email
        try:
            # 建立客户端
            smtpObj = smtplib.SMTP()
            # 连接163邮箱服务器地址
            smtpObj.connect('smtp.163.com')
            # 方法二：利用SSL的方式发送
            # smtpObj = smtplib.SMTP_SSL('smtp.163.com', 465)
            # smtpObj.ehlo()    # 使用EHLO向ESMTP服务器标识自己
            # 登录认证
            smtpObj.login(sender, auth_code)
            # 发送邮件
            smtpObj.sendmail(sender, [email], messageObj.as_string())
            # 断开连接
            smtpObj.close()
            print("Send mail successfully.")
            return True
        except smtplib.SMTPException as e:
            print("Send email failed.")
            print("Error logs: ", e)
            return False

    def main(self):
        """
        调度方法
        :return: Boole
        """
        for friend in self.friend_list:
            mail = friend.get('mail')
            city = friend.get('city')
            name = friend.get('name')
            his_or_her_name = friend.get('othername')
            cur_whether = self.get_whether(city, his_or_her_name)
            cur_word = self.get_word()
            cur_news = self.get_weibo_news()
            cur_search = self.get_weiboHotNews()
            # 构造邮件的正文内容
            msg = '您的贴心{}上线啦 ！！！<br>'.format(name) + cur_whether + cur_word + '<font size=5 color=#0081ff>下面是今天的微博要闻榜！</font><br><ul>' + cur_news + '</ul>' + \
            '<font size=5 color=#01B468>下面是今天的微博热搜榜！</font><br>' + cur_search
            print("=========={}: {}".format(friend.get('mail'), msg))
            self.send_email_message(mail, msg)

DailyGreeting([{'mail': '19127927490787238@qq.com', 'city': '西安','othername':'生儿' , 'name': '好兄弟'}]).main()
# if __name__ == '__main__':
#     # 需要发送邮件的联系方式

#     DailyGreeting(friend_list).main()

    # SECONDS_PER_DAY = 24 * 60 * 60  # 一天时间(秒)
    # SET_TIME = 7                    # 定时每日7点执行一次
    # is_first = True                 # 是否第一次执行任务
    # now = datetime.datetime.now()   # 第一次执行获取当前时间
    # # 定时执行任务逻辑
    # while True:
    #     cur_s = now.hour * 60 * 60 + now.minute * 60 + now.second   # 当前时间(时+分+秒)--> 秒
    #     first_gap_s = 0     # 第一次等待的时间(秒)
    #     if now.hour > SET_TIME:
    #         # 当前时间小时数 大于 7点
    #         first_gap_s = 24 * 60 * 60 - cur_s + SET_TIME * 60 * 60 # 差距 --> 秒
    #         print("========== 大于时 ==========", first_gap_s)
    #     elif now.hour < SET_TIME:
    #         # 当前时间小时数 小于 7点
    #         first_gap_s = SET_TIME * 60 * 60 - cur_s
    #         print("========== 小于时 ==========", first_gap_s)
    #     if is_first:
    #         # 第一次执行需要等待的时间，即first_gap_s秒后调用main()发送邮件
    #         time.sleep(first_gap_s)
    #     else:
    #         print("========== 24H 之后再次执行 ==========")
    #         time.sleep(SECONDS_PER_DAY)     # 每24H执行一次
    #     DailyGreeting(friend_list).main()
    #     is_first = False    # 第一次执行完后将is_first置False
    #     print("========== 每日华丽分割线 ==========")