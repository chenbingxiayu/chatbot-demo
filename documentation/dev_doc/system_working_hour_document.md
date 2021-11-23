# System Working Hour Document V0.1 20211123


## 1.	Two types of working hour

<br/>

| Type | Date | Time Slot (Mon.-Fri.) | Time Slot (Sat.) |
|  ----  | ---- | ----  | ---- |
| Online Chatting Working Hour | Non public holiday | 9:00-12:00 14:00-18:00 | Non |
| Other Services Working Hour | Non public holiday | 9:00-19:00 | 9:00-12:00 |

<br/>

## 2.	APIs for checking working hour

<br/>

### 1)	is_ chatting_working_hour


For checking the working hour of Online Chatting service


First check if today is working day and then check the day of the week and time


Return: True/False

<br/>

### 2) is_working_hour


For checking the working hour of other service


First check if today is working day and then check the day of the week and time


Return: True/False

<br/>

## 3.	Upload Function and CSV File Template


Use existing API update_calendar


Need to update the existing class BusinessCalendar, and the method BusinessCalendar.update_items_from_csv

<br/>

### Table BusinessCalendar
| Item | Format/options | Remarks |
|  ----  | ---- | ----  |
| date | yyyy-mm-dd | Not Changed |
| is_working_day | boolean | Not Changed |
| office_hr_begin | hh:mm (00:00-24:00) | Not Changed; For other services |
| office_hr_end | hh:mm (00:00-24:00) | Not Changed; For other services |
| chatting_office_hr_begin | hh:mm (00:00-24:00) | New; For online chatting |
| chatting_office_hr_end | hh:mm (00:00-24:00) | New; For online chatting |

<br/>

### Upload CSV template:

<br/>

{date, public_holiday, office_hr_begin, office_hr_end, chatting_office_hr_begin, chatting_office_hr_end}

<br/>

| | | | | | |
|  ----  | ---- | ----  | ----  | ---- | ----  |
| 01/11/2021 | Monday | 9:00 | 19:00 | 9:00 | 18:00 |
| 02/11/2021 | Tuesday | 9:00 | 19:00 | 9:00 | 18:00 |
| 03/11/2021 | Wednesday | 9:00 | 19:00 | 9:00 | 18:00 |
| 04/11/2021 | Thursday | 9:00 | 19:00 | 9:00 | 18:00 |
| 05/11/2021 | Friday | 9:00 | 19:00 | 9:00 | 18:00 |
| 06/11/2021 | Saturday | 9:00 | 12:00 | | |
| 07/11/2021 | public holiday | | | |		
| 08/11/2021 | Monday | 9:00 | 19:00 | 9:00 | 18:00 |

<br/>

Need to update the method BusinessCalendar.update_items_from_csv to adapt to the new CSV template
