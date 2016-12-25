CODES = {
    'bg_black': '\x1b[40m',
    'bg_blue': '\x1b[44m',
    'bg_bold_black': '\x1b[100m',
    'bg_bold_blue': '\x1b[104m',
    'bg_bold_cyan': '\x1b[106m',
    'bg_bold_green': '\x1b[102m',
    'bg_bold_purple': '\x1b[105m',
    'bg_bold_red': '\x1b[101m',
    'bg_bold_white': '\x1b[107m',
    'bg_bold_yellow': '\x1b[103m',
    'bg_cyan': '\x1b[46m',
    'bg_green': '\x1b[42m',
    'bg_purple': '\x1b[45m',
    'bg_red': '\x1b[41m',
    'bg_white': '\x1b[47m',
    'bg_yellow': '\x1b[43m',
    'black': '\x1b[30m',
    'blue': '\x1b[34m',
    'bold': '\x1b[01m',
    'bold_black': '\x1b[01;30m',
    'bold_blue': '\x1b[01;34m',
    'bold_cyan': '\x1b[01;36m',
    'bold_green': '\x1b[01;32m',
    'bold_purple': '\x1b[01;35m',
    'bold_red': '\x1b[01;31m',
    'bold_white': '\x1b[01;37m',
    'bold_yellow': '\x1b[01;33m',
    'cyan': '\x1b[36m',
    'fg_black': '\x1b[30m',
    'fg_blue': '\x1b[34m',
    'fg_bold_black': '\x1b[01;30m',
    'fg_bold_blue': '\x1b[01;34m',
    'fg_bold_cyan': '\x1b[01;36m',
    'fg_bold_green': '\x1b[01;32m',
    'fg_bold_purple': '\x1b[01;35m',
    'fg_bold_red': '\x1b[01;31m',
    'fg_bold_white': '\x1b[01;37m',
    'fg_bold_yellow': '\x1b[01;33m',
    'fg_cyan': '\x1b[36m',
    'fg_green': '\x1b[32m',
    'fg_purple': '\x1b[35m',
    'fg_red': '\x1b[31m',
    'fg_white': '\x1b[37m',
    'fg_yellow': '\x1b[33m',
    'green': '\x1b[32m',
    'purple': '\x1b[35m',
    'red': '\x1b[31m',
    'reset': '\x1b[0m',
    'white': '\x1b[37m',
    'yellow': '\x1b[33m',
}


NO_CODES = {k: '' for k in CODES}


def simple_colorizer(styles, style):
    colors = styles[style]

    def proc(data, level, codes):
        color = colors[level]
        return codes[color] + str(data) + codes['reset']

    return proc


def kv_colorizer(styles, style):
    key_style, val_style = style
    key_colors = styles[key_style]
    val_colors = styles[val_style]

    def proc(data, level, codes):
        key_color = key_colors[level]
        val_color = val_colors[level]
        return ' '.join(
            (codes[key_color] + str(key) + '=' +
             codes[val_color] + str(val) + codes['reset'])
            for key, val in data
        )

    return proc


PROC_MAP = {
    'created': simple_colorizer,
    'level_name': simple_colorizer,
    'name': simple_colorizer,
    'message': simple_colorizer,
    'extra': kv_colorizer,
}

DEFAULT_FMT = [
    ('created', 'message'),
    ('level_name', 'level'),
    ('name', 'message'),
    ('message', 'message'),
    ('extra', ['key', 'message']),
]

DEFAULT_STYLES = {
    'level': {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    },
    'message': {
        'DEBUG': 'cyan',
        'INFO': 'white',
        'WARNING': 'white',
        'ERROR': 'white',
        'CRITICAL': 'white',
    },
    'key': {
        'DEBUG': 'cyan',
        'INFO': 'cyan',
        'WARNING': 'cyan',
        'ERROR': 'cyan',
        'CRITICAL': 'cyan',
    }
}
