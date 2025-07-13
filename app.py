from ics import Calendar
from collections import defaultdict

classes_by_day = defaultdict(list)
current_classes = []

class ClassEvent:
    def __init__(self, name, start, end, location):
        self.name = name
        self.start = start
        self.end = end
        self.location = location
        current_classes.append(self)

# Load and parse .ics file
with open('schedule.ics', 'r') as file:
    calendar_data = file.read()

calendar = Calendar(calendar_data)

weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Loop through all calendar events
for event in calendar.events:
    print("📚 Name:", event.name)
    print("🕒 Start:", event.begin)
    print("🕒 End:", event.end)
    print("📍 Location:", event.location)
    print("-" * 40)

    # Create a ClassEvent object
    class_obj = ClassEvent(
        name=event.name,
        start=event.begin,
        end=event.end,
        location=event.location
    )

    # Get the day name (e.g., "Monday")
    day_index = event.begin.weekday()
    day_name = weekday_names[day_index]

    # Add this class to the list for that day
    classes_by_day[day_name].append(class_obj)

# Print how many events were parsed
print(len(current_classes))  # total number of classes
print(current_classes[0].name)  # name of the first class
for day in weekday_names:
    print(f"\n📅 {day}")
    for c in classes_by_day[day]:
        print(f"  - {c.name} at {c.start.time()} in {c.location}")
