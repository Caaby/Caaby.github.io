from icalendar import Calendar, Event, Alarm
from datetime import datetime,timedelta
import uuid
from zhdate import ZhDate
import toml
import requests
import os
from io import StringIO


"""
BEGIN:VCALENDAR									# 日历开始
PRODID:-//139 Mail//calendar 2.3//EN			# 软件信息
VERSION:2.0										# 遵循的iCalendar版本号
CALSCALE:GREGORIAN								# 历法：公历
METHOD:PUBLISH                                  # 方法：公开 也可以是 REQUEST 等用于日历间的信息沟通方法
X-WR-CALNAME:yulanggong@gmail.com               # 这是一个通用扩展属性 表示本日历的名称
X-WR-TIMEZONE:Asia/Shanghai                     # 通用扩展属性，表示时区

BEGIN:VEVENT									# 事件开始
DTSTAMP:20230411T031706Z						# 有 Method 属性时表示实例创建时间，没有时表示最后修订的日期时间
DTSTART:20230410T000000							# 开始的时间
DTEND:20230411T000000							# 结束的时间
SUMMARY:每周提醒，测试								# 简介、标题
LOCATION:地点										# 地点
DESCRIPTION:备注L提前15分钟						# 事件的描述
X-ALLDAY:1										# 是否是全天事件
UID:10-414111111-1591111111@139.com			# 唯一标识
CLASS:PRIVATE                               # 保密类型
ORGANIZER:mailto:1591111111@139.com			# 组织者
SEQUENCE:1                                  # 排列序号
STATUS:CONFIRMED                            # 状态 TENTATIVE 试探 CONFIRMED 确认 CANCELLED 取消
ATTENDEE;CN=11111@outlook.com;RSVP=TRUE:mailto:11111@outlook.com
ATTENDEE;CN=1111111@qq.com;RSVP=TRUE:mailto:1111111@qq.com
RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,WE,FR
X-REQMY:EMAIL
BEGIN:VALARM									# alarm组件开始
TRIGGER:-PT15M									# 提前15分钟提醒
REPEAT:1
DURATION:PT1M
SUMMARY:每周提醒，测试
ACTION:DISPLAY									# 在ACTION:DISPLAY时，预期的效果是向用户显示“DESCRIPTION”属性的文本值。
DESCRIPTION:每周提醒，测试
END:VALARM										# alarm结束
END:VEVENT										# 事件结束

END:VCALENDAR									# 日历结束

"""


def add_event_conf(name, start_date, anniversary):  # 事件函数
    event_conf = Event()
    # 当前时间
    # 时间戳 属性时表示实例创建时间，没有时表示最后修订的日期时间
    event_conf['DTSTAMP;VALUE=DATE'] = 19760401  # noqa
    event_conf['UID'] = str(uuid.uuid4())  # 唯一标识
    # 开始时间
    event_conf['DTSTART;VALUE=DATE'] = start_date.strftime("%Y%m%d")  # noqa
    event_conf['CLASS'] = 'PRIVATE'  # 保密类型 PRIVATE私有 PUBLIC公开
    # 结束时间
    # noqa event_conf['DTEND;VALUE=DATE'] = (start_date + timedelta(days=1)).strftime("%Y%m%d")
    # noqa event_conf.add('X-ALLDAY', 1)  # noqa  是否是全天事件
    event_conf['X-APPLE-TRAVEL-ADVISORY-BEHAVIOR'] = 'AUTOMATIC'
    # 事件名
    event_conf['SUMMARY;LANGUAGE=zh_CN'] = f"{name}生日"  # 事件名
    event_conf['TRANSP'] ="TRANSPARENT"  # noqa
    event_conf['DESCRIPTION'] = f"{name}{anniversary}周岁的生日" if anniversary else f"{name}的生日"  # 详情描述
    event_conf['CATEGORIES'] = "聖日"
    event_conf['X-APPLE-UNIVERSAL-ID'] = str(uuid.uuid4())
    # event_conf.add('RRULE',  {'FREQ': 'YEARLY', 'COUNT': 5})

    # 闹钟设置，默认为无闹钟
    # alarm_conf = Alarm()
    # alarm_conf.add('ACTION', 'NONE')
    # alarm_conf.add('TRIGGER;VALUE=DATE-TIME', '19760401T005545Z')
    # 10分钟
    # alarm_conf.add('ACTION', 'DISPLAY')
    # alarm_conf.add("TRIGGER;RELATED=START", "-PT{0}M".format(10))
    # event_conf.add_component(alarm_conf)

    # 闹钟设置
    alarm_conf = Alarm()
    alarm_conf.add('ACTION', 'DISPLAY')  # AUDIO 音频
    alarm_conf.add('X-WR-ALARMUID', str(uuid.uuid4())) # noqa
    alarm_conf.add('UID', str(uuid.uuid4()))
    alarm_conf.add("TRIGGER", timedelta(days=-1))
    alarm_conf.add("TRIGGER", timedelta(days=-2))
#     alarm_conf.add("TRIGGER;RELATED=START", "PT9H")
    # alarm_conf.add("TRIGGER;RELATED=START", "-PT{0}M".format(10))

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
    cal.add('X-APPLE-CALENDAR-COLOR', '#708090')
    cal.add('X-WR-TIMEZONE', 'Asia/Shanghai')

    data_list = conf_dict.get('birthday')

    # 生成三年的数据
    for year in range(
            datetime.today().year,
            datetime.today().year + 3):

        for data in data_list:
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
            event = add_event_conf(name, start_date, anniversary)
            cal.add_component(event)

    with open('birthday.ics', 'wb') as f:
        f.write(cal.to_ical())


if __name__ == '__main__':
    """
    pip install icalendar==4.1.0 toml=0.10.2 requests==2.27.1 zhdate
    """
    url = os.getenv("BIRTH_CONG_TOML_URL")
    if not url:
        exit(1)

    resp = requests.get(url)
    resp.raise_for_status()
    conf = toml.load(f=StringIO(resp.text))
    add_calendar(conf)
