// Function to check if the current page is the home page
function isHomePage() {
    return window.location.href === 'https://learn.inha.ac.kr/';
}
// Function to append buttons immediately after the course title within the <h3> tag
function appendButtonsAfterCourseTitle(titleElement, link, buttonType) {
    // Create the appropriate button based on the buttonType
    let imgSrc, altText;
    switch (buttonType) {
        case 'blue':
            imgSrc = 'chrome-extension://lcehaibjfdahdhlcgijddcpdenaoboco/images/redbutton.png';
            altText = '과제';
            break;
        case 'red':
            imgSrc = 'chrome-extension://lcehaibjfdahdhlcgijddcpdenaoboco/images/redbutton.png';
            altText = '퀴즈';
            break;
        case 'black':
            imgSrc = 'chrome-extension://lcehaibjfdahdhlcgijddcpdenaoboco/images/blackbutton.png';
            altText = '강의';
            break;
        default:
            console.error('Invalid button type');
            return;
    }

    const img = document.createElement('img');
    img.src = imgSrc;
    img.alt = altText;
    img.height = 25;
    img.style.width = 'auto';    

    const anchor = document.createElement('a');
    anchor.href = link;
    anchor.style.display = 'inline-block';
    anchor.style.padding = '0';
    anchor.style.margin = '0';
    anchor.style.border = 'none';
    anchor.classList.add('custom-button'); // Add a class for easier selection
    anchor.appendChild(img);

    // Append the anchor element (button) after the course title text node
    titleElement.appendChild(document.createTextNode(' ')); // Add space before button
    titleElement.appendChild(anchor);
}




// Modify displaySavedButtons and fetchAndUpdateButtons functions to check if it's the home page
function displaySavedButtons() {
    if (!isHomePage()) return; // Exit if not on the home page

    const savedData = JSON.parse(localStorage.getItem('courseAssignments'));
    if (savedData) {
        console.log("got saved function");
        const courseTitles = document.querySelectorAll('.course-title');
        courseTitles.forEach(title => {
            const courseTitleText = title.querySelector('h3').textContent.trim();
            if (courseTitleText in savedData[0]) {
                const assignmentLinks = savedData[0][courseTitleText];
                assignmentLinks.forEach(link => {
                    appendButtonsAfterCourseTitle(title.querySelector('h3'), link, 'blue');
                });
            }
            if (courseTitleText in savedData[1]) {
                const quizLinks = savedData[1][courseTitleText];
                quizLinks.forEach(link => {
                    appendButtonsAfterCourseTitle(title.querySelector('h3'), link, 'red');
                });
            }
            if (courseTitleText in savedData[2]) {
                const lectureLinks = savedData[2][courseTitleText];
                lectureLinks.forEach(link => {
                    appendButtonsAfterCourseTitle(title.querySelector('h3'), link, 'black');
                });
            } else {
                console.log("Couldn't match the course title to saved data");
            }
        });
    }
}



function fetchAndUpdateButtons() {
    if (!isHomePage()) return; // Exit if not on the home page

    // Fetch data from the server and update local storage
    fetch('http://127.0.0.1:5001/assignments')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                return response.json();
            } else {
                throw new Error('Received non-JSON response');
            }
        })
        .then(data => {
            // Process the retrieved data here
            console.log(data);

            // Save the new data to local storage
            localStorage.setItem('courseAssignments', JSON.stringify(data));

            // Clear existing buttons
            const existingButtons = document.querySelectorAll('.custom-button');
            existingButtons.forEach(button => button.remove());

            // Create and append new buttons
            const courseTitles = document.querySelectorAll('.course-title');
            courseTitles.forEach(title => {
                const courseTitleText = title.querySelector('h3').textContent.trim();
                if (courseTitleText in data[0]) {
                    const assignmentLinks = data[0][courseTitleText];
                    assignmentLinks.forEach(link => {
                        appendButtonsAfterCourseTitle(title.querySelector('h3'), link, 'blue');
                    });
                }
                if (courseTitleText in data[1]) {
                    const quizLinks = data[1][courseTitleText];
                    quizLinks.forEach(link => {
                        appendButtonsAfterCourseTitle(title.querySelector('h3'), link, 'red');
                    });
                }
                if (courseTitleText in data[2]) {
                    const lectureLinks = data[2][courseTitleText];
                    lectureLinks.forEach(link => {
                        appendButtonsAfterCourseTitle(title.querySelector('h3'), link, 'black');
                    });
                }
            });
        })
        .catch(error => console.error('Error fetching data:', error));
}


// Display saved buttons and fetch data from server only on the home page
if (isHomePage()) {
    displaySavedButtons();
    fetchAndUpdateButtons();
}
