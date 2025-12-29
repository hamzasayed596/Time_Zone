import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

app_token = os.environ.get("SLACK_APP_TOKEN")
bot_token = os.environ.get("SLACK_BOT_TOKEN")

app = App(token=app_token)
df = pd.read_csv("time_zone_data.csv")
df.columns = df.columns.str.lower()

def utc_offset(offset_str):
    if not offset_str or offset_str == '':
        return 0
    offset_str = offset_str.replace("UTC", "").strip()
    if offset_str == '':
        return 0
    sign = 1
    if offset_str[0] == "-":
        sign = -1
    offset_str = offset_str.replace("+", "").replace("-", "")
    parts = offset_str.split(":")
    if len(parts) != 2:
        return 0

    hours = int(parts[0])
    minutes = int(parts[1])
    return sign * (int(hours) + int(minutes) / 60)

def am_pm(h, m):
    suf = "AM"
    if h >= 12:
        suf = "PM"
    if h == 0:
        h = 12
    elif h > 12:
        h -= 12
    if h < 10:
        h_str = "0" + str(h)
    else:
        h_str = str(h)
    if m < 10:
        m_str = "0" + str(m)
    else:
        m_str = str(m)
    return h_str + ":" + m_str + " " + suf

@app.command("/switchtime")
def handle_switchtime(ack, body, client):
    ack()
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "switchtime",
            "title": {"type": "plain_text", "text": "Switch Time Zone"},
            "submit": {"type": "plain_text", "text": "Convert"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "country_from",
                    "label": {"type": "plain_text", "text": "From"},
                    "element": {
                        "type": "external_select",
                        "action_id": "country_from_select",
                        "placeholder": {"type": "plain_text", "text": "Start typing..."}
                    }
                },
                {
                    "type": "input",
                    "block_id": "country_to",
                    "label": {"type": "plain_text", "text": "To"},
                    "element": {
                        "type": "external_select",
                        "action_id": "country_to_select",
                        "placeholder": {"type": "plain_text", "text": "Start typing..."}
                    }
                },
                {
                    "type": "input",
                    "block_id": "time_block",
                    "label":{"type": "plain_text", "text": "Select Time"},
                    "element": {
                        "type": "timepicker",
                        "action_id": "time_picker_action",
                    }
                }
            ]
        }
    )

@app.options("country_to_select")
def handle_country_select(ack, body):
    user_input = body.get("value","").lower()
    options = []
    for i in range(len(df)):
        country = str(df['country'][i])
        code = str(df['code'][i])
        tz = str(df['timezone'][i])
        if user_input in country.lower():
            label = country + " (" + code + ")" + " || " + tz
            options.append({
                "text": {"type": "plain_text", "text": label},
                "value": tz
            })
    ack(options=options[:100])

@app.options("country_from_select")
def handle_country_select(ack, body):
    user_input = body.get("value","").lower()
    options = []
    for i in range(len(df)):
        country = str(df['country'][i])
        code = str(df['code'][i])
        tz = str(df['timezone'][i])
        if user_input in country.lower():
            label = country + " (" + code + ")" + " || " + tz
            options.append({
                "text": {"type": "plain_text", "text": label},
                "value": tz
            })
    ack(options=options[:100])

@app.view("switchtime")
def submission(ack, body, client):
    ack()
    state = body["view"]["state"]["values"]

    from_tz = state["country_from"]["country_from_select"]["selected_option"]["value"]
    to_tz = state["country_to"]["country_to_select"]["selected_option"]["value"]

    selected_time = state["time_block"]["time_picker_action"]["selected_time"]
    h,m = selected_time.split(":")

    raw_from = df.loc[df["timezone"] == from_tz, "utcoffset"].values[0]
    raw_to = df.loc[df["timezone"] == to_tz, "utcoffset"].values[0]

    off_from = utc_offset(raw_from)
    off_to = utc_offset(raw_to)

    total_original = int(h) * 60 + int(m)
    total_from = int(off_from * 60)
    total_to = int(off_to * 60)

    diff = total_to - total_from

    new_total = (total_original + diff) % (24 * 60)
    new_h = new_total // 60
    new_m = new_total % 60

    converted_time = am_pm(new_h, new_m)

    client.chat_postMessage(
        channel=body["user"]["id"],
        text=converted_time
    )

if __name__ == "__main__":
    handler = SocketModeHandler(app, bot_token)
    handler.start()
