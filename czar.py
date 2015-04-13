SCRIPT_NAME = 'czar'
SCRIPT_AUTHOR = 'Samuel Damashek <samuel.damashek@gmail.com>'
SCRIPT_VERSION = '1.0'
SCRIPT_LICENSE = 'GPL3'
SCRIPT_DESC = 'Run czar commands natively in WeeChat'
SCRIPT_COMMAND = 'czar'

try:
    import weechat
except ImportError:
    print('This script must be run under WeeChat.')
    print('Get WeeChat now at: http://www.weechat.org/')
    exit(1)

import hashlib, time

czar_settings_default = {
    'key' : ('', 'key for signing messages'),
    }

czar_settings = {}

def commandtoken(nick, command):
    timestr = str(int(time.time()) // 300)
    return hashlib.sha1("{}{}{}{}".format(timestr, nick, command, czar_settings['key']).encode()).hexdigest()

def optoken(challenge, nick):
    return hashlib.sha1("{}{}{}".format(challenge, czar_settings['key'], nick).encode()).hexdigest()

def czar_config_cb(data, option, value):
    global czar_settings
    pos = option.rfind('.')
    czar_settings[option[pos+1:]] = value
    return weechat.WEECHAT_RC_OK

def czar_cmd_cb(data, buffer, args):
    args = args.split(' ')
    if args[0] == 'op':
        servername = (weechat.buffer_get_string(buffer, 'name').split('.'))[0]
        if len(args) > 2:
            plugin = weechat.buffer_get_string(buffer, 'plugin')
            name = weechat.buffer_get_string(buffer, 'name')
            name = '.'.join(name.split('.')[:-1]+[args[2]])
            buf_context = weechat.buffer_search(plugin, name)
        else:
            buf_context = buffer
        weechat.command(buf_context, '%s: opme %s' % (args[1], commandtoken(weechat.info_get('irc_nick',servername), 'opme:')))
    elif args[0] == 'cmd':
        servername = (weechat.buffer_get_string(buffer, 'name').split('.'))[0]
        cmdargs = ','.join(args[2:])
        token = commandtoken(weechat.info_get('irc_nick',servername), ':'.join([args[1],cmdargs]))
        weechat.command(buffer, ';;%s %s %s' % (args[1], token, ' '.join(args[2:])))

    else:
        weechat.prnt('', 'Invalid command in czar.')

    return weechat.WEECHAT_RC_OK

if __name__ == '__main__':
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, '', ''):
        version = weechat.info_get('version_number', '') or 0
        for option, value in czar_settings_default.items():
            if weechat.config_is_set_plugin(option):
                czar_settings[option] = weechat.config_get_plugin(option)
            else:
                weechat.config_set_plugin(option, value[0])
                czar_settings[option] = value[0]
            if int(version) >= 0x00030500:
                weechat.config_set_desc_plugin(option, '%s (default: "%s")' % (value[1], value[0]))

        weechat.hook_config('plugins.var.python.%s.*' % SCRIPT_NAME, 'czar_config_cb', '')

        #weechat.hook_print('', '', 'CHALLENGE', 1, 'czar_msg_cb', '')

        weechat.hook_command(SCRIPT_COMMAND, SCRIPT_DESC, 'op|cmd',
                ' op <nick> [channel]: request to be opped in the current channel or [channel] if specified, by <nick>\n'
                'cmd <cmd>:            issue <cmd> to all bots (do not specify the cmdchar)', 'op|cmd', 'czar_cmd_cb', '')
  
