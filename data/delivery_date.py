from icalendar import Calendar, Event, Alarm, vDate, vDatetime, vText
from datetime import timedelta, date, datetime
import uuid
import calendar
from pytz import timezone

# 创建时区对象，表示东八区（北京时间）
tz = timezone('Asia/Shanghai')


def option_expiration(year, month):
    """获取year-month的第三个周五"""
    day = 21 - (calendar.weekday(year, month, 1) + 2) % 7
    return datetime(year, month, day)


def add_event_conf(year, month):  # 事件函数

    start_date = option_expiration(year, month)
    date_str = start_date.strftime('%Y-%m-%d')

    event_conf = Event()
    # 当前时间
    event_conf.add('DTSTAMP', vDatetime(datetime.now(tz))) # noqa

    event_conf['UID'] = str(uuid.uuid4())  # 唯一标识
    # 开始时间
    event_conf.add('DTSTART', vDate(start_date))  # noqa

    event_conf['CLASS'] = 'PRIVATE'  # 保密类型 PRIVATE私有 PUBLIC公开
    # 事件名
    event_conf['SUMMARY;LANGUAGE=zh_CN'] = f"{month}月股指期货交割日"  # 事件名
    event_conf['TRANSP'] = "TRANSPARENT"  # noqa
    event_conf['DESCRIPTION'] = f"{year}年{month}月股指期货交割日"  # 详情描述
    event_conf['X-APPLE-UNIVERSAL-ID'] = str(uuid.uuid4())
    event_conf['CATEGORIES'] = ["交割日", ]

    # 闹钟设置
    alarm_conf = Alarm()
    alarm_conf.add('ACTION', 'DISPLAY')  # AUDIO 音频
    alarm_conf.add("TRIGGER", vDatetime(start_date + timedelta(days=-1, hours=9)))
    alarm_conf.add("DESCRIPTION", vText(f"明天{date_str}股指期货交割日"))

    alarm = Alarm()
    alarm.add('ACTION', vText('DISPLAY'))  # AUDIO 音频
    alarm.add("TRIGGER", vDatetime(start_date + timedelta(hours=9)))
    alarm.add("DESCRIPTION", vText(f"{date_str}股指期货交割日"))

    event_conf.add_component(alarm)
    event_conf.add_component(alarm_conf)
    return event_conf


def add_calendar():
    cal = Calendar()
    cal.add('VERSION', '2.0')
    cal.add('PROID', vText('caaby.com'))  # noqa
    cal.add('CALSCALE', vText('GREGORIAN'))  # noqa
    cal.add('X-WR-CALNAME', vText('股指期货交割日'))  # noqa
    cal.add('X-APPLE-LANGUAGE', vText('zh'))  # noqa
    cal.add('X-APPLE-REGION', vText('CN'))  # noqa
    cal.add('X-WR-TIMEZONE', vText('Asia/Shanghai'))
    cal.add('X-WR-CALDESC', vText('股指期货交割日是合约的约定最后交易日(就是最后履行合约的日子,一般是合约月份的第三个周五,遇国家法定假日顺延)'))  # noqa

    for y in range(date.today().year, date.today().year + 3):
        for m in range(1, 13):
            cal.add_component(add_event_conf(y, m))

    with open('delivery_date.ics', 'wb') as f:
        f.write(cal.to_ical())


if __name__ == '__main__':
    """
    pip install icalendar
    """
    add_calendar()
