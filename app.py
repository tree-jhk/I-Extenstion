# app.py

from flask import Flask, jsonify
from flask_cors import CORS
from learn_inha import login, get_courses, get_assignments, get_quiz, online_attendance_home, online_attendance_tab
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def fetch_assignments():
    driver = None
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")


    try:
        driver = webdriver.Chrome(options=chrome_options)
        link = 'https://learn.inha.ac.kr/'
        try:
            login(driver, link)
            print("logged in")

        except Exception as e:
            print("while logging in:", e)

    except Exception as e:
        print(f"An error occurred while opening driver: {e}")
        return {}, {}, {}
    
    try:
        courses = get_courses(driver)
        assignments = {}
        quizzes = {}
        lectures = {}
    except Exception as e:
        print(f"An error occurred while fetching assignments: {e}")
        return {}, {}, {}
    for course_name, course_link in courses.items():
            print(course_name)
            try:
                lectures_this_week = online_attendance_home(driver, course_link)
                if lectures_this_week:
                    lecture_link = online_attendance_tab(driver, lectures_this_week)
                    if lecture_link:
                        lectures[course_name] = lecture_link
            except Exception as e:
                print(f"An error occurred while getting lectures: {e}")
                return {}, {}, {}

            try:
                assignment_link = get_assignments(driver)
                if assignment_link:
                    assignments[course_name] = assignment_link
            
            except Exception as e:
                print(f"An error occurred while getting assignments: {e}")
                return {}, {}, {}
            
            try:
                quiz_link = get_quiz(driver)
                if quiz_link:
                    quizzes[course_name] = quiz_link
            except Exception as e:
                print(f"An error occurred while getting quizzes: {e}")
                return {}, {}, {}
        
    return assignments, quizzes, lectures    
    


@app.route('/assignments', methods=['GET'])
def handle_ajax_request():
    assignments_data = fetch_assignments()  # Fetch assignments on each request
    return jsonify(assignments_data)

if __name__ == '__main__':
    print("Starting Flask app")
    app.run(host="0.0.0.0", port=5000, use_reloader=False)  # Development server, not suitable for production
    print("ended")
