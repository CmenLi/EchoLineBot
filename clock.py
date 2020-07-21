from apscheduler.schedulers.blocking import BlockingScheduler
import pykachu
from datetime import datetime


class ScheduledEvent:
    def __init__(self, date_time, content):
        self.date_time = date_time
        self.content = content


__schedule = BlockingScheduler()


@__schedule.scheduled_job('interval', minutes=3)
def time_signal():
    print('報時: ' + datetime.now().ctime())
    print('尚有%d則提醒' % (len(__schedule.get_jobs()) - 1))


def set_notify(user, event):
    dt = datetime.strptime(event.date_time, '%Y-%m-%dT%H:%M')
    print(dt.ctime())

    __schedule.add_job(
        __remind, 'date',
        run_date=dt,
        args=[user, event.content]
    )
    print('successfully add one job')


def __notify_all(msg):
    pykachu.line_bot_api.broadcast(pykachu.TextSendMessage(text=msg))


def __remind(user, msg):
    print('notify: ' + user)
    pykachu.line_bot_api.push_message(user, pykachu.TextSendMessage(text='叮咚叮咚♪ 你有一則提醒: ' + msg))


if __name__ == '__main__':
    print('schedule start!')
    __schedule.start()
