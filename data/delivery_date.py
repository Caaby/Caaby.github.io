from icalendar import Calendar, Event, Alarm
from datetime import timedelta, date
import uuid
import calendar


def option_expiration(year, month):
    """获取year-month的第三个周五"""
    day = 21 - (calendar.weekday(year, month, 1) + 2) % 7
    return date(year, month, day).strftime("%Y%m%d")


def add_event_conf(year, month):  # 事件函数
    date_str = option_expiration(year, month)
    
    event_conf = Event()
    # 当前时间
    event_conf['DTSTAMP;VALUE=DATE'] = date_str  # noqa
    event_conf['UID'] = str(uuid.uuid4())  # 唯一标识
    # 开始时间
    event_conf['DTSTART;VALUE=DATE'] = date_str  # noqa
    event_conf['CLASS'] = 'PRIVATE'  # 保密类型 PRIVATE私有 PUBLIC公开
    event_conf['X-APPLE-TRAVEL-ADVISORY-BEHAVIOR'] = 'AUTOMATIC'
    # 事件名
    event_conf['SUMMARY;LANGUAGE=zh_CN'] = f"{month}月股指期货交割日"  # 事件名
    event_conf['TRANSP'] ="TRANSPARENT"  # noqa
    event_conf['DESCRIPTION'] = f"{year}年{month}月股指期货交割日"  # 详情描述
    event_conf['CATEGORIES'] = "交割日"
    event_conf['X-APPLE-UNIVERSAL-ID'] = str(uuid.uuid4())

    # 闹钟设置
    alarm_conf = Alarm()
    alarm_conf.add('ACTION', 'DISPLAY')  # AUDIO 音频
    alarm_conf.add('X-WR-ALARMUID', str(uuid.uuid4())) # noqa
    alarm_conf.add('UID', str(uuid.uuid4()))
    alarm_conf.add("TRIGGER", timedelta(hours=-15))
    alarm_conf.add("DESCRIPTION", f"{date_str}股指期货交割日")

    event_conf.add_component(alarm_conf)
    return event_conf


def add_calendar():
    cal = Calendar()
    cal.add('VERSION', '2.0')
    cal.add('PROID', 'icalendar-rust')  # noqa
    cal.add('CALSCALE', 'GREGORIAN')  # noqa
    cal.add('X-WR-CALNAME', '股指期货交割日')  # noqa
    cal.add('X-APPLE-LANGUAGE', 'zh')  # noqa
    cal.add('X-APPLE-REGION', 'CN')  # noqa
    cal.add('X-WR-TIMEZONE', 'Asia/Shanghai')
    cal.add('X-WR-CALDESC', '股指期货交割日是合约的约定最后交易日(就是最后履行合约的日子,一般是合约月份的第三个周五,遇国家法定假日顺延)')  # noqa

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
