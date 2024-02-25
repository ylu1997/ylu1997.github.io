class Node():
    def __init__(self):
        self.next = None
        self.last = None

    def append_next(self, next_node):
        self.next = next_node
        next_node.last = self

    def append_last(self, last_node):
        self.last = last_node
        last_node.next = self

    def break_next_connect(self):
        next_node = self.next
        next_node.last = None
        self.next = None

    def break_last_connect(self):
        last_node = self.last
        last_node.next = None
        self.last = None

    def is_head(self):
        return self.last == None

    def is_tail(self):
        return self.next == None

    def remove_next(self):
        if self.is_tail():
            next_node = self.next
            if not next_node.is_tail():
                next_next_node = next_node.next
                next_node.break_last_connect()
                next_node.break_next_connect()
                self.append_next(next_next_node)
            else:
                self.break_next_connect()
        else:
            pass

    def remove_last(self):
        if self.is_head():
            last_node = self.last
            if not last_node.is_head():
                last_last_node = last_node.next
                last_node.break_last_connect()
                last_node.break_next_connect()
                self.append_last(last_last_node)
            else:
                self.break_last_connect()
        else:
            pass

    def traverse(self, func):
        ptr = self
        while True:
            if ptr is None:
                break
            else:
                func(ptr)
                ptr = ptr.next
