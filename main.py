from pymongo import MongoClient
from random import randint
import os
import argparse


class DBGateway():
    def __init__(self, db, command, pool, words):
        self.db = db
        self.command = command
        self.pool = pool
        self.words = words

    def insert_to_db(self):
        pass

    def delete_from_db(self):
        pass

    def read_from_db(self):
        pass


class Tester():
    def __init__(self, words):
        self.words = words


def main():
    client = MongoClient(
        "mongodb+srv://keren:{}@mandarintrainer.w7ywy.mongodb.net/MandarinTrainer?retryWrites=true&w=majority".format(
            os.environ['MONGODB']))
    db = client.MandarinTrainer

    parser = argparse.ArgumentParser('Test your mandarin skills')
    parser.add_argument('command', nargs=1,
                        help='insert - for adding new words to a pool\ndelete - for deleting words from a pool\ntest - '
                             'for pseudo randomly picking words from a pool')
    parser.add_argument('pool', nargs=1, help='the pool of words to interact with')
    parser.add_argument('words', nargs='*', help='words to insert or delete')

    args = parser.parse_args()
    print(args)
    while input('Go Again? (Press any key to continue or N to quit)') != 'N':
        fivestar = db.reviews.find_one({'rating': 5})
        print(fivestar)


if __name__ == '__main__':
    main()
