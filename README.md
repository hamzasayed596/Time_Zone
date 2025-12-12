# ⏰ Slack Time Zone Switcher Bot

A lightweight Slack bot that converts time between countries using an interactive modal.  
Great for distributed teams and quick scheduling across different time zones.
And you can also it to not pass the YSWS deadline!

---

## 🎯 Features

- `/switchtime` slash command  
- Select **From** and **To** countries using Slack’s searchable dropdown  
- Pick a time with Slack’s built-in timepicker  
- Automatically calculates the correct converted time based on UTC offsets  
- Sends the result back to the user via DM in AM/PM format

---

## 📁 Project Files

- `main.py` – Slack Bolt app with modal, handlers, and conversion logic  
- `time_zone_data.csv` – Countries, ISO codes, timezones, UTC offsets  
---

## ⚙️ How It Works

1. User runs `/switchtime`.  
2. A modal opens with two dropdowns and a timepicker.  
3. The bot looks up UTC offsets from the CSV.  
4. It calculates the time difference.  
5. It sends the converted time back to the user.

---
