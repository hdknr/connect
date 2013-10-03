# -*- coding: utf-8 -*-
#
from django.utils.timezone import now 
import django.dispatch
#
import os
import traceback
import syslog
#
__all__ = ['LOGGING','applog_rotated',]

#logs signal
applog_rotated= django.dispatch.Signal(providing_args=["rotated_at", ])

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# 
# - level -
# DEBUG     : Low level system information for debugging purposes
# INFO      : General system information
# WARNING   : Information describing a minor problem that has occurred.
# ERROR     : Information describing a major problem that has occurred.
# CRITICAL  : Information describing a critical problem that has occurred.


_LOG_DIR = os.environ.get('DJ_LOGGER_DIR',
        os.path.join( os.path.dirname(os.path.abspath(__file__)) ,'logs') 
    )   #:TODO: specify evnironment in LIVE

_LOG_FILE = lambda signature : os.path.join( _LOG_DIR,signature +".log" )

_LOG_ROOT = {
        'handlers': ['file'],
        'level': os.environ.get('DJ_LOGGER_LEVEL','DEBUG'),               #:TODO: other than DEBUG on LIVE
        'propagate': True, }

_LOG_FORMATTERS = { 
        'parsefriendly': { 
             'format': '[%(levelname)s] %(asctime)s - M:%(pathname)s, P:%(process)d, T:%(thread)d, MSG:%(message)s',
             'datefmt': '%d/%b/%Y:%H:%M:%S %z',
         }, 
    }

_LOG_FILTERS = {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    }

_LOG_HANDLER_MAIL_ADMINS = {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }

_LOG_HANDLER_FILE= {
            'level':    'DEBUG',
            'class':    'app.logs.AppFileLogHandler', 
            'formatter':'parsefriendly',
            'when':     'midnight',
#            'when': 'S',
#            'interval':  2,
            'filename': os.environ.get('DJ_LOGGER_FILE',_LOG_FILE('apps')),   #:TODO: specify evnironment in LIVE
    }

from logging.handlers import TimedRotatingFileHandler

class AppFileLogHandler(TimedRotatingFileHandler):
    def doRollover(self):
        super(AppFileLogHandler,self).doRollover()
        #:
        try:
            applog_rotated.send( self,rotated_at = now() )    #:シグナル送ります
        except:
            syslog.openlog('APP')
            syslog.syslog(syslog.LOG_ALERT, traceback.format_exc() )
            syslog.closelog()
#

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'root': _LOG_ROOT,          #: root logger for logging.getLoagger() without a logger name
    'formatters': _LOG_FORMATTERS,
    'filters': _LOG_FILTERS,

    'handlers': {
        'mail_admins': _LOG_HANDLER_MAIL_ADMINS,
        'file': _LOG_HANDLER_FILE,
    },

    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
   } 
}
