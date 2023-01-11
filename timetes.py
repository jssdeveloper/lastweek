from datetime import datetime

# dd/mm/YY H:M:S
date = datetime.now().strftime("%d/%m/%Y")
time = datetime.now().strftime("%H:%M:%S")
print(date)
print(time)