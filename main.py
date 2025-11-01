import random
import json
import matplotlib.pyplot as plt

# ------------------------- Load Course Requirements from JSON -------------------------
with open("data.json", "r") as f:
    course_requirements = json.load(f)

rooms_lecture = ["R1", "R2", "R3"]
rooms_lab = ["Lab1", "Lab2", "Lab3"]
days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday"]
time_slots = ["8-10", "10-12", "12-2", "2-4", "4-6"]
all_slots = [(d, s) for d in days for s in time_slots]  # 5x5 = 25

# ------------------------- Expand Courses -------------------------
def expanded_courses():
    expanded = []
    for course, details in course_requirements.items():
        if "lectures" in details:
            for _ in range(details["lectures"]["hours"]):
                expanded.append({
                    "course": course,
                    "type": "lecture",
                    "instructor": details["lectures"]["lecturer"]
                })
        if "labs" in details:
            for _ in range(details["labs"]["hours"]):
                expanded.append({
                    "course": course,
                    "type": "lab",
                    "instructor": details["labs"]["ta"]
                })
    return expanded

# ------------------------- Create Chromosome -------------------------
def create_random_schedule():
    schedule = []
    slots = all_slots[:]
    random.shuffle(slots)
    expanded = expanded_courses()
    random.shuffle(expanded)
    for i in range(len(expanded)):
        lec_type = expanded[i]["type"]
        room = random.choice(rooms_lab if lec_type == "lab" else rooms_lecture)
        lec = {
            "course": expanded[i]["course"],
            "type": lec_type,
            "instructor": expanded[i]["instructor"],
            "room": room,
            "day": slots[i][0],
            "slot": slots[i][1]
        }
        schedule.append(lec)
    return schedule

# ------------------------- Fitness Function -------------------------
def calculate_fitness(schedule):
    penalty = 1
    room_slot = set()
    instructor_slot = set()

    for lec in schedule:
        rs_key = (lec["day"], lec["slot"], lec["room"])
        is_key = (lec["day"], lec["slot"], lec["instructor"])

        if rs_key in room_slot:
            penalty += 1
        else:
            room_slot.add(rs_key)

        if is_key in instructor_slot:
            penalty += 1
        else:
            instructor_slot.add(is_key)

    return 1 / (1 + penalty)

# ------------------------- Genetic Operators -------------------------
def crossover(p1, p2):
    point = random.randint(1, len(p1)-2)
    return p1[:point] + p2[point:]

def mutate(schedule, rate=0.3):
    for gene in schedule:
        if random.random() < rate:
            gene["day"], gene["slot"] = random.choice(all_slots)
            gene["room"] = random.choice(rooms_lab if gene["type"] == "lab" else rooms_lecture)
    return schedule

# ------------------------- Genetic Algorithm -------------------------
def genetic_algorithm(pop_size=50, generations=100):
    population = [create_random_schedule() for _ in range(pop_size)]
    fitness_history = []

    for gen in range(generations):
        population = sorted(population, key=calculate_fitness, reverse=True)
        best = population[0]
        best_fit = calculate_fitness(best)
        fitness_history.append(best_fit)
        if best_fit >= 0.99:
            break

        new_gen = population[:10]
        while len(new_gen) < pop_size:
            p1, p2 = random.sample(population[:25], 2)
            child = crossover(p1, p2)
            child = mutate(child)
            new_gen.append(child)
        population = new_gen

    return best, fitness_history

# ------------------------- Display Timetable -------------------------
def display_schedule(schedule):
    timetable = {d: {s: None for s in time_slots} for d in days}
    for lec in schedule:
        timetable[lec["day"]][lec["slot"]] = (lec["course"], lec["instructor"], lec["room"], lec["type"])

    width = 25
    print(f"{'Day':<12}", end="")
    for slot in time_slots:
        print(f"| {slot:^{width}}", end="")
    print("\n" + "-" * (12 + len(time_slots)*(width+3)))

    for day in days:
        print(f"{day:<12}", end="")
        for slot in time_slots:
            entry = timetable[day][slot]
            label = f"{entry[0]} ({'Lec' if entry[3] == 'lecture' else 'Lab'})" if entry else ""
            print(f"| {label:^{width}}", end="")
        print()
        print(f"{'':<12}", end="")
        for slot in time_slots:
            entry = timetable[day][slot]
            print(f"| {entry[1] if entry else '':^{width}}", end="")
        print()
        print(f"{'':<12}", end="")
        for slot in time_slots:
            entry = timetable[day][slot]
            print(f"| {entry[2] if entry else '':^{width}}", end="")
        print("\n" + "-" * (12 + len(time_slots)*(width+3)))

if __name__ == "__main__":
    best, fitness_history = genetic_algorithm()
    display_schedule(best)
    print("Final Fitness:", calculate_fitness(best))