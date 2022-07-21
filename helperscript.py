import datetime
import cv2


def getVideoLength(video):
    data=cv2.VideoCapture(video)
    frames=data.get(cv2.CAP_PROP_FRAME_COUNT)
    fps=int(data.get(cv2.CAP_PROP_FPS))

    seconds=int(frames/fps)
    video_time=str(datetime.timedelta(seconds=seconds))

    minutes=int(seconds/60)
    print("Seconds to minutes: ",int(seconds/60))

    print("Duration in seconds: ",seconds)
    print("Video Time : ",video_time)

    duration=(minutes,seconds/60)

    return duration

def convertStringToDate(stringDate):
    newdate=datetime.date(int(stringDate[0:4]),int(stringDate[5:7]),int(stringDate[8:10]))
    print(newdate)
    return newdate