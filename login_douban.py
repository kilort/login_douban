import requests,re,time,http.cookiejar as cookielib
agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/63.0.3239.84 Chrome/63.0.3239.84 Safari/537.36'


#豆瓣的登陆有所不同，不可一次性的将username，passwd，captcha等数据一同post，否则将登陆失败，需要先带入un和pd去获取captcha然后再captcha导入到
#post表单中，否则登陆将失败，而且在第一次用un，pdpost时不可以用session创建会话，只可以通过requests的方法，可以比作是新的浏览器登录时是不会有session
#的，在un和pd输入成功后，获取captcha的信息，在导入到session的post的表单中，这可能就是豆瓣的反爬机制，在datas表单创建时，remember键值对的作用可以看作
#是保持post表单的一致性，具体的方法不知道。

headers = { 'Host':'www.douban.com',
            'Referer':'https://www.douban.com',
             'User-Agent': agent
           }
#创建post数据表单datas
datas = {'source': 'index_nav',
        'remember': 'on'
        }
#创建session

session =requests.session()
session.cookies = cookielib.LWPCookieJar(filename='login_douban_cookie.txt')
try:
    session.cookies.load(ignore_discard=True)
except:
    print('cookies导入失败')
    #输入email和password
    datas['form_email'] = input('username:')
    datas['form_password'] = input('password:')
url ='https://accounts.douban.com/login'
#豆瓣的captcha是在login页面中写好的，需要提取

def get_captcha():
    req = requests.post(url,data =datas,headers=headers)
    req.encoding = 'utf-8'
    pat1 = '<img id="captcha_image" src="(.*?)"'
    #提取captcha链接
    captcha_url = re.compile(pat1,re.S).findall(req.text)[0]
    #print(captcha_url)
    pat2 = 'https:\/\/www.douban.com\/misc\/captcha\?id=(.*?)&amp;size=s'
    #提取captcha_id的链接
    id = re.compile(pat2).findall(captcha_url)[0]
    #print(id)
    #获取captcha并存入本地读取输入
    r = session.get(captcha_url,headers=headers)
    with open('douban_captcha.jpg','wb')as f:
        try:
            f.write(r.content)
            f.close()
            print('到根目录下查看验证码 captcha.jpg文件')
            captcha = input('验证码：')
        except:
            print('验证码抓取出错请重试')
            captcha =' '
    return (captcha,id)

#判断是否登陆，
def is_login():
    url = 'https://www.douban.com/mine/orders/'
    login_code = session.get(url,headers=headers,allow_redirects = False).status_code
    if login_code ==200:
        return  True
    else:
        return False

#若未登陆则登陆
def login():
    (captcha, id) = get_captcha()
    #post表单中添加captcha的数据
    datas['captcha-solution'] = captcha
    datas['captcha-id'] = id
    login_page = session.post(url,headers=headers,data = datas)
    pat = '<title>(.*?)</title>'
    title = re.compile(pat).findall(login_page.text)
    #查看title判断是否登陆成功
    print(title)
    session.cookies.save()
if __name__ =='__main__':
    if is_login():
        print('已登陆')
    else:
        login()
