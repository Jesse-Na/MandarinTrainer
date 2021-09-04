from pymongo import MongoClient
from random import randint
import os
import argparse
from typing import List
from dotenv import load_dotenv
import cc_edict_parser

load_dotenv()
MONGODB = os.getenv('MONGODB')


class DBGateway:
    def __init__(self, db, pool: str, words: List[str], mandarin_dict):
        self.db = db
        self.pool = pool
        self.words = words
        self.mandarin_dict = mandarin_dict

    def insert_to_db(self):
        tmp = []
        for word in self.words:
            if word in self.mandarin_dict:
                for d in self.mandarin_dict[word]:
                    tmp.append(d)
            else:
                print('{} not inserted because there is no entry in the dictionary'.format(word))
        if len(tmp) > 0:
            print(tmp)
            self.db[self.pool].insert_many(tmp)

    def delete_from_db(self):
        if not self.is_valid_pool():
            return False
        if len(self.words) > 0:
            self.db[self.pool].delete_many({'simplified': {'$in': self.words}})
        else:
            self.db[self.pool].drop()  # delete all
        return True

    def read_from_db(self):
        if not self.is_valid_pool():
            return False
        return self.db[self.pool].find({})

    def is_valid_pool(self):
        # Check if pool exists as a collection
        collections = self.db.list_collection_names()
        if self.pool not in collections:
            return False
        return True


class Tester:
    def __init__(self, words):
        self.words = words

    def give_word(self):
        r = randint(0, len(self.words))
        return self.words.pop(r)


def main():
    parser = argparse.ArgumentParser('Test your mandarin skills\n')
    parser.add_argument('command', choices=['insert', 'delete', 'test'], nargs=1,
                        help='insert - for adding new words to a pool\ndelete - for deleting words from a pool\ntest - '
                             'for pseudo randomly picking words from a pool')
    parser.add_argument('pool', nargs=1, help='the pool of words to interact with')
    parser.add_argument('words', nargs='*', help='words to insert or delete')
    args = parser.parse_args()
    print(args)

    client = MongoClient(
        "mongodb+srv://keren:{}@mandarintrainer.w7ywy.mongodb.net/MandarinTrainer?retryWrites=true&w=majority".format(
            MONGODB))
    db = client.MandarinTrainer

    cc_edict_dict = cc_edict_parser.get_dicts()
    print('Formatting Dictionary . . .')
    mandarin_dict = {}
    for word in cc_edict_dict:
        if word['simplified'] not in mandarin_dict:
            mandarin_dict[word['simplified']] = [word]
        else:
            mandarin_dict[word['simplified']].append(word)

    db_gateway = DBGateway(db, args.pool[0], args.words, mandarin_dict)
    command = args.command[0]
    if command == 'insert':
        db_gateway.insert_to_db()
    elif command == 'delete':
        if db_gateway.delete_from_db():
            print('Delete successful')
        else:
            print('Delete failed')
    else:
        words = list(db_gateway.read_from_db())
        if words:
            tester = Tester(words)
            print(words)

    while input('Go Again? (Press any key to continue or N to quit)') != 'N':
        db_gateway.is_valid_pool()


if __name__ == '__main__':
    main()
