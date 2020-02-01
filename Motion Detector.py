import imutils
import cv2
import numpy as np
import FireBaseRestAPICall
import time



# Number of frames to pass before changing the frame to compare the current frame against
FRAMES_TO_PERSIST = 10
# Minimum boxed area for a detected motion to count as actual motion Use to filter out noise or small objects
MIN_SIZE_FOR_MOVEMENT = 2000
# Minimum length of time where no motion is detected it should take
# (in program cycles) for the program to declare that there is no movement
MOVEMENT_DETECTED_PERSISTENCE = 100


# Create capture object
cap = cv2.VideoCapture(5)  # Flush the stream
cap.release()
cap = cv2.VideoCapture(0)  # Then start the webcam

# Init frame variables
first_frame = None
next_frame = None
counter = 0

# Init display font and timeout counters
font = cv2.FONT_HERSHEY_SIMPLEX
delay_counter = 0
movement_persistent_counter = 0
faces_cascade = cv2.CascadeClassifier('haarcascade/haarcascade_fullbody.xml')

fireBaseRestAPIThread = FireBaseRestAPICall.FireBaseRestAPICallThread()
fireBaseRestAPIThread.start()
time.sleep(30)

while (fireBaseRestAPIThread.isActiveFlag == 'True'):
    # Set transient motion detected as false
    transient_movement_flag = False

    # Read frame
    (ret, frame) = cap.read()
    text = 'Unoccupied'

    # If there's an error in capturing
    if not ret:
        print ('CAPTURE ERROR')
        continue

    # Resize and save a Grey scale version of the image
    frame = imutils.resize(frame, width=750)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Blur it to remove camera noise (reducing false positives)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # If the first frame is nothing, initialize it
    if first_frame is None:
        first_frame = gray

    delay_counter += 1

    # Otherwise, set the first frame to compare as the previous frame
    # But only if the counter reaches the appropriate value
    # The delay is to allow relatively slow motions to be counted as large
    # motions if they're spread out far enough

    if delay_counter > FRAMES_TO_PERSIST:
        delay_counter = 0
        first_frame = next_frame

    # Set the next frame to compare (the current frame)
    next_frame = gray

    # Compare the two frames, find the difference
    frame_delta = cv2.absdiff(first_frame, next_frame)
    thresh = cv2.threshold(frame_delta, 25, 0xFF, cv2.THRESH_BINARY)[1]

    # Fill in holes via dilate(), and find contours of the thresholds
    thresh = cv2.dilate(thresh, None, iterations=2)
    (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)

    # loop over the contours
    for c in cnts:
        # Save the coordinates of all found contours
        (x, y, w, h) = cv2.boundingRect(c)
        # If the contour is too small, ignore it, otherwise, there's transient movement
        if cv2.contourArea(c) > MIN_SIZE_FOR_MOVEMENT:
            transient_movement_flag = True
            # Draw a rectangle around big enough movements
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # The moment something moves momentarily, reset the persistent
    # movement timer.

    if transient_movement_flag == True:
        movement_persistent_flag = True
        movement_persistent_counter = MOVEMENT_DETECTED_PERSISTENCE

    # As long as there was a recent transient movement, say a movement
    # was detected

    if movement_persistent_counter > 0:
        text = 'Movement Detected ' + str(movement_persistent_counter)
        movement_persistent_counter -= 1
    else:
        text = 'No Movement Detected'

    if movement_persistent_counter > 0:
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faces_cascade.detectMultiScale(grey, 1.1, 4)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0xFF, 0, 0),
                          3)
        if len(faces) > 0:
            counter = counter + 1
            cv2.imwrite('images/' + str(counter) + '.jpg', frame)
            human_detection_flag = False

    # Print the text on the screen, and display the raw and processed video
    # feeds

    cv2.putText(
        frame,
        str(text),
        (10, 35),
        font,
        0.75,
        (0xFF, 0xFF, 0xFF),
        2,
        cv2.LINE_AA,
        )

    # For if you want to show the individual video frames
#    cv2.imshow("frame", frame)
#    cv2.imshow("delta", frame_delta)

    # Convert the frame_delta to color for splicing

    frame_delta = cv2.cvtColor(frame_delta, cv2.COLOR_GRAY2BGR)

    # Splice the two video frames together to make one long horizontal one

    cv2.imshow('frame', np.hstack((frame_delta, frame)))

    # Interrupt trigger by pressing q to quit the open CV program

    ch = cv2.waitKey(1)
    if ch & 0xFF == ord('q'):
        break

# Cleanup when closed

cv2.waitKey(0)
cv2.destroyAllWindows()
cap.release()


