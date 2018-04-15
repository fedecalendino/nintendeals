# Standard
import logging
import time
import traceback

# Modules
from app import app

# Statics
from app.commons.config import *


LOG = logging.getLogger('main')


def main():
    LOG.info(' Start up')
    LOG.info(' ')

    LOG.info("  Mongo: {}".format(MONGODB_URI))
    LOG.info("  Reddit Username: {}".format(REDDIT_USERNAME))
    LOG.info(' ')

    while True:
        LOG.info(' Running Bot')

        try:
            app.run()
        except Exception as e:
            LOG.error(e)
            traceback.print_exc()

        LOG.info(' Sleeping for {} seconds'.format(UPDATE_FREQUENCY))
        time.sleep(UPDATE_FREQUENCY)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    main()
