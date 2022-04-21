# Extract frames from a video file, convert them to grayscale, and display them in sequence
# You must have three functions
# One function to extract the frames
# One function to convert the frames to grayscale
# One function to display the frames at the original framerate (24fps)
# The functions must each execute within their own python thread
# The threads will execute concurrently
# The order threads execute in may not be the same from run to run
# Threads will need to signal that they have completed their task
# Threads must process all frames of the video exactly once
# Frames will be communicated between threads using producer/consumer idioms
# Producer/consumer queues must be bounded at ten frames
# Note: You may have ancillary objects and method in order to make your code easier to understand and implement.

import cv2
from threading import Thread, Semaphore, Lock


class PCQueue:

    def __init__(self):
        self.queue = []
        self.full = Semaphore(0)
        self.empty = Semaphore(10)
        self.lock = Lock()

    def put(self, item): # Producer
        self.empty.acquire()
        self.lock.acquire()
        self.queue.append(item)  # "q.put(F)"
        self.lock.release()
        self.full.release()

    def get(self): # Consumer
        self.full.acquire()
        self.lock.acquire()
        frame = self.queue.pop(0)  # remove first frame "q.get()"
        self.lock.release()
        self.empty.release()
        return frame


# One function to extract the frames
def extract_frames(clipFileName, output_queue):
    count = 0  # frame count
    vidcap = cv2.VideoCapture(clipFileName)  # open the video clip
    success, image = vidcap.read()  # read one frame

    print(f'Reading frame {count} {success}')
    while success:
        output_queue.put(image)  # add frame to queue
        success, image = vidcap.read()  # get next frame
        count += 1
        print(f'Reading frame {count} {success}')
    output_queue.put(-1)
    print('Frame extraction complete')
    return


# One function to convert the frames to grayscale
def convert_grayscale(input_queue, output_queue):
    count = 0  # frame count
    inputFrame = input_queue.get()  # get input colored frame

    while type(inputFrame) != int:
        print(f'Converting frame {count}')
        grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)  # convert the image to grayscale
        output_queue.put(grayscaleFrame)  # add frame to queue
        count += 1
        inputFrame = input_queue.get()  # get next input colored frame
    output_queue.put(-1)
    print('Frame conversion complete')
    return


# One function to display the frames at the original framerate (24fps)
def display_f(input_queue):
    count = 0  # frame count
    inputFrame = input_queue.get()  # get input colored frame
    frameDelay = 42  # the answer to everything

    while type(inputFrame) != int:
        print(f'Displaying frame {count}')
        cv2.imshow('Video', inputFrame) # Display the frame in a window called "Video"
        if cv2.waitKey(42) and 0xFF == ord("q"): # Wait for 42 ms and check if the user wants to quit
            break
        count += 1
        inputFrame = input_queue.get() # get the next frame
    print('Finished displaying all frames')
    cv2.destroyAllWindows() # Clean up the windows
    return


file = 'clip.mp4'

extract_queue = PCQueue()
grayscale_queue = PCQueue()

extract = Thread(target=extract_frames, args=(file, extract_queue))
convert = Thread(target=convert_grayscale, args=(extract_queue, grayscale_queue))
display = Thread(target=display_f, args=(extract_queue,))

extract.start()
convert.start()
display.start()
