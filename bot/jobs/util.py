import traceback

from commons.classes import Job
from db.mongo import JobDatabase


def track(name):
    def outer(func):
        def inner(*args, **wargs):
            job = Job(_id=name)
            job.status = 'started'
            JobDatabase().save(job)

            try:
                job.result = func()
                job.status = 'finished'
            except:
                job.result = str(traceback.format_exc())
                job.status = 'error'

            job.finish()
            JobDatabase().save(job)

            return job.result
        return inner
    return outer
