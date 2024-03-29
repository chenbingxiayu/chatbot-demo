# SAO demo



## 2021.0519 需求：

https://www.cnblogs.com/wasbg/p/10844274.html

Cross-Origin Read Blocking (CORB) 头像的问题可以参考一下这个


## 新需求

1. 更新头像，静态文件已经上传，目前可以正常load， 但是需要调整一下大小，先尝试一下如何改变；（尝试 前端调整大小 or 换更大的其他图片尝试，如果是后者的原因，我们可以跟那边沟通要新图）
2. 探索一下如何改theme (https://docs.botui.org/theme.html)

2021.0517新更新需求
1. 尝试不同形式的T&C,分多段呈现或放一段内（段指的是聊天中一条信息）
2. 在学生选择了suggestion后，仍然有全部suggestion的选项
3. Online Chat T&C 需要再次回答问题包括基本的联系方式以及紧急联系人的联系方式
4. workflow中stop here 那句话下面的一大块句子要用不同的颜色展示
一些需要进一步讨论的问题
1. 有哪些信息需要统计
2. counselor的默认status
3. 如何提醒counselor
4. 如何设置聊天自动退出的条件，比如counselor五分钟内不重连就默认对话结束

2021.0603新更新需求
1. 每次操作网页右边下滑条都默认最下面，需要改成默认最上面，且聊天框内右边下滑条总是在最下面，而网页右边下滑条不变。
2. Emergency Hyperlink (1). 文本替换； (2). 自动判断office-hour
3. 聊天框内所有外链需要确保点击后会打开新的窗口。
4. Q2选否之后对照workflow少显示一个文本框的内容。





## 更新:

- 把按钮文字submit替换成confirm
- rating五个可选项不要emoji
- Thanks for using "MyPoly" 弹出慢一点
- 删除 May I assist 之前的句子
- 解决了第一个polly-agent头像不能正确显示的bug



## 需求：



- 登录信息传回后台，发送请求给ITS认证
- 选择语言（ENG/繁/简体）（是否能够提前为第一个逻辑？）

# i18n
js 文件中用 gettext('msgid')
html 文件用 {% translate 'msgid' %}
其它请查阅https://docs.djangoproject.com/en/3.2/ref/django-admin/#django-admin-makemessages


command:
```
自动生成js .po 文件
python manage.py makemessages --domain djangojs --all
生成html和python .po文件
python manage.py makemessages --all

编译生成 .mo 文件 
python manage.py compilemessages  
```

## Deployment
Our chatbot images is built from source code. So every time we want to deploy the newer version, we have to pull the new code and rebuild the image again.

1. Pull the new code

```bash
cd /root/chatbot/chatbot-demo
git pull
```

2. Edit environment variables

Please specify all your environment variables inside file `.env.docker`, and don't commit into this repo.

3. Deploy backend

```bash
docker-compose up -d --build django celery celery_beat
```

Then it will build the newer image for our chatbot services.
`celery` and `celery_beat` are modules responsible for the scheduled tasks. 
Once this process is done, it has successfully depolyed.

4. Check logs

```bash
# check the containers' name out
docker ps -a

docker logs chatbot-demo_celery_1
docker logs <container name>
```

5. Remove containers and images

```bash
docker-compose down
docker rm -f $(docker ps -a -q) // delete all conainers
docker volume rm $(docker volume ls -q) // remove all docker-compose volumes

# Remove images
docker image ls  // list all images
docker image rm  {IMAGE ID}
# or
docker rmi $(docker images -a -q)
```



# compile js file
```
cd chatbot_demo
npm install
```

## developement mode
开发的时候将setting.py 里面STATS_FILE 设置为 os.path.join(BASE_DIR, "webpack-stats.json")
```
WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        "BUNDLE_DIR_NAME": "/",
        "STATS_FILE": os.path.join(BASE_DIR, "webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "IGNORE": [".*\.hot-update.js", ".+\.map"]
    }
}
```

编译文件命令
```
npm run build
```

## production mode
开发完成后上传最终生产环境的文件，将setting.py 里面STATS_FILE 设置为 os.path.join(BASE_DIR, "webpack-stats-prod.json")

```
WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        "BUNDLE_DIR_NAME": "/",
        "STATS_FILE": os.path.join(BASE_DIR, "webpack-stats-prod.json"),
        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "IGNORE": [".*\.hot-update.js", ".+\.map"]
    }
}
```
编译文件命令
```
npm run prod
```
需要commit的文件为 
改动的js文件
webpack-stats-prod.json
新生成的chatbot_demo/main/static/main-xxxxxxxxx.js文件
旧的chatbot_demo/main/static/main-xxxxxxxxx.js删除


