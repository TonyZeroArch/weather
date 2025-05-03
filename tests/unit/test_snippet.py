from datetime import datetime


cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S%z")
print(cur_time)

if cur_time < "2025-04-18 14:00:00+00:00 ":
    print("yes")
else:
    print("no")
