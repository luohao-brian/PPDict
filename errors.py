class NotFoundError(Exception):
    def __init__(self, what):
        self.what = what

    def __str__(self):
        return self.what

class InvalidDictError(Exception):
    def __init(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason

if __name__ == "__main__":
    try:
        raise NotFoundError("something")
    except NotFoundError, e:
        print "%s not found" % e
