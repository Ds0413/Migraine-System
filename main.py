import subprocess
import pandas as pd
from datetime import datetime, timedelta
import base64
import time
import calendar
import os

# --------------- Functions that will be reused multiple times --------------- #
pages_stack = []


# clear screen for every menu switches
def clear():
    time.sleep(1)
    sysname = os.name
    # for windows
    if sysname == 'nt':
        _ = os.system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')


# custom input to determine if user wants to return to previous menu
def custom_input(prompt):
    while True:
        user_input = input(prompt).strip()
        if user_input.upper() == 'B':
            if pages_stack:
                # Pop the function from the stack and assign it to previous_page
                previous_page = pages_stack.pop()
                previous_page()  # Call the function popped
            else:
                print("No previous page to go back to.")
            return None  # Indicate that the user chose to go back
        elif user_input == '':
            print("This input is required. Please enter a value or press 'B' to go back.")
        else:
            return user_input  # Non-empty input is returned


# get the name of user after checking the username / user id
def get_user_full_name(user_id):
    role = get_role(user_id)

    if role is None:
        print("Error: User role not found.")
        return None

    if role == "D":  # If the user is a doctor
        with open("doctor.txt", "r") as file:
            for line in file:
                id, name, clinic, email, phone = line.strip().split("|")
                if id == user_id:
                    return name
    elif role == "P":  # If the user is a patient
        with open("patient.txt", "r") as file:
            for line in file:
                id, name, email, phone = line.strip().split("|")
                if id == user_id:
                    return name

    return None  # Return None if the user is not found in the respective database


# get the role of user using user id
def get_role(user_id):
    with open("login.txt", "r") as file:
        for line in file:
            usr, _, role = line.strip().split("|")
            if usr == user_id:
                return role
    return None
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
# ----------------------------------- Menus ---------------------------------- #
# ---------------------------------------------------------------------------- #
# the main directory
def main_menu():
    pages_stack.clear() # clear the stack everytime when returned to main menu
    clear()

    print("****************************************************************************")
    print("*                   Welcome to Migraine Management Program                 *")
    print("****************************************************************************")
    print("----------------------------")
    print("|        Main Menu         |")
    print("----------------------------")
    print("Please choose what you would like to do.")
    main_menu_choice = input("For Login Type L, For Register Type R, To exit type E: ")

    if main_menu_choice.upper() == "L":
        pages_stack.append(main_menu)
        return Login()
    elif main_menu_choice.upper() == "R":
        pages_stack.append(main_menu)
        return Register()
    elif main_menu_choice.upper() == "E":
        print("Goodbye and take care.")
        exit()
    else:
        print("\nPlease only choose L or R, or E to exit.")
        return main_menu()


# the login page
def Login():
    clear()
    global username
    print("----------------------------")
    print("|          Login           |")
    print("----------------------------")

    username = custom_input("Enter your user ID : ")
    if username is None:
        return # return to main menu

    while True:
        password = custom_input("Enter password: ")
        if password is None:
            return # return to main menu

        user_found = False
        with open("login.txt", "r") as file:
            for line in file:
                userID, encoded_password, role = line.strip().split("|")
                decoded_pas = base64.b64decode(encoded_password).decode('utf-8')

                if userID == username:
                    user_found = True
                    if decoded_pas == password:
                        if role == "D":
                            print("Welcome, doctor")
                            return DoctorMenu()
                        elif role == "P":
                            print("Welcome, dear user")
                            return PatientMenu()
                    else:
                        print("\nInvalid Password. Please try again.")
                        break

            if not user_found:
                print("\nInvalid user ID, or user doesn't exists")
                time.sleep(1)
                break

    return Login()  # Try login again if any error occurs


# the registration page
def Register():
    clear()
    global userID
    print("----------------------------")
    print("|         Register         |")
    print("----------------------------")
    while True:  # Loop until a valid username is entered
        userID = custom_input("Enter a user ID (digits only): ")
        if userID is None:
            return  # return to main menu

        if userID.isdigit():  # Check if the username contains only digits
            if userID.startswith('0'):  # Check if the userID starts with a zero
                print("\nThe user ID should not start with zero. Please try again.")
            else:
                break  # userID is valid
        else:
            print("\nInvalid user ID, only digits are allowed. Please try again.")

    register_password = custom_input("Enter a password: ")
    if register_password is None:
        return # return to main menu

    match_password = custom_input("Confirm password: ")
    if match_password is None:
        return # return to main menu

    userID_exists = False
    file = open("login.txt", "r")
    userinfo = file.readlines()
    for i in userinfo:
        i = i.strip().split('|')
        userid = i[0]
        if userID == userid:
            userID_exists = True
            break
    file.close()
    if userID_exists:
        print("\nThis user ID has already been registered. Kindly log in.")
        time.sleep(1)
        return pages_stack.pop()()
    else:
        if register_password == match_password:
            # encrypt password
            encodedpassword = base64.b64encode(register_password.encode("utf-8"))
            # turn encrypted password into string to be stored in txt file because bytes cannot be stored in a text file, unless, txt file is opened in binary mode (rb)
            encoded_password = str(encodedpassword, "utf-8")
            file = open("login.txt", "a")
            file.write("\n")
            file.write(userID + "|" + encoded_password + "|P")
            file.close()
        else:
            print("\nPassword does not match, please try again.")
            return Register()

    print("Account created successfully, please enter your personal info.")
    patient_name = custom_input("Your full name: ")
    if patient_name is None:
        return # return to main menu

    patient_email = custom_input("Email: ")
    if patient_email is None:
        return # return to main menu
    
    while True:
        patient_phone = custom_input("Phone number (with your country code): ")
        if patient_phone is None:
            return # return to main menu

        if patient_phone.isdigit():
            break
        else:
            print("\nInvalid phone number, only digits are allowed, please try again.")

    file = open("patient.txt", "a")  # new file
    file.write("\n")
    file.write(
        userID + "|" + patient_name + "|" + patient_email + "|" + patient_phone)
    print("Account created successfully! Redirecting you to main menu...")
    file.close()

    return pages_stack.pop()()


# the patient menu directory
def PatientMenu():
    clear()
    print("----------------------------")
    print("|       Patient Menu       |")
    print("----------------------------")

    # to display the name of the current user
    name = get_user_full_name(username)
    if name:
        print(f'Welcome, {name}.')
    else:
        print("\nThere was an error during log in. Redirecting you back to main menu...")
        return main_menu()

    print("Please choose what you would like to do.")
    patient_menu_choice = input(
        "To update profile: Type 1\n"
        "To record migraine: Type 2\n"
        "To request appointment: Type 3\n"
        "To view report: Type 4\n"
        "To chat with a doctor: Type 5\n"
        "To view calendar: Type 6\n"
        "To view precaution recommendation: Type 7\n"
        "To logout: Type 8\n"
        "To exit: Type 9\n: ")

    if patient_menu_choice == "1":  # update profile
        pages_stack.append(PatientMenu)
        return update_profile()

    elif patient_menu_choice == "2":  # record migraine
        pages_stack.append(PatientMenu)
        return record_migraine(username)

    elif patient_menu_choice == "3":  # request appointment
        pages_stack.append(PatientMenu)
        return request_appointment()

    elif patient_menu_choice == "4":  # view report
        pages_stack.append(PatientMenu)
        return view_report()

    elif patient_menu_choice == "5":  # chat with doctor
        return chat_with_doctor(username)

    elif patient_menu_choice == "6":  # view calender
        pages_stack.append(PatientMenu)
        return view_calendar()

    elif patient_menu_choice == "7":  # view precautions
        pages_stack.append(PatientMenu)
        return view_precautions()

    elif patient_menu_choice == "8":  # logout
        print(f'Take care, {name}.')
        return main_menu()

    elif patient_menu_choice == "9":  # exit
        print("Exiting Program. Please check info in our program regularly.")
        exit()

    else:
        print("\nPlease only type the shown numbers")
        return PatientMenu()


# the doctor menu directory
def DoctorMenu():
    clear()
    print("----------------------------")
    print("|        Doctor Menu       |")
    print("----------------------------")

    # to display the name of doctor
    name = get_user_full_name(username)
    if name:
        print(f'Welcome, Dr {name}.')
    else:
        print("There was an error during log in. Redirecting you back to main menu...")
        return main_menu()

    print("Please choose what you would like to do.")
    doctor_menu_choice = input(
        "To manage appointments: Type 1\n"
        "To view calendar: Type 2\n"
        "To view report of patients: Type 3\n"
        "To chat with patients: Type 4\n"
        "To logout: Type 5\n"
        "To exit: Type 6\n: ")
    if doctor_menu_choice == "1": # manage appointment
        pages_stack.append(DoctorMenu)
        return manage_appointment()

    elif doctor_menu_choice == "2": # view calendar
        pages_stack.append(DoctorMenu)
        return view_calendar()

    elif doctor_menu_choice == "3": # view report
        pages_stack.append(DoctorMenu)
        return view_report()

    elif doctor_menu_choice == "4": # chat with patient
        print("Opening chat.")
        # Run the chat_client.py script in a new command prompt
        subprocess.run(["start", "cmd", "/k", "python", "chat_doctor.py"], shell=True)
        return DoctorMenu()

    elif doctor_menu_choice == '5': # logout
        print("See you next time doctor.")
        return main_menu()

    elif doctor_menu_choice == '6': # exit
        print("Goodbye.")
        exit()

    else:
        print("\nNot a valid option, please choose again")
        return DoctorMenu()
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
# ----------------------------- Patient functions ---------------------------- #
# ---------------------------------------------------------------------------- #
# update patient's profile
def update_profile():
    clear()
    print("----------------------------")
    print("|      Update Profile      |")
    print("----------------------------")
    # Read user details from the database
    with open("patient.txt", "r") as file:
        users = [line.strip().split('|') for line in file]

    # Find the user's current details
    user_details = next((user for user in users if user[0] == username), None)
    if not user_details:
        print("User not found.")
        return

    # display the current information
    print("Your current profile information:")
    print(f"ID: {user_details[0]}, Name: {user_details[1]}, Email: {user_details[2]}, Phone: {user_details[3]}\n")

    # Let user choose what to update
    print("What would you like to update?")
    update_choice = custom_input("1. Name\n2. Email\n3. Phone\nOr enter 'B' to go back\n: ")
    if update_choice is None:
        return # return to patient menu

    if update_choice == '1': # Update Name
        update_name = custom_input("Enter your new name: ")
        if update_name is None:
            return # return to patient menu
        user_details[1] = update_name

    elif update_choice == '2':  # Update Email
        update_email = custom_input("Enter your new email: ")
        if update_email is None:
            return 
        user_details[2] = update_email

    elif update_choice == '3': # Update Phone
        update_phone = custom_input("Enter your new phone number (digits only): ")
        if update_phone is None:
            return # return to patient menu
        if not update_phone.isdigit(): # check if contain non digits
            print("\nInvalid phone number. Phone number must be digits only.")
            return update_profile()
        user_details[3] = update_phone

    else:
        print("\nPlease choose a valid option to update.")
        return update_profile()
    
    # Write the changes to the user details file
    with open("patient.txt", "w") as file:
        for user in users:
            file.write('|'.join(user) + '\n')

    print("\nProfile updated successfully.")
    print("Updated profile information:")
    print(f"ID: {user_details[0]}, Name: {user_details[1]}, Email: {user_details[2]}, Phone: {user_details[3]}")
    time.sleep(1)
    return pages_stack.pop()()


# record migraine episodes
def record_migraine(username):
    clear()
    print("----------------------------")
    print("|   Migraine Assessment    |")
    print("----------------------------")

    # Get current date and time
    current_datetime = datetime.now()
    migraine_date = current_datetime.strftime("%d/%m/%Y %H:%M:%S")

    # Get user input
    while True:
        migraine_severity = custom_input(
            "On a scale of 1 to 10, how severe was the migraine?: ")
        if migraine_severity is None:
            return # return to patient menu
        if migraine_severity.isnumeric():
            migraine_severity = int(migraine_severity)
            if migraine_severity > 10 or migraine_severity < 1:
                print("\nInvalid range, please try again.")
            else:
                break
        else:
            print("\nInvalid input, please try again.")

    medications_used = custom_input(
        "List any medications used for the migraine: ")
    if medications_used is None:
        return # return to patient menu

    migraine_trigger = custom_input(
        "Enter the trigger that caused the migraine: ")
    if migraine_trigger is None:
        return # return to patient menu

    while True:
        water_intake = custom_input(
            "Enter the number of glasses of water you've had between current and last migraine episode: ")
        if water_intake is None:
            return  # return to patient menu
        elif not water_intake.isdigit():
            print("\nInvalid input. Please enter a valid number.")
        else:
            water_intake = int(water_intake)  # Convert valid input to an integer
            break

    # Create a DataFrame to store the migraine data
    migraine_data = pd.DataFrame({
        'mID': [get_next_migraine_id()],
        'userID': [username],
        'Date': [migraine_date],
        'Severity': [migraine_severity],
        'Water Intake': [water_intake],
        'Medications Used': [medications_used],
        'Trigger': [migraine_trigger]
    })

    # Define the file name
    file_name = 'migraine_data.xlsx'

    try:
        # Check if the Excel file exists in the current directory, if not, create a new one
        if not os.path.isfile(file_name):
            migraine_data.to_excel(file_name, index=False)
        else:
            # Append data to the existing Excel file
            existing_data = pd.read_excel(file_name)
            updated_data = pd.concat([existing_data, migraine_data], ignore_index=True)
            updated_data.to_excel(file_name, index=False)

        print("\nMigraine data has been logged successfully.")

    except PermissionError:
        print("\nFailed to write to the file. The file may be open in another program. Please close the file and try again.")
        time.sleep(1)

    return pages_stack.pop()()


# get id from migraine database
def get_next_migraine_id():
    # Read the existing data and find the next available ID
    file_path = 'migraine_data.xlsx'

    if os.path.isfile(file_path):
        existing_data = pd.read_excel(file_path)
        max_id = existing_data['mID'].max()
        next_id = max_id + 1 if not pd.isna(max_id) else 1
        return next_id
    else:
        return 1
        

# create a request for an appointment
def request_appointment():
    clear()
    print("-------------------------")
    print("|  Request Appointment  |")
    print("-------------------------")

    doctors = get_doctors_list()  # This should return a dictionary like {'Doctor Name': (doctor_id, 'Clinic')}

    print("Please choose a doctor from the list:")
    for idx, (doctor_name, (doctor_id, clinic)) in enumerate(doctors.items(), start=1):
        print(f"{idx}. Dr {doctor_name} - {clinic}")

    request_choice = custom_input("Which doctor would you like to have an appointment with? (or 'B' to go back): ")
    if request_choice is None:
        return  # return to patient menu

    try:
        request_choice = int(request_choice)
        doctor_name = list(doctors.keys())[request_choice - 1]
        doctor_id, clinic = doctors[doctor_name]
    except (ValueError, IndexError):
        print("\nInvalid choice. Please enter a valid number or 'B' to go back.")
        return request_appointment()

    now = datetime.now()
    while True:
        appointment_date = custom_input("Enter desired appointment date (dd/mm/yyyy) or 'B' to go back: ")
        if appointment_date is None:
            return  # return to patient menu

        appointment_time = custom_input("Enter desired appointment time (HH:MM) or 'B' to go back: ")
        if appointment_time is None:
            return  # return to patient menu

        try:
            appointment_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%d/%m/%Y %H:%M")
            if appointment_datetime <= now:
                print("\nPlease enter a future date and time for the appointment.")
            else:
                break
        except ValueError:
            print("\nInvalid date or time format. Please enter the date in dd/mm/yyyy format and time in HH:MM format.")

    print(f"Appointment with Dr {doctor_name} is set for {appointment_date} at {appointment_time}.")

    appointment_id = get_last_appointment_id() + 1

    with open('appointment.txt', 'a') as file:
        file.write(
            f"{appointment_id}|{username}|{doctor_id}|{clinic}|{appointment_datetime.strftime('%d/%m/%Y %H:%M')}|Pending\n")
    
    return pages_stack.pop()()


# get id from apppointment database
def get_last_appointment_id():
    try:
        with open('appointment.txt', 'r') as file:
            lines = file.readlines()
            if not lines:
                return 0  # Return 0 if the file is empty
            last_line = lines[-1]
            last_id = int(last_line.split('|')[0])
            return last_id
    except FileNotFoundError:
        return 0  # Return 0 if the file does not exist


# get list of doctors, will be used in multiple functions
def get_doctors_list():
    doctors = {}
    with open("doctor.txt", 'r') as file:
        for line in file:
            line = line.strip()
            if '|' in line:
                doctor_id, name, clinic, email, phone = line.split('|')
                # Add the doctor_id, name and clinic to the dictionary
                doctors[name] = (doctor_id, clinic)
    return doctors
    

# chat function for patient
def chat_with_doctor(username):
    # Get the list of doctors
    doctors = get_doctors_list()

    # Display the list of doctors
    for doctor_name, (doctor_id, clinic) in doctors.items():
        print(f"(ID: {doctor_id}) {doctor_name} | {clinic}")

    # Get the doctor choice from the user
    doc_choice = custom_input("Please enter the ID of the doctor you would like to chat with (or 'B' to go back): ").strip()

    if doc_choice is None:
        return  # return to patient menu
    
    # Find the doctor by ID
    doc_name = None
    for name, (id, clinic) in doctors.items():
        if id == doc_choice:
            doc_name = name
            break

    # Check if the doctor was found
    if doc_name is None:
        print("\nInvalid doctor ID.")
        return PatientMenu()

    folder_path = 'chat_logs'

    # Create the folder if it does not exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Create a chat log file based on username and doc_name
    chat_log_file = os.path.join(folder_path, f'{username}_{doc_name}_chatlog.txt')

    # Check if the chat log file exists, if not, create a new one
    if not os.path.isfile(chat_log_file):
        with open(chat_log_file, 'w'):
            pass  # This line ensures that the file is created even if it's empty

    print("Opening chat.")

    # Run the chat_server.py first
    subprocess.run(["start", "cmd", "/k", "python", "chat_server.py", doc_name], shell=True)
    # Run the chat_client.py script in a new command prompt
    subprocess.run(["start", "cmd", "/k", "python", "chat_patient.py", username], shell=True)
    return PatientMenu()


# display precaution recommendations
def view_precautions():
    clear()
    print("--------------------------------")
    print("|  Precaution Recommendations  |")
    print("--------------------------------")

    while True:
        # Get the age from user
        age_input = custom_input("Please enter your age or 'B' to go back: ")
        if age_input is None:
            return # return to patient menu
        if not age_input.isdigit() or int(age_input) <= 0:
            print("\nInvalid age. Please enter a valid number.")
            continue  # Ask for the age again
        age = int(age_input)  # Convert the valid input to an integer
        break  # Exit the loop when a valid age is entered

    precautions = []

    if age <= 18:
        precautions.append("Drink plenty of water.")
        precautions.append("Eat a healthy diet.")
        precautions.append("Engage in regular exercise.")

    elif age <= 60:
        precautions.append("Limit phone and screen usage.")
        precautions.append(
            "Manage stress levels through meditation or relaxation techniques.")

    else:
        precautions.append("Practice yoga for flexibility and relaxation.")
        precautions.append("Maintain a healthy diet.")
        precautions.append("Avoid smoking cigarettes.")

    # Display precaution recommendations
    print("\nPrecaution Recommendations:")
    for precaution in precautions:
        print("- " + precaution)

    input("Press any key to return to menu...")
    return pages_stack.pop()()
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
# ----------------------------- Doctor functions ----------------------------- #
# ---------------------------------------------------------------------------- #
def manage_appointment():
    clear()
    print("--------------------------")
    print("|  Manage Appointments   |")
    print("--------------------------")

    doctor_id = username
    # Read existing appointments from the file
    appointments = get_appointment_list(doctor_id)

    if not appointments:
        print("No appointments available.")
        input("Press any key to return to menu...")
        return pages_stack.pop()()

    # Display existing appointments with their current status
    print("Your Appointments:")
    for idx, appointment in enumerate(appointments, start=1):
        patient_name = get_user_full_name(appointment['patient_id'])
        print(
            f"{idx}. Patient: {patient_name}, Date and time: {appointment['datetime']}, Status: {appointment['status']}")

    # Ask the doctor to choose an appointment to manage
    appointment_choice = custom_input("Enter the number of the appointment you want to manage or 'B' to go back: ")
    if appointment_choice is None:
        return # return to doctor menu

    try:
        # Check if appointment selected is valid
        appointment_choice = int(appointment_choice)
        selected_appointment = None

        if 1 <= appointment_choice <= len(appointments):
            selected_appointment = appointments[appointment_choice - 1]
        else:
            print("\nInvalid choice. Please enter a valid number.")
            return manage_appointment()

        patient_name = get_user_full_name(selected_appointment['patient_id'])
        print(
            f"Selected Appointment: Patient: {patient_name}, Date and time: {selected_appointment['datetime']}, Status: {selected_appointment['status']}")

        # Choose whether to accept or decline
        new_status = custom_input("Enter the new status (Accept/Decline) or 'B' to go back: ").capitalize()
        if new_status is None:
            return # return to doctor menu

        if new_status not in ["Accept", "Decline"]:
            print("\nInvalid status. Please enter either 'Accept' or 'Decline'.")
            return manage_appointment()

        # Modify the status and update the appointment
        selected_appointment['status'] = new_status
        update_appointment(selected_appointment)

        print(f"Appointment status updated successfully.")
        return pages_stack.pop()()

    except (ValueError, IndexError):
        print("\nInvalid choice. Please enter a valid number.")
        return manage_appointment()
    

# Get appointment data in a list then return as dictionary
def get_appointment_list(user_id):
    appointments = []
    role = get_role(user_id)
    if role is None:
        print("Error: User role not found.")
        return []

    try:
        with open('appointment.txt', 'r') as file:
            for line in file:
                parts = line.strip().split('|')
                # For doctors, check if the doctor_id matches
                # For patients, check if the patient_id matches
                if (role == "D" and parts[2] == user_id) or (role == "P" and parts[1] == user_id):
                    # Create a dictionary for each appointment
                    appointment_dict = {
                        'appointment_id': parts[0],
                        'patient_id': parts[1],
                        'doctor_id': parts[2],
                        'clinic_name': parts[3],
                        'datetime': parts[4],
                        'status': parts[5]
                    }
                    appointments.append(appointment_dict)
        return appointments
    except FileNotFoundError:
        print("Appointments file not found.")
        return []


# update the selected appointment in the database
def update_appointment(selected_appointment):
    try:
        # Read all appointments from the file
        with open('appointment.txt', 'r') as file:
            appointments = file.readlines()

        # Update the selected appointment status
        updated_appointments = []
        for appointment in appointments:
            parts = appointment.strip().split('|')
            if parts[0] == selected_appointment['appointment_id']:
                # Replace only the status part
                parts[5] = selected_appointment['status']
                updated_appointments.append('|'.join(parts) + '\n')
            else:
                updated_appointments.append(appointment)

        # Write all appointments back to the file
        with open('appointment.txt', 'w') as file:
            file.writelines(updated_appointments)

    except Exception as e:
        print(f"An error occurred while updating the appointments: {e}")
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
# ---------------- Functions both patient and doctor will use ---------------- #
# ---------------------------------------------------------------------------- #
# view report function for both patient and doctor
def view_report():
    clear()
    print("------------------------")
    print("|        Report        |")
    print("------------------------")

    role = get_role(username)

    if role is None:
        print("Error: User role not found.")
        return
    
    # get data from migraine logs
    file_path = 'migraine_data.xlsx'
    if not os.path.isfile(file_path):
        print("No data found. Please log migraines first.")
        input("Press any key to return to the previous menu...")
        return pages_stack.pop()()

    data = pd.read_excel(file_path, dtype={'userID': str})  # Ensure Username is read as a string
    data['userID'] = data['userID'].str.strip()  # Remove any leading/trailing whitespace

    if role == "D":  # If the user is a doctor
        while True:  # Loop to allow viewing multiple reports
            patient_id_input = custom_input("Enter Patient ID or 'B' to go back: ")
            if patient_id_input is None:
                return # return to doctor menu
            if not patient_id_input.isdigit():
                print("\nInvalid Patient ID. Patient ID should only contain numbers.")
                continue  # Ask for the patient ID again

            patient_id = patient_id_input.strip()  # Use the entered patient ID for filtering

            # Filter data for the given patient ID
            filtered_data = data[data['userID'] == patient_id].copy()

            if filtered_data.empty:
                print(f"No data found for Patient ID {patient_id}.")
                print("Check if the ID is correct or if the user exists, or press 'B' to go back.")
                continue  # Allow re-entering another patient ID

            # Display the report for the filtered data
            display_report(filtered_data, patient_id)

            # After displaying the report, ask if the doctor wants to view report of another patient
            view_another = input("Would you like to view another report? (Y/N): ").upper()
            if view_another == 'N':
                print("Returning to menu...")
                return pages_stack.pop()() # Return to doctor menu

    elif role == "P":  # If the user is a patient
        patient_id = username
        filtered_data = data[data['userID'] == patient_id].copy()
        if not filtered_data.empty:
            display_report(filtered_data, patient_id)  # Display the report for the patient
        else:
            print("No data found. Please log migraines first.")
        input("Press any key to return to the previous menu...")
        return pages_stack.pop()() # Return to patient menu


# for displaying report after getting data
def display_report(filtered_data, patient_id):
    # Filter data for the last 7 days
    current_date = datetime.now()
    seven_days_ago = current_date - timedelta(days=7)

    # Convert 'Date' column to datetime type
    filtered_data['Date'] = pd.to_datetime(filtered_data['Date'], format="%d/%m/%Y %H:%M:%S")

    filtered_data_last_seven_days = filtered_data[
        (filtered_data['Date'] >= seven_days_ago) & (filtered_data['Date'] <= current_date)
    ]

    if filtered_data_last_seven_days.empty:
        print(f"No data found for Patient ID {patient_id} in the last 7 days.")
        return

    # Calculate average severity_level and total water intake
    average_severity = filtered_data_last_seven_days['Severity'].mean()
    total_water_intake = filtered_data_last_seven_days['Water Intake'].sum()

    # Display the results
    print("# ------------------------------------------------------------- #")
    print("Patient ID:", patient_id)
    print("\nMigraine logs in the last 7 days:")

    for index, entry in filtered_data_last_seven_days.iterrows():
        print(f"\nDate: {entry['Date']}")
        print(f"Severity: {entry['Severity']}")
        print(f"Water Intake: {entry['Water Intake']} glasses")
        print(f"Medications Used: {entry['Medications Used']}")
        print(f"Trigger: {entry['Trigger']}")

    print("\nAverage Severity: {:.2f}".format(average_severity))
    print("Total Water Intake: {} glasses".format(total_water_intake))
    print("# ------------------------------------------------------------- #")


# view calendar function for both patient and doctor
def view_calendar():
    clear()
    # get the current month and year
    now = datetime.now()
    year = now.year
    month_num = now.month
    user_role = get_role(username)  # Get the current user's role

    # Get the list of appointments for the user (doctor or patient)
    appointments = get_appointment_list(username)

    while True:
        print("----------------------------")
        print("|      Calendar Viewer     |")
        print("----------------------------")
        # Get the calendar matrix for the current month
        cal = calendar.monthcalendar(year, month_num)

        print(calendar.month_name[month_num], year)
        print("  Mo Tu We Th Fr Sa Su")
        for week in cal:
            week_str = "  "
            for day in week:
                if day != 0:
                    day_has_appointment = False
                    # Check if there's an appointment for the current date
                    for appointment in appointments:
                        appointment_datetime = datetime.strptime(appointment['datetime'], "%d/%m/%Y %H:%M")
                        if appointment_datetime.date().day == day and appointment_datetime.date().month == month_num and appointment_datetime.date().year == year and \
                                appointment['status'] == "Accept":
                            day_has_appointment = True
                            break
                    # highlight the date with color
                    week_str += f"\033[32m\033[1m{day:2}\033[0m " if day_has_appointment else f"{day:2} "
                else:
                    week_str += "   "
            print(week_str)

        # Display upcoming appointments line by line
        print(f"\nUpcoming Appointments:\n")
        upcoming_appointments = [appointment for appointment in appointments if
                                 datetime.strptime(appointment['datetime'], "%d/%m/%Y %H:%M") > now and appointment[
                                     'status'] == "Accept"]
        for appointment in upcoming_appointments:
            appointment_datetime = datetime.strptime(appointment['datetime'], "%d/%m/%Y %H:%M")
            if user_role == 'D':
                # If the user is a doctor, show the patient's name
                user_name = get_user_full_name(appointment['patient_id'])
            else:
                # If the user is a patient, show the doctor's name
                user_name = get_user_full_name(appointment['doctor_id'])
            print(
                f"Appointment on {appointment_datetime.strftime('%d/%m/%Y')}: {user_name}, {appointment['clinic_name']}, {appointment_datetime.strftime('%H:%M')}")

        # allow user to navigate through different months
        user_input = custom_input("\nPress P for previous month, N for next month\nOr press B to go back\n: ").upper()
        if custom_input is None:
            return # return to respective menu

        if user_input == "P": # previous month
            month_num -= 1
            if month_num == 0: # if month is 0 reset to 12
                month_num = 12
                year -= 1
            clear()
        elif user_input == "N": # next month
            month_num += 1
            if month_num == 13: # if month is 13 reset to 1
                month_num = 1
                year += 1
            clear()
        else:
            print("\nPlease enter a valid option.")
            return view_calendar()
# ---------------------------------------------------------------------------- #

print(main_menu())
