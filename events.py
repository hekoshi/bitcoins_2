#!/usr/bin/env python3
from imports import *

class Event(object):
    data = {}
    def __init__(self, type, **data):
        self.data = data
        self.type = type

    def __getattribute__(self, name):
        if name == 'data':
            return object.__getattribute__(self, name)
        elif name in self.data:
            return self.data[name]
        else: return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in self.data:
            self.data[name] = value
        else: object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name in self.data:
            del self.data[name]
        else: object.__delattr__(self, name)

class Events(object):
    def __init__(self):
        self.events = queue.Queue()

    def post(self, event):
        assert(isinstance(event, Event))
        self.events.put(event)

    def get(self):
        events = list()
        while not self.events.empty():
            events.append(self.events.get())
        return events

    def poll(self):
        if self.events.empty(): return None
        return self.events.get()

    def wait(self):
        return self.events.get()

    def clear(self):
        while not self.events.empty():
            self.events.get()

    def __iter__(self):
        return iter(self.get())

    def __add__(self, y):
        assert(isinstance(y, (Events, Event)))
        if isinstance(y, Event):
            self.events.put(y)
        elif isinstance(y, Events):
            for event in y.get():
                self.events.put(event)
        return self
