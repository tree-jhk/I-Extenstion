# learn_inha.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from datetime import datetime, timedelta
from dateutil.parser import parse, ParserError


def due_thisweek(duedate):
    today = datetime.now() + timedelta(days=0)
    week_start = today - timedelta(days=today.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=1, microsecond=0)
    week_end = week_start + timedelta(days=7)

    if week_start <= duedate <= week_end and today <= duedate:
        return True
    else:
        return False
 

def login(driver, link):
    print("Navigating to login page")
    try:
        driver.get(link)
    except WebDriverException:
        print("can't navigate to link")
    try:
        username_input = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.NAME, 'username'))
        )
        id = ''  # id 입력
        pw = ''  # 비밀번호 입력

        username_input.send_keys(id)
        driver.find_element(By.NAME, 'password').send_keys(pw)
        driver.find_element(By.NAME, 'loginbutton').click()
        print("Login submitted")
    except TimeoutException:
        print("Login elements not found")
    except Exception as e:
        print(f"An error occurred during login: {e}")


def get_courses(driver):
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'course_label_re_02'))
        )
        course_list = driver.find_elements(By.CLASS_NAME, 'course_label_re_02')
        course_list += driver.find_elements(By.CLASS_NAME, 'course_label_re_01')
        courses = {}
        for course in course_list:
            course_name = course.find_element(By.TAG_NAME, 'h3').get_attribute('textContent')
            course_link = course.find_element(By.CLASS_NAME, 'course_link').get_attribute('href')
            courses[course_name] = course_link
        print("Courses retrieved")
        return courses
    except NoSuchElementException as e:
        print(f"Course elements not found: {e}")
    except Exception as e:
        print(f"An error occurred while fetching courses: {e}")


def get_assignments(driver):
    assignments_left = []

    try:
        # Check if the '과제' link exists
        #  assignment_exist = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.LINK_TEXT, '과제')))
        assignment_exist = driver.find_element(By.LINK_TEXT, '과제')
        driver.execute_script('arguments[0].click();', assignment_exist)

        try:
            # Wait for the table to be present
            table = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                    ".table.table-bordered.generaltable")))

            rows = table.find_elements(By.TAG_NAME, "tr")[1:]
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 5:
                    due_date_str = cells[2].text.strip()
                    due_date = parse(due_date_str)

                    if due_thisweek(due_date):
                        assignment_status = cells[3].text.strip()
                        link_element = cells[1].find_element(By.TAG_NAME, "a")
                        assignment_link = link_element.get_attribute('href')
                        if assignment_status == '미제출':
                            assignments_left.append(assignment_link)

            return assignments_left

        except TimeoutException:
            print("Assignments table not found")
            return []
    except NoSuchElementException:
        print("No such element found 과제")
        return []
    

def get_quiz(driver):
    quizzes_left = []

    try:
        # Check if the '퀴즈' link exists
        # quiz_exist = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.LINK_TEXT, '퀴즈')))
        quiz_exist = driver.find_element(By.LINK_TEXT, '퀴즈')
        driver.execute_script('arguments[0].click();', quiz_exist)
        print("quiz exists")
    except NoSuchElementException:
        # If the link doesn't exist, return an empty list
        print("퀴즈 link not found")
        return []

    try:
        # Wait for the table to be present
        table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                ".table.table-bordered.generaltable")))
    except TimeoutException:
        # If the table doesn't exist, return an empty list
        print("Quizzes table not found")
        return []

    # Process the table to find quizzes due this week
    rows = table.find_elements(By.TAG_NAME, "tr")[1:]
    quizzes_thisweek = []

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 4:
            due_date_str = cells[2].text.strip()
            due_date = parse(due_date_str)

            if due_thisweek(due_date):
                try:
                    quiz_link_element = cells[1].find_element(By.TAG_NAME, "a")
                    quiz_link = quiz_link_element.get_attribute('href')
                    quizzes_thisweek.append(quiz_link)
                except NoSuchElementException:
                    print("Quiz link not found within cell")
                    continue

    # Process quizzes due this week
    for quiz in quizzes_thisweek:
        try:
            driver.get(quiz)
            print("got in quiz")
            # search the whole page for the word "제출됨"
            page_source = driver.page_source
            if "제출됨" not in page_source:
                # If "제출됨" is not found on the page, consider the quiz not submitted
                quizzes_left.append(quiz)
                continue
            else:
                # If "제출됨" is found on the page, consider the quiz submitted
                continue

        except Exception as e:
            print(f"An error occurred while processing quiz link: {e}")
            continue

    return quizzes_left
    

def online_attendance_home(driver, link):
    try:
        driver.get(link)
    except WebDriverException:
        return "Can't navigate to link"

    exclude_current = driver.find_element(By.CLASS_NAME, "total_sections")
    rows = exclude_current.find_elements(By.CLASS_NAME, "text-ubstrap")

    not_video = []
    for i, row in enumerate(rows):
        ancestor_class = row.find_element(By.XPATH, "./ancestor::div[contains(@class, 'activityinstance')]")
        lecture_type = ancestor_class.find_element(By.CLASS_NAME, "accesshide").text
        if lecture_type != "동영상":
            not_video.append(i)

    if not_video:
        for i in reversed(not_video):
            del rows[i]

    if not rows:
        return None

    lectures_this_week = {}

    for row in rows:
        due_date_str = row.text.split("~")[1].strip()
        try:
            due_date = parse(due_date_str)
        except ParserError:
            print("This element is not a date")
            continue

        if due_thisweek(due_date):
            ancestor_class = row.find_element(By.XPATH, "./ancestor::div[contains(@class, 'activityinstance')]")
            lecture_title = ancestor_class.find_element(By.CLASS_NAME, "instancename").text.split('\n')[0]
            lecture_link = ancestor_class.find_element(By.TAG_NAME, "a").get_attribute("href")
            lectures_this_week[lecture_title] = lecture_link

    return lectures_this_week if lectures_this_week else None


def online_attendance_tab(driver, lectures_this_week):
    if not lectures_this_week:
        return None

    lecture_links = []
    if isinstance(lectures_this_week, dict):
        progress = driver.find_element(By.LINK_TEXT, '온라인출석부')
        driver.execute_script('arguments[0].click();', progress)

        try:
            table = driver.find_element(By.CLASS_NAME, "table-bordered.user_progress_table")
            rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip table header row
        except NoSuchElementException:
            print("No rows in attendance table")
            return None

        attended = []

        for title in lectures_this_week.keys():
            attendance_status = ''
            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 4 and (title in cells[1].text.strip() or title in cells[0].text.strip()):
                        if "text-center" in cells[0].get_attribute("class"):
                            attendance_status = cells[4].text.strip()
                        elif "text-left" in cells[0].get_attribute("class"):
                            attendance_status = cells[3].text.strip()

                        if attendance_status == 'O':
                            print("Attended:", title)
                            attended.append(title)
                            break
                except NoSuchElementException:
                    print("No cells in row")
                    continue

        for title in attended:
            del lectures_this_week[title]

        lecture_links = list(lectures_this_week.values())

    return lecture_links if lecture_links else None
