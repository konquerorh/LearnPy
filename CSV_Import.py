from datetime import datetime as dt
import unicodecsv
from collections import defaultdict
import numpy as np

enrollments_filename = '/Users/macuser/PycharmProjects/DataScience/SourceData/enrollments.csv'
engagement_filename = '/Users/macuser/PycharmProjects/DataScience/SourceData/daily_engagement.csv'
submissions_filename = '/Users/macuser/PycharmProjects/DataScience/SourceData/project_submissions.csv'


def read_csv(filename):
    with open(filename, 'rb') as f:
        reader = unicodecsv.DictReader(f)
        return list(reader)

def parse_bolean(value):
    if value == 'True':
        return True
    else:
        return False

def parse_datetime(date):
    if date == '':
        return None
    else:
        return dt.strptime(date, '%Y-%m-%d')

def parse_maybe_int(i):
    if i == '':
        return 0
    else:
        return int(i)

def parse_float(i):
    if i == '':
        return 0.00
    else:
        return float(i)

def get_unique_students(data):
    unique_students = set()
    for data_point in data:
        unique_students.add(data_point['account_key'])
    return unique_students

def remove_free_trial_cancels(data):
    new_data = []
    for data_point in data:
        if data_point['account_key'] in paid_students:
            new_data.append(data_point)
    return new_data

def remove_udacity_test(data):
    new_data = []
    for data_point in data:
        if not data_point['account_key'] in udacity_test_accounts:
            new_data.append(data_point)
    return new_data

def within_one_week(join_date, engagement_date):
    time_delta = engagement_date - join_date
    return time_delta.days < 7

enrollments = read_csv(enrollments_filename)
# print(enrollments[0])
daily_engagements = read_csv(engagement_filename)
# print(daily_engagements[0])
project_submissions = read_csv(submissions_filename)
# print(project_submissions[0])

enrollments_num_rows = len(enrollments)

#Get the unique enrolled students
unique_enrolled_students = set()
for enrollment in enrollments:
    unique_enrolled_students.add(enrollment['account_key'])
len(unique_enrolled_students)
#print('There are {0} students enrolled, among which, {1} are unique'.format(enrollments_num_rows, len(unique_enrolled_students)))

#Get the unique enaged student
engagements_num_rows = len(daily_engagements)
unique_engagement = set()
for engagement in daily_engagements:
    unique_engagement.add(engagement['acct'])
len(unique_engagement)
#print('There are {0} students enrolled, among which, {1} are unique'.format(engagements_num_rows, len(unique_engagement)))

#Rename key 'acct' to 'account_key'
for each_record in daily_engagements:
    each_record['account_key'] = each_record['acct']
    del[each_record['acct']]

#Format dat type
for enrollment in enrollments:
    enrollment['is_canceled'] = parse_bolean(enrollment['is_canceled'])
    enrollment['join_date'] = parse_datetime(enrollment['join_date'])
    enrollment['cancel_date'] = parse_datetime(enrollment['cancel_date'])
    enrollment['days_to_cancel'] = parse_maybe_int(enrollment['days_to_cancel'])
    enrollment['is_udacity'] = parse_bolean(enrollment['is_udacity'])

for record in daily_engagements:
    record['utc_date'] = parse_datetime(record['utc_date'])
    record['total_minutes_visited'] = parse_float(record['total_minutes_visited'])
    record['num_courses_visited'] = parse_float(record['num_courses_visited'])
    #print('type of total_minutes_visited', record['total_minutes_visited'])

engagement_unique_student = get_unique_students(daily_engagements)
engagement_unique_student_number = len(get_unique_students(daily_engagements))
print('Engaged unique students: {0}'.format(engagement_unique_student_number))

#Get the surprising data: enrolled but not enagaged.
surprising_data = set()
for enrollment in enrollments:
    student = enrollment['account_key']
    if student not in engagement_unique_student:
        surprising_data.add(enrollment['account_key'])
        #print(enrollment)

#print('Start to print surprising data')
#for data in surprising_data:
 #   print(data)

#print('End printing of surprising data.')

#Get paid student, account key and join date.
paid_students = {}
for enrollment in enrollments:
    if not enrollment['is_canceled'] or enrollment['days_to_cancel'] > 7:
        account_key = enrollment['account_key']
        enrollment_date = enrollment['join_date']
        if(account_key not in paid_students) or (enrollment_date > paid_students[account_key]):
            paid_students[account_key] = enrollment_date

# len(paid_students)
print('Number of paid student: {0}'.format(len(paid_students)))
print('429', paid_students['429'])

udacity_test_accounts = set()
for enrollment in enrollments:
    if enrollment['is_udacity']:
        udacity_test_accounts.add(enrollment['account_key'])

print("# of test accounts:", len(udacity_test_accounts))


non_udacity_enrollments = []
non_udacity_engagements = []
non_udacity_submissions = []

non_udacity_enrollments = remove_udacity_test(enrollments)
non_udacity_engagements = remove_udacity_test(daily_engagements)
non_udacity_submissions = remove_udacity_test(project_submissions)

paid_engagements = remove_free_trial_cancels(non_udacity_engagements)
paid_enrollments = remove_free_trial_cancels(non_udacity_enrollments)
paid_submissions = remove_free_trial_cancels(non_udacity_submissions)

print('paid enrollments', len(paid_enrollments))
print('paid engagements:', len(paid_engagements))
print('paid submissions:', len(paid_submissions))
# print('display one row of engagement:\n', paid_enrollments[0])
# print('display one row of project submission\n', paid_submissions[0])

list_zero = []
list_one = []
for records in paid_engagements:
    if records['account_key'] == "0":
        list_zero.append(records)
    if records['account_key'] == "1":
        list_one.append(records)
print('record with 0 in account_key:\n', len(list_zero))
print('record with 1 in account_key:\n', len(list_one))


#find students engaged in the 1st week of their enrollment
paid_engagement_in_first_week = []

for engagement_record in paid_engagements:
    account_key = engagement_record['account_key']
    join_date = paid_students[account_key]
    engagement_record_date = engagement_record['utc_date']
    if engagement_record['num_courses_visited'] > 0:
        engagement_record['has_visited'] = 1
    else:
        engagement_record['has_visited'] = 0
    #print('type of engagement:', type(engagement_record_date), type(join_date))
    if within_one_week(join_date, engagement_record_date):
        paid_engagement_in_first_week.append(engagement_record)

print('Display one row of Student engaged within the 1st week:\n', paid_engagement_in_first_week[0])


def group_data(data, key_name):
    grouped_data = defaultdict(list)
    for data_point in data:
        key = data_point[key_name]
        grouped_data[key].append(data_point)
    return grouped_data


engagement_by_account = group_data(paid_engagement_in_first_week, 'account_key')


def sum_grouped_items(grouped_data, field_name):
    summed_data = {}

    for key, data_points in grouped_data.items():
        total = 0
        for data_point in data_points:
            total += data_point[field_name]
        summed_data[key] = total
    return summed_data


total_minutes_by_account = sum_grouped_items(engagement_by_account, 'total_minutes_visited')
total_minutes = list(total_minutes_by_account.values())

print('Printing total minutes by account:', total_minutes_by_account)
# Dict comprehension with items
max_minutes = 0
student_with_max_minutes = None

for student, total_minutes in total_minutes_by_account.items():
    if total_minutes > max_minutes:
        max_minutes = total_minutes
        student_with_max_minutes = student


print('Student with max minutes:', student_with_max_minutes)
print('max minutes:', max_minutes)


print(np.mean(total_minutes))


days_visited_by_account = sum_grouped_items(engagement_by_account, 'has_visited')

days_visited = list(days_visited_by_account.values())
print('printing 1st row of days visited', days_visited[0])


print('Visited days - mean:', np.mean(total_visited_days))
print('Visited days - Max:', np.max(total_visited_days))
print('Visited days - Min:', np.min(total_visited_days))
print('Visited days - Standard Deviation:', np.std(total_visited_days))

# print('visited days by account:\n', visited_days_by_account.values())
#Mean


