from firebase import firebase
import threading
import time
import json

class FireBaseRestAPICallThread(threading.Thread):
    activeFlag: False

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            print('inside loop')
            self.activeFlag = self.getValueFromFirebase()
            time.sleep(30)

    def getValueFromFirebase(self) -> bool:
        firebaseobj = firebase.FirebaseApplication("https://pythondatabaseexample.firebaseio.com/", None)
        result = firebaseobj.get("/pythondatabaseexample/test", '')
        #print(json.load(result).get('activeFlag'))
        print(result)
        return result.get('activeFlag')

    @property
    def isActiveFlag(self) -> bool:
        return self.activeFlag
