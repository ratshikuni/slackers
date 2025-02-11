import pytz
from datetime import datetime, timedelta
from collections import defaultdict

def handle_datetime(date_string, duration):
    tz = pytz.timezone('Africa/Johannesburg')
    start_time = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
    start_time = pytz.utc.localize(start_time)
    start_time_za = start_time.astimezone(tz)
    end_time = start_time_za + timedelta(minutes=duration)

    meeting_duration = f"{start_time_za.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
    date = start_time_za.strftime('%b %d')
    
    return date, meeting_duration, start_time_za, end_time

def get_meeting_lists(meets):
    tz = pytz.timezone('Africa/Johannesburg')
    meetings_list = defaultdict(list)

    now = datetime.now(tz)
    today = datetime.now(tz).date()
    tomorrow = today + timedelta(days=1)

    for meeting in meets['meetings']:
        meeting_info = {}
        date, duration, start_time, end_time = handle_datetime(meeting['start_time'], meeting['duration'])

        meeting_info["title"] = meeting['topic']
        meeting_info["link"] = meeting['join_url']
        meeting_info["time"] = duration
        meeting_info["day"] = date
        meeting_info["id"] = meeting['id']
        meeting_info["start_time"] = start_time.isoformat()
        meeting_info["end_time"] = end_time.isoformat()

        if start_time.date() == today:
            if start_time <= now <= end_time:
                meetings_list['live'].append(meeting_info)
            else:
                meetings_list['today'].append(meeting_info)
        elif start_time.date() == tomorrow:
            meetings_list['tomorrow'].append(meeting_info)
        else:
            meetings_list[date].append(meeting_info)

    return meetings_list
