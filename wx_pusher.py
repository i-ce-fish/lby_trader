# -*- encoding: UTF-8 -*-

import settings
from wxpusher import WxPusher



def wx_push(msg):
    if settings.config['push']['enable']:
        response = WxPusher.send_message(msg, uids=[settings.config['push']['wxpusher_uid']],
                                         token=settings.config['push']['wxpusher_token'])
        return response






