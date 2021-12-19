# -*- coding:utf-8 -*-
from apscheduler.schedulers.background import BackgroundScheduler


"""
构建说明：
id：指定作业的唯一ID
name：指定作业的名字
trigger：apscheduler定义的触发器，用于确定Job的执行时间，根据设置的trigger规则，计算得到下次执行此job的时间， 满足时将会执行
executor：apscheduler定义的执行器，job创建时设置执行器的名字，根据字符串你名字到scheduler获取到执行此job的 执行器，执行job指定的函数
max_instances：执行此job的最大实例数，executor执行job时，根据job的id来计算执行次数，根据设置的最大实例数来确定是否可执行
next_run_time：Job下次的执行时间，创建Job时可以指定一个时间[datetime],不指定的话则默认根据trigger获取触发时间
misfire_grace_time：Job的延迟执行时间，例如Job的计划执行时间是21:00:00，但因服务重启或其他原因导致21:00:31才执行，如果设置此key为40,则该job会继续执行，否则将会丢弃此job
coalesce：Job是否合并执行，是一个bool值。例如scheduler停止20s后重启启动，而job的触发器设置为5s执行一次，因此此job错过了4个执行时间，如果设置为是，则会合并到一次执行，否则会逐个执行
func：Job执行的函数
args：Job执行函数需要的位置参数
kwargs：Job执行函数需要的关键字参数
"""


def timetask(job, hour, minute, arg=None):
    """

    :param job:定时任务函数名
    :param hour:定时时间的小时
    :param minute:定时时间的分钟
    :param arg: 调用参数
    :return:
    """
    sched = BackgroundScheduler()
    sched.add_job(job, 'cron', day_of_week='mon-fri', hour=hour, minute=minute, end_date='2024-05-30', args=arg)
    sched.start()
    return True
