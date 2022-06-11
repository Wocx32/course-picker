# Course Picker
Automatically register for courses 

Note: Only supports Forman Christian College's Empower SIS

Note: **You must have Firefox installed**

**USE AT YOUR OWN RISK**

# Install
Clone this repository
    
```bash
git clone https://github.com/Wocx32/course-picker.git
```

Cd to the directory

```bash
cd course-picker
```

Install requirements
    
```bash
pip install -r requirements.txt
```

# Download Geckodriver
Download the latest version of Geckodriver from [here](https://github.com/mozilla/geckodriver/releases/latest)

Move the executable to repo directory

# Configure
Add your empower username, password and path to geckodriver in config.py

# Run
Run the script

```bash
python main.py
```

It will ask you for the courses, semester and if you belong to Pharmacy department.

```
Enter courses and comma separate them (eg. envr 240 a, geog 101 a): envr 240 a, geog 101 a
Enter semester (eg. 2022 Summer): 2022 summer
Department of Pharmacy? (y/n): n
```

It will then register the courses and save the screenshot of courses you registered.

