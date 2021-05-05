# SAO demo



## 新需求

1. 重新调整一下响应时间，除了计算分数那里需要5000毫秒，其余的如果有长的适当减少一下延迟，最长不超过3000mm吧
2. 更新头像，静态文件已经上传，目前可以正常load， 但是需要调整一下大小，先尝试一下如何改变；（尝试 前端调整大小 or 换更大的其他图片尝试，如果是后者的原因，我们可以跟那边沟通要新图）
3. 探索一下如何改theme (https://docs.botui.org/theme.html)





## 更新:

- 删除了所有message中的 *
- 删除了mental health 101服务结束并选择其他服务时的建议信息
- 修复了non-office-hour时，medium/high level不能正常选择服务的bug
- 调整了选择服务按钮的顺序，使其符合建议信息的先后顺序
- 替换了medium/high level的建议信息。office-hour时不会出现non-office-hour的建议。同理，non-office-hour时不会出现office-hour的建议
- 为所有message添加了loading
- 根据篇幅长度、语境等因素，主观调整了所有message的delay
- 缩短了Confirm Answer的篇幅长度，并用红色加粗字体高亮了Answer




## 需求：



- 添加头像 参考：https://github.com/botui/botui/issues/81
- 登录信息传回后台，发送请求给ITS认证
- 选择语言（ENG/繁/简体）（是否能够提前为第一个逻辑？）
  

