class Event:

    def __init__(self, event_time, event_type, peer_id, data=None):
        self.event_time=event_time
        self.event_type=event_type
        self.peer_id=peer_id
        self.data=data

    def __lt__(self, other): #For Comparisons in Event Priority Queue
        return self.event_time < other.event_time