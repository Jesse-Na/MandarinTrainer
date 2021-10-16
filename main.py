from pymongo import MongoClient
from random import randint
import os
import argparse
from typing import List
from dotenv import load_dotenv
import cc_edict_parser
import ssl

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
        self.answers = []
        self.curr_word = None
        # Generate random list of words
        while len(self.words) != 0:
            r = randint(0, len(self.words) - 1)
            word = self.words.pop(r)
            self.answers.append(word)

    def give_word(self):
        self.curr_word = self.answers.pop()
        return self.curr_word['english']

    def is_empty(self):
        return len(self.answers) == 0

    def give_answer(self):
        return self.curr_word


def main():
    parser = argparse.ArgumentParser('Test your mandarin skills\n')
    parser.add_argument('command', choices=['insert', 'delete', 'display', 'test'], nargs=1,
                        help='insert - for adding new words to a pool\n'
                             'delete - for deleting words from a pool\n'
                             'display - to display all words in the given pool\n'
                             'test - for pseudo randomly picking words from a pool')
    parser.add_argument('pool', nargs=1, help='the pool of words to interact with')
    parser.add_argument('words', nargs='*', help='words to insert or delete')
    args = parser.parse_args()
    print(args)

    client = MongoClient(
        "mongodb+srv://keren:{}@mandarintrainer.w7ywy.mongodb.net/MandarinTrainer?retryWrites=true&w=majority".format(
            MONGODB), ssl_cert_reqs=ssl.CERT_NONE)
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
    elif command == 'display':
        words = list(db_gateway.read_from_db())
        for word in words:
            print(word['simplified'], word['pinyin'], word['english'])
    else:
        words = list(db_gateway.read_from_db())
        if words:
            tester = Tester(words)
            print(tester.give_word())
            while input('Another? (Press any key to continue or Q to quit)') != 'Q' and not tester.is_empty():
                print(tester.give_answer())
                print(tester.give_word())
            print(tester.give_answer())

    print('Finish')


if __name__ == '__main__':
    main()
