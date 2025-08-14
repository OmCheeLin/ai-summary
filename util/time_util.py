from datetime import timedelta


def ms_to_format_str(ms):
    """把毫秒转为 HH:MM:SS"""
    seconds = ms / 1000
    # 用 timedelta 得到小时、分钟、秒
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_str_to_ms(time_str):
    """把 HH:MM:SS 转成毫秒"""
    h, m, s = map(int, time_str.split(':'))
    return (h * 3600 + m * 60 + s) * 1000
