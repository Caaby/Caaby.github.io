from icalendar import Calendar, Event, Alarm, vDatetime, vDuration, vText
from datetime import datetime, timedelta
import uuid
from zhdate import ZhDate
import toml
import requests
import os
from io import StringIO
from pytz import timezone
from oss_update import put_object

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

# 创建时区对象，表示东八区（北京时间）
tz = timezone('Asia/Shanghai')


def add_event_conf(name, start_date, anniversary):  # 事件函数
    event_conf = Event()
    event_conf.add('CREATED', vDatetime(datetime.now(tz)))
    event_conf.add('LAST-MODIFIED', vDatetime(datetime.now(tz)))
    # event_conf.add('LOCATION', vText('Room 101'))
    event_conf.add('dtstamp', vDatetime(datetime.now(tz)))
    """ DTSTAMP 是 icalendar 中一个标准的属性（Property），用于指示事件的创建或最后修改时间。

        该属性表示一个日期时间值，用于指示事件的创建或最后修改时间。具体含义如下：
            对于新创建的事件，DTSTAMP 属性应该表示该事件的创建时间。
            对于已经存在的事件，DTSTAMP 属性应该表示该事件的最后修改时间。
    """

    event_conf['UID'] = str(uuid.uuid4())
    event_conf.add('UID', vText(uuid.uuid4()))
    """唯一标识"""

    event_conf.add('dtstart', vDatetime(start_date))  # noqa
    """开始时间
        vDate 表示日期事件
        vDatetime 表示时间事件
    """

    event_conf.add('dtend', vDatetime(start_date + timedelta(hours=23)))  # noqa
    """结束时间"""

    event_conf.add('class', vText('PRIVATE'))
    """CLASS 是 icalendar 中一个标准的属性（Property），用于指示事件的保密级别或重要性。
        该属性表示一个字符串值，用于指示事件的保密级别或重要性。具体取值及含义如下：
            PUBLIC：表示事件是公开的，任何人都可以查看。
            PRIVATE：表示事件是私有的，只有组织者和邀请的参与者可以查看。
            CONFIDENTIAL：表示事件是保密的，只有组织者和邀请的参与者可以查看，并且应该采取特殊措施保护隐私。
        除了上述标准取值外，CLASS 属性还可以使用其他自定义取值，以便满足特定应用的需求。
    """

    event_conf.add('x-allday', 'TRUE')  # noqa
    """ X-ALLDAY 是 icalendar 中一个非标准的属性（Non-Standard Property），通常用于指示事件是否是全天事件。
        全天事件是一种不需要指定具体时间的事件，通常用于表示整天的节日或假期等。在 icalendar 标准中，全天事件的开始时间和结束时间应该分别设置为当天的起始时间和结束时间。而 X-ALLDAY 属性则可以用于更方便地指示事件是否是全天事件。

        该属性表示一个布尔值，用于指示事件是否是全天事件。具体取值及含义如下：
            TRUE：表示事件是全天事件。
            FALSE：表示事件不是全天事件。
    """

    event_conf['X-APPLE-TRAVEL-ADVISORY-BEHAVIOR'] = 'CALCULATED'
    """ X-APPLE-TRAVEL-ADVISORY-BEHAVIOR 是 icalendar 中一个非标准的属性（Non-Standard Property），
        通常用于在 Apple 设备上指示旅行事件的行为。

        该属性表示一个字符串值，用于指示旅行事件的行为。具体取值及含义如下：
            AUTOMATIC：表示自动更新旅行建议，即根据当前位置和交通方式自动计算旅行时间。
            CONFIRMED：表示旅行时间已确认，不需要更新旅行建议。
            CALCULATED：表示已手动计算旅行时间，不需要更新旅行建议。

    """
    event_conf.add('SUMMARY', vText(f"{name}生日"))  # 事件名
    """用于指示事件的摘要或标题。
    """

    event_conf.add('TRANSP', vText('OPAQUE'))  # noqa
    """ 在icalendar标准中，TRANSP是一个事件属性（EventProperty），用于指示事件的可见性，即指示事件是否应该在日历中显示。

        TRANSP属性包含以下取值：
            TRANSPARENT：表示事件是透明的，即事件的时间段应该被忽略，不应该在日历中显示。
            这通常用于表示非工作时间或其他不需要显示在日历中的时间段。

        OPAQUE：表示事件是不透明的，即事件的时间段应该被显示在日历中。这是TRANSP属性的默认取值。
    """
    description = f"{name}{anniversary}周岁生日" if anniversary else f"{name}生日"  # 详情描述
    event_conf.add('description', vText(description))

    event_conf['CATEGORIES'] = ["生日", ]
    """ CATEGORIES 是一个事件属性（Event Property）用于指示事件所属的类别或标签
    """

    event_conf['X-APPLE-UNIVERSAL-ID'] = str(uuid.uuid4())
    """ X-APPLE-UNIVERSAL-ID 是 icalendar 中一个非标准的属性（Non-Standard Property），
        通常用于在 Apple 设备上对事件进行标识和同步。
        该属性表示一个字符串值，用于唯一标识一个事件。该属性通常用于在同步事件时进行匹配，以便在多个设备之间保持事件的同步状态。
    """

    """ 设置组织者信息
    organizer = vCalAddress('MAILTO:noreply@example.com')
    organizer.params['cn'] = vText(name)
    event_conf.add('organizer', organizer)
    """

    # 创建4个闹钟提醒
    alarm = Alarm()
    alarm1 = Alarm()
    alarm2 = Alarm()
    alarm3 = Alarm()

    alarm.add('action', 'DISPLAY')
    alarm.add('trigger', vDuration(timedelta(days=-6, hours=-15)))
    alarm.add('description', vText('下周{}'.format(description)))

    alarm1.add('action', 'DISPLAY')
    alarm1.add('trigger', vDuration(timedelta(days=-1, hours=-15)))
    alarm1.add('description', vText('后天{}'.format(description)))

    alarm2.add('action', 'DISPLAY')
    alarm2.add('trigger', vDuration(timedelta(hours=-15)))
    alarm2.add('description', vText('明天{}'.format(description)))

    alarm3.add('action', 'DISPLAY')
    alarm3.add('trigger', vDuration(timedelta(hours=+9)))
    alarm3.add('description', vText('今天{}'.format(description)))

    event_conf.add_component(alarm)
    event_conf.add_component(alarm1)
    event_conf.add_component(alarm2)
    event_conf.add_component(alarm3)
    return event_conf


def add_calendar(conf_dict: dict):
    cal = Calendar()
    cal.add('VERSION', '2.0')
    cal.add('PROID', vText('caaby.com'))  # noqa
    cal.add('CALSCALE', vText('GREGORIAN'))  # noqa
    """ GREGORIAN：表示使用公历。
        其他自定义取值：表示使用其他类型的日历系统。
    """
    cal.add('X-WR-CALNAME', vText(conf_dict.get("title")))  # noqa
    cal.add('X-APPLE-LANGUAGE', vText('zh'))  # noqa
    cal.add('X-APPLE-REGION', vText('CN'))  # noqa
    cal.add('X-WR-TIMEZONE', vText('Asia/Shanghai'))

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
            event = add_event_conf(name, tz.localize(start_date), anniversary)
            cal.add_component(event)

    put_object("birthday.ics", cal.to_ical())

    # with open('../calendars/birthday.ics', 'wb') as f:
    #    f.write(cal.to_ical())


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
