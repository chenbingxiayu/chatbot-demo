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





## 更新:

- 把按钮文字submit替换成confirm
- rating五个可选项不要emoji
- Thanks for using "MyPoly" 弹出慢一点
- 删除 May I assist 之前的句子
- 解决了第一个polly-agent头像不能正确显示的bug



## 需求：



- 登录信息传回后台，发送请求给ITS认证
- 选择语言（ENG/繁/简体）（是否能够提前为第一个逻辑？）
  

