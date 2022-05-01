import json
import time
from datetime import date
from sys import getsizeof

NAMES_FILENAME = './data/names.txt'
SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = SECONDS_IN_MINUTE * 60

def main():
    global data, filename, names, start_times

    today = date.today()
    filename = today.strftime("./data/%Y %B.json")
    dateInMonth = today.strftime("%d")

    # load data from earlier today
    try:
        with open(filename) as file:
            data = json.load(file)
    except json.JSONDecodeError:
        data = {}
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
        match len(tokens):

            case 1:
                match tokens[0]:
                    case 'quit':
                        save()
                        break
                    
                    case 'save':
                        save()
                    
                    case 'list':
                        max_len = max(map(len, names))
                        curr = time.time()
                        for name, value in data[dateInMonth].items():
                            if name in start_times:
                                value += curr - start_times[name]
                            print(f"{name}{' ' * (max_len - len(name))} | {time_convert(value)}")

            case 2:
                if tokens[0] == 'eval':
                    print(eval(command[command.index("eval")+4:]))
                    continue

                name = tokens[1]
                
                match tokens[0]:

                    case 'add':
                        names.add(name)
                        data[dateInMonth][name] = 0

                    case 'remove':
                        if name not in names:
                            print(f"Invalid name {name} (does not exist)")
                            continue
                        names.remove(name)
                        del data[dateInMonth][name]

                    case 'start':
                        if name not in names:
                            print(f"Invalid name {name} (you can use the 'add' command to add a new name)")
                            continue
                        if name in start_times:
                            print(f"Timer '{name}' has already started")
                        else:
                            start_times[name] = time.time()

                    case 'stop':
                        if name not in names:
                            print(f"Invalid name {name} (you can use the 'add' command to add a new name)")
                            continue
                        if name not in start_times:
                            print(f"Timer '{name}' has not been started yet")
                        else:
                            time_passed = time.time() - start_times[name]
                            data[dateInMonth][name] = time_passed if name not in data[dateInMonth] else data[dateInMonth][name] + time_passed
                            print(f"{name} | passed: {time_convert(time_passed)} | total: {time_convert(data[dateInMonth][name])}")
                            del start_times[name]

                    case 'get':
                        if name not in names:
                            print(f"Invalid name {name} (you can use the 'add' command to add a new name)")
                            continue
                        if name not in start_times:
                            print(f"{name} | total: {time_convert(data[dateInMonth][name])}")
                        else:
                            time_passed = time.time() - start_times[name]
                            print(f"{name} | passed: {time_convert(time_passed)} | total: {time_convert(data[dateInMonth][name] + time_passed)}")

            case _:
                print(f"Unknown command '{command}'")


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
    main()