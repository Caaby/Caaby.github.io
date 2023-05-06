from icalendar import Calendar, Event, Alarm
from datetime import datetime, timedelta
import uuid
from zhdate import ZhDate
import toml


def add_event_conf(name, start_date, anniversary, gregorian: bool):  # 事件函数
    event_conf = Event()
    # 当前时间
    event_conf['DTSTAMP;VALUE=DATE'] = 19760401  # noqa
    event_conf['UID'] = str(uuid.uuid4())  # 唯一标识
    # 开始时间
    event_conf['DTSTART;VALUE=DATE'] = start_date.strftime("%Y%m%d")  # noqa
    event_conf['CLASS'] = 'PRIVATE'  # 保密类型 PRIVATE私有 PUBLIC公开
    event_conf['X-APPLE-TRAVEL-ADVISORY-BEHAVIOR'] = 'AUTOMATIC'
    # 事件名
    event_conf['SUMMARY;LANGUAGE=zh_CN'] = name  # 事件名
    event_conf['TRANSP'] ="TRANSPARENT"  # noqa
    event_conf['DESCRIPTION'] = f"{anniversary}年{name}" if anniversary else name  # 详情描述
    event_conf['CATEGORIES'] = "gift"
    event_conf['X-APPLE-UNIVERSAL-ID'] = str(uuid.uuid4())
    if gregorian:
        event_conf.add('RRULE',  {'FREQ': 'YEARLY', 'COUNT': 5})

    # 闹钟设置
    alarm_conf = Alarm()
    alarm_conf.add('ACTION', 'AUDIO')  # AUDIO 音频
    alarm_conf.add('X-WR-ALARMUID', str(uuid.uuid4())) # noqa
    alarm_conf.add('UID', str(uuid.uuid4()))
    alarm_conf.add("TRIGGER", timedelta(weeks=-1, hours=9))

    event_conf.add_component(alarm_conf)
    return event_conf


def add_calendar(conf_dict: dict):
    cal = Calendar()
    cal.add('VERSION', '2.0')
    cal.add('PROID', 'icalendar-rust')  # noqa
    cal.add('CALSCALE', 'GREGORIAN')  # noqa
    cal.add('X-WR-CALNAME', conf_dict.get("title"))  # noqa
    cal.add('X-APPLE-LANGUAGE', 'zh')  # noqa
    cal.add('X-APPLE-REGION', 'CN')  # noqa
    cal.add('X-WR-TIMEZONE', 'Asia/Shanghai')

    gregorian = conf_dict.get('gregorian')
    lunar = conf_dict.get('lunar')

    year = datetime.today().year
    for data in gregorian:
        name = data.get('name')
        date = data.get('date')
        date_parse = str(date).split("-")
        anniversary = 0
        if len(date_parse) == 3:
            birth_year = int(date_parse[0])
            month = int(date_parse[1])
            day = int(date_parse[2])
            anniversary = year - birth_year
        else:
            month = int(date_parse[0])
            day = int(date_parse[1])

        start_date = datetime(year, month, day)
        cal.add_component(add_event_conf(name, start_date, anniversary, gregorian=True))

    # 农历 生成三年的数据
    for year in range(year, year + 5):
        for data in lunar:
            name = data.get('name')
            date = data.get('date')
            date_parse = str(date).split("-")

            anniversary = 0
            if len(date_parse) == 3:
                birth_year = int(date_parse[0])
                month = int(date_parse[1])
                day = int(date_parse[2])
                anniversary = year - birth_year
            else:
                month = int(date_parse[0])
                day = int(date_parse[1])

            start_date = ZhDate(year, month, day).to_datetime()
            cal.add_component(
                add_event_conf(name, start_date, anniversary, gregorian=False)
            )

    with open('gift.ics', 'wb') as f:
        f.write(cal.to_ical())


if __name__ == '__main__':
    """
    pip install icalendar toml zhdate
    """
    conf = toml.load("./gift.toml")
    add_calendar(conf)
