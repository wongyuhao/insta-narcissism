# Get instance
import os
from datetime import datetime
from dotenv import load_dotenv
import csv
import instaloader

L = instaloader.Instaloader()
load_dotenv()
# Login or load session
# replace or replicate env where necessary
L.login(os.environ.get('TEST_USER'), os.environ.get('TEST_PASS'))  # (login)

# Obtain profile metadata
profile = instaloader.Profile.from_username(L.context, os.environ.get('TARGET_USER'))


class Record:
    def __init__(self, dt, following=None, followers=None):
        if followers is None:
            followers = set()
        if following is None:
            following = set()
        self.datetime = dt
        self.username = profile.username
        self.filename = self.datetime.strftime('%Y-%m-%d_%H%M%S')
        self.following = following
        self.followers = followers


def write_csv(record):
    print(record.filename)
    with open('{}.csv'.format(record.filename), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows([
            [record.datetime],
            [record.username],
            [len(record.followers)],
            [len(record.following)]
        ])
        writer.writerow(record.followers)
        writer.writerow(record.following)


def get_info():
    r = Record(datetime.now())
    print('Fetching info', 'for @' + r.username, 'at', r.datetime)
    print('Getting followers...')
    for follower in profile.get_followers():
        r.followers.add(follower.username)
    print('Found', len(r.followers), 'followers')
    print('Getting following...')
    for following in profile.get_followees():
        r.following.add(following.username)
    print('Found', len(r.following), 'following')
    print('Done! Saved to file ' + r.filename + '.csv')
    print()
    write_csv(r)
    return r


def parse_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        result = []
        for row in reader:
            result.append(row)
        dt = result[0][0]
        username = result[1][0]
        follower_count = result[2][0]
        following_count = result[3][0]
        followers = result[4]
        following = result[5]

        print('Parsed record for @' + username + ' at ' + dt)
        print('Following:', following_count, 'Followers:', follower_count)
        print()
        r = Record(datetime.strptime(filename.replace('.csv', ''), '%Y-%m-%d_%H%M%S'), set(following), set(followers))
        return r


def compare_csv(old, new):
    # sanity check
    if old.username != new.username:
        print('Can\'t compare across accounts!')
        return

    print('Time elapsed between records', new.datetime - old.datetime)

    # compare following lists between two records
    if old.following == new.following:
        print('No changes in following count\t[{}]'.format(len(new.following)))
    else:
        intersect = old.following.intersection(new.following)
        diff_old = old.following.difference(intersect)
        diff_new = new.following.difference(intersect)
        print('Following count changes: ({}) +{} -{}'.format(len(new.following), len(diff_new), len(diff_old)))
        for username in diff_new:
            print('[+]', username)
        for username in diff_old:
            print('[-]', username)
        print()
    # compare follower lists between two records
    if old.followers == new.followers:
        print('No changes in follower count\t[{}]'.format(len(new.followers)))
    else:
        intersect = old.followers.intersection(new.followers)
        diff_old = old.followers.difference(intersect)
        diff_new = new.followers.difference(intersect)
        print('Follower count changes: ({}) +{} -{}'.format(len(new.followers), len(diff_new), len(diff_old)))
        for username in diff_new:
            print('[+]', username)
        for username in diff_old:
            print('[-]', username)
        print()

    no_followback = new.following.difference(new.followers)
    print('Accounts you follow that don\'t follow you back: [{}]'.format(len(no_followback)))
    for user in no_followback:
        print(user)


def get_latest_filename():
    def filtercsv(filename):
        return '.csv' in filename

    lst = list(filter(filtercsv, os.listdir()))
    return lst.pop()


r1 = parse_csv(get_latest_filename())
r2 = get_info()
compare_csv(r1, r2)
