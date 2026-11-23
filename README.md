# PS5 光碟版監控

每 5 分鐘由 GitHub Actions 啟動，每 60 秒查 PChome 24h、Yahoo購物中心、宏碁遊戲，找到「PS5 光碟版主機、≤ NT$22,000、可購買」就推播到手機（ntfy）。

- 改價格上限：`.github/workflows/monitor.yml` 的 `MAX_PRICE`
- 通知管道設在 repo 的 Settings → Secrets：`NTFY_TOPIC`、`TELEGRAM_BOT_TOKEN`、`TELEGRAM_CHAT_ID`、`DISCORD_WEBHOOK`
- 暫停：Actions 分頁 → PS5 監控 → Disable workflow
