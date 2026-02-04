import datetime


if __name__ == '__main__':
    dt = datetime.datetime(
        year=2026, month=3, day=1,
        hour=16, minute=32
    )
    print(dt - datetime.timedelta(days=30) + datetime.timedelta(days=30))