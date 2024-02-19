import csv
import random

# Step 1: Import the necessary modules

# Step 2: Open the CSV file in read mode
filename = "Apr.csv"  # Replace 'your_file.csv' with your actual file path
with open(filename, 'r', newline='') as csvfile:
    # Step 3: Read all rows into a list
    reader = csv.reader(csvfile)
    rows = [row for row in reader]

    # Step 4: Generate a random index
    random_index = random.randint(0, len(rows) - 1)

    # Step 5: Retrieve the row at the random index
    random_row = rows[random_index]

    # Step 6: Print or process the random row
    print(random_row)