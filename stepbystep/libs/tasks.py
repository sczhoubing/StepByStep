from stepbystep import app
from celery import Celery

from crawl import AccountCrawler
from stepbystep.models import AccountItem


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)


@celery.task()
def account_crawler(origin_oj, username):
    crawler = AccountCrawler()
    crawler.crawl(
        origin_oj,
        username,
    )


@celery.task()
def sdut_schedule():
    for account in AccountItem.objects(origin_oj='sdut').all():
        account_crawler(account.origin_oj, account.username)


@celery.task()
def poj_schedule():
    for account in AccountItem.objects(origin_oj='poj').all():
        account_crawler(account.origin_oj, account.username)


@celery.task()
def hduoj_schedule():
    for account in AccountItem.objects(origin_oj='hduoj').all():
        account_crawler(account.origin_oj, account.username)


@celery.task()
def rating_schdule():
    from mongoengine import Q
    for account in AccountItem.objects(
                Q(origin_oj='bestcoder') |
                Q(origin_oj='topcoder') |
                Q(origin_oj='codeforces')
            ).all():
        account_crawler(account.origin_oj, account.username)
