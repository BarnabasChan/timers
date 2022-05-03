import json
import time
from datetime import date, timedelta
from sys import exit, argv

NAMES_FILENAME = './data/names.txt'
SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = SECONDS_IN_MINUTE * 60

def main(yesterday:bool):
    global data, filename, names, start_times, dateInMonth

    day = date.today() - timedelta(days=1) if yesterday else date.today()
    filename = day.strftime("./data/%Y %B.json")
    dateInMonth = day.strftime("%d")

    # load data from earlier today
    try:
        with open(filename) as file:
            data = json.load(file)
    except json.JSONDecodeError:
        data = {}
    except FileNotFoundError:
        data = {}
        open(filename, 'x').close()
    if str(dateInMonth) not in data:
        data[dateInMonth] = {}
        
    with open(NAMES_FILENAME) as file:
        names = set(name.strip() for name in file.readlines())
    for name in names:
        if name not in data[dateInMonth]:
            data[dateInMonth][name] = 0
    print(data[dateInMonth])

    # time where timer started
    start_times = {}

    while True:
        command = input("> ")
        tokens = command.split()


        if tokens[0] == 'eval':
            print(eval(command[command.index("eval")+4:]))
            continue
        
        execute(tokens)


def execute(tokens:list[str]):
    if not tokens: return
    match tokens[0]:
        case 'quit':
            execute(tokens[1:])
            save()
            exit()
        
        case 'save':
            save()
        
        case 'execute':
            execute(tokens[1:])

        case 'list':
            list_timers()

        case 'create':
            if len(tokens) != 2: return print("Invalid amount of argument for command 'create' (expected 1)")
            create(tokens[1])
        
        case 'delete':
            if len(tokens) != 2: return print("Invalid amount of argument for command 'delete' (expected 1)")
            delete(tokens[1])

        case 'start':
            if len(tokens) != 2: return print("Invalid amount of argument for command 'start' (expected 1)")
            start(tokens[1])
        
        case 'stop':
            if len(tokens) == 1: stop_all()
            elif len(tokens) == 2: stop(tokens[1])
            else: return print("Invalid amount of argument for command 'stop' (expected 1 or 2)")

        case 'get':
            if len(tokens) != 2: return print("Invalid amount of argument for command 'get' (expected 1)")
            get(tokens[1])
            
        

def create(name:str):
    global data, names
    if name in names: return print(f"Name '{name}' already exists")
    names.add(name)
    data[dateInMonth][name] = 0


def delete(name:str):
    if name not in names:
        print(f"Invalid name {name} (does not exist)")
        return
    names.remove(name)
    del data[dateInMonth][name]


def start(name:str):
    if name not in names: return print(f"Invalid name {name} (you can use the 'create' command to add a new name)")
    if name in start_times:
        print(f"Timer '{name}' has already started")
    else:
        start_times[name] = time.time()


def stop(name:str):
    if name not in names: return print(f"Invalid name {name} (you can use the 'create' command to add a new name)")
    if name not in start_times:
        print(f"Timer '{name}' has not been started yet")
    else:
        time_passed = time.time() - start_times[name]
        data[dateInMonth][name] = time_passed if name not in data[dateInMonth] else data[dateInMonth][name] + time_passed
        print(f"{name} | passed: {time_convert(time_passed)} | total: {time_convert(data[dateInMonth][name])}")
        del start_times[name]


def stop_all():
    for name in tuple(start_times):
        stop(name)


def list_timers():
    max_len = max(map(len, names))
    curr = time.time()
    for name, value in data[dateInMonth].items():
        if name in start_times:
            value += curr - start_times[name]
        print(f"{name}{' ' * (max_len - len(name))} | {time_convert(value)}")

def get(name:str):
    if name not in names:
        print(f"Invalid name {name} (you can use the 'add' command to add a new name)")
    if name not in start_times:
        print(f"{name} | total: {time_convert(data[dateInMonth][name])}")
    else:
        time_passed = time.time() - start_times[name]
        print(f"{name} | passed: {time_convert(time_passed)} | total: {time_convert(data[dateInMonth][name] + time_passed)}")


def save():
    curr = time.time()
    if start_times:
        tmp = dict(data)
        for name, start_time in start_times.items():
            if name in tmp:
                tmp[name] += curr - start_time
            else:
                tmp[name] = curr - start_time
    else: tmp = data
    print(tmp)
    with open(filename, 'w') as file:
        json.dump(tmp, file)
    with open(NAMES_FILENAME, 'w') as file:
        names_str = '\n'.join(sorted(names))
        file.write(names_str)
        file.truncate()


def time_convert(seconds:float) -> str:
    seconds = int(seconds)
    hours, seconds = seconds // SECONDS_IN_HOUR, seconds % SECONDS_IN_HOUR
    minutes, seconds = seconds // SECONDS_IN_MINUTE, seconds % SECONDS_IN_MINUTE
    return f"{' '*(2-len(str(hours)))}{hours} hrs {' '*(2-len(str(minutes)))}{minutes} mins {' '*(2-len(str(seconds)))}{seconds} secs"


if __name__ == "__main__":
    main('-y' in argv)