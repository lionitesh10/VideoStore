import datetime
import cv2
import os

def getVideoSize(file):
    """
        --- This function returns the integer part of size of the file in MB
    """
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    return byteToMbConversion(file_length)

def byteToMbConversion(btsize):
    """
        --- Input Size in Byte
        --- Output Size in MB
        --- This function converts bytes to MB and round it to 3 
    """
    return round(btsize/1048576,3)

def checkVideoDuration(file):
    """
        --- This function saves the file temporarily to ./temp/ directory
        --- Input :: File
        --- Returns function to check Video Length 
    """

    filepath=os.path.join("temp",file.filename)
    file.save(filepath)
    return checkVideoLength(filepath)

def checkVideoLength(filepath):
    """
        This function gets the filepath and checks the length of the video
        --- Input :: File Path
        --- Output :: Returns True if length of the video is less than 10
                        Else Returns False
    """
    minutes,duration=getVideoLength(filepath)
    
    # Delete the temporary file
    os.remove(filepath)
    if minutes<10:
        return True,duration
    else:
        return False,0

def getVideoLength(video):
    """
        --- This function computes the duration length of the video
        --- Input :: Video of provided path
        --- Output :: Returns Duration Both (minute only , minute.seconds)
    """
    data=cv2.VideoCapture(video)
    frames=data.get(cv2.CAP_PROP_FRAME_COUNT)
    fps=int(data.get(cv2.CAP_PROP_FPS))

    seconds=int(frames/fps)

    # video_time=str(datetime.timedelta(seconds=seconds))

    minutes=int(seconds/60)

    duration=(minutes,seconds/60)

    return duration

def convertStringToDate(stringDate):
    """ 
        This function Converts String Date to Date Type
        --- Input String date in format YYYY/MM/DD or YYYY-MM-DD
        --- Output String in format YYYY-MM-DD
    """
    newdate=datetime.date(int(stringDate[0:4]),int(stringDate[5:7]),int(stringDate[8:10]))
    return newdate