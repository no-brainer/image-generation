QUERIES_FILE = "queries.txt"


class QueryQueue:
    def __init__(self):
        self.offset = 63
        with open(QUERIES_FILE, "r") as query_file:
            self.queries = query_file.readlines()
        self.queries = self.queries[self.offset:]

    def get_all(self):
        for query in self.queries:
            yield query.strip()
