# Tower.im 接入 Slack

将 Tower.im 的消息发送到 Slack 上。

<https://tower-slack.avosapps.com> / <https://tower-slack.avosapps.us>

![Slack 消息示例](https://cloud.githubusercontent.com/assets/290496/10628183/a9b02d5c-77f4-11e5-9894-faf7b2ede82e.png)


## 使用方法

在 Slack 上新建一个 Incoming Webhook，获取到 Webhook URL:

```
https://hooks.slack.com/services/T0DRRRYS1/C9XZ5VL2/bqiCkTrLYMpJcDaKG9HaS4yu
```

将获取到的链接替换成 tower-slack 的链接：

```
https://tower-slack.avosapps.com/T0DRRRYS1/C9XZ5VL2/bqiCkTrLYMpJcDaKG9HaS4yu
```

在 Tower.im 上添加 webhook，填入 tower-slack 的链接

![tower slack](https://cloud.githubusercontent.com/assets/290496/10625797/59b64710-77da-11e5-90dc-e496113aceab.png)

Tower.im webhook 上的 Secret 可不填。如需改变 channel，可将 channel 名填入 Secret，如 `@lepture` 或 `#developer`。

## 部署到 Leancloud

你可以使用我部署好的 <https://tower-slack.avosapps.com/> 也可以自己部署到 Leancloud。直接 clone 这个仓库就可以部署到 Leancloud 了，具体操作请参考 Leancloud 文档。
