import traceback

from commons.classes import Job
from db.mongo import JobDatabase


def track(name, history=False):
    def outer(func):
        def inner(*args, **wargs):
            run = None
            job = Job(_id=f'_{name}')
            job.name = name
            
            JobDatabase().save(job)

            if history:
                run = Job(_id=f'{name}_{job.start.strftime("%d/%m/%Y_%H:%M:%S")}')
                run.name = name

                JobDatabase().save(run)

            try:
                result = func()
                status = 'finished'
            except:
                result = str(traceback.format_exc())
                status = 'error'

            job.finish(status=status, result=result)
            JobDatabase().save(job)

            if history and run:
                run.finish(status=status, result=result)
                JobDatabase().save(run)

            return result
        return inner
    return outer
