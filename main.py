
import os
import csv
import requests


SUBDOMAIN = 'apiary'
PAGER_DUTY_API_ACCESS_KEY = os.getenv('PAGER_DUTY_API_ACCESS_KEY')


CSV_STRUCTURE = [
    {'header': 'Name', 'get_value': lambda data: data['name']},
    {'header': 'E-mail Address', 'get_value': lambda data: data['emails'][0]},
    {'header': 'E-mail Address', 'get_value': lambda data: data['emails'][1]},
    {'header': 'E-mail Address', 'get_value': lambda data: data['emails'][2]},
    {'header': 'Mobile Phone', 'get_value': lambda data: data['phones'][0]},
    {'header': 'Mobile Phone', 'get_value': lambda data: data['phones'][1]},
    {'header': 'Mobile Phone', 'get_value': lambda data: data['phones'][2]},
]


def request_api():
    url = 'https://{0}.pagerduty.com/api/v1/users'.format(SUBDOMAIN)
    headers = {
        'Authorization': 'Token token={0}'.format(API_ACCESS_KEY),
        'Content-Type': 'application/json',
    }

    res = requests.get(url, headers=headers, params={'include[]': 'contact_methods'})
    res.raise_for_status()

    return res.json()


def user_to_row(user):
    data = {'name': user['name'], 'emails': set(), 'phones': set()}

    for contact_method in user['contact_methods']:
        if 'email' in contact_method:
            data['emails'].add(contact_method['email'])
        if 'phone_number' in contact_method:
            data['phones'].add(phone_number(contact_method))

    data['emails'] = list(data['emails'])
    data['phones'] = list(data['phones'])

    row = []
    for column_definition in CSV_STRUCTURE:
        try:
            row.append(column_definition['get_value'](data))
        except LookupError:
            row.append('')
    return row


def phone_number(contact_method):
    return '+{} {}'.format(contact_method['country_code'], contact_method['phone_number'])


def write_csv(rows):
    with open('contacts.csv', 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)

        headers = [column_definition['header'] for column_definition in CSV_STRUCTURE]
        csv_writer.writerow(headers)

        for row in rows:
            csv_writer.writerow(row)


if __name__ == '__main__':
    data = request_api()
    write_csv([user_to_row(user) for user in data['users']])
