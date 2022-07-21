import os
import time
from datetime import datetime as dt
from webbrowser import get
from flask import *
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

from helperscript import *

""" 
    App Configurations:: 
    Path for Video Uploads -- VIDEO_UPLOADS :: static/Videos
    ALLOWED_VIDEO_EXTENSIONS --  :: mp4 and mkv
    Maximum 1 GB limit on video upload Files-- MAX_CONTENT_LENGTH i.e 1024*1024*1024
    A sqlite database to store video info -- VideoStore.sqlite3
"""

app=Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
app.config["VIDEO_UPLOADS"]="static/Videos"
app.config["ALLOWED_VIDEO_EXTENSIONS"]=["mp4","mkv"]
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///VideoStore.sqlite3'


# Creating SQLAlchemy Object db 
db=SQLAlchemy(app)

class Videos(db.Model):
    """
        -- Videos class is a database model i.e Table on VideoStore Database
        
        Columns:
            Id -- Primary key
            Videourl -- The url of video,
            Videosize -- Size of Video in MB,
            Videolength in Minutes 
            Uploaded Date time      
    """

    id=db.Column(db.Integer,primary_key=True)
    videourl=db.Column(db.String(256))
    videosize=db.Column(db.Float)
    videolength=db.Column(db.Float)
    uploadedAt=db.Column(db.DateTime,default=dt.utcnow())

    def __init__(self,videourl,videosize,videolength):
        """
            Constructor for Videos
        """
        self.videourl=videourl
        self.videosize=videosize
        self.videolength=videolength

    def as_dict(self):
        """
            --- This function returns object in the form of dictionary
            --- Use :: For Easy Json Conversion of Video Object
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Creates VideoStore Database and Table if not exists         
db.create_all()


#A global list to keep track of videos being uploaded -- UploadingList
UploadingList=[]


@app.route('/')
def index():
    """
        -- Route For /
        -- Return API endpoint Info/ 
    """
    domain=request.host_url
    return jsonify({
        "APIEndpoints":"Api Endpoints",
        "VideoUpload":f"{domain}uploadvideo/",
        "BeingUploaded":f"{domain}uploadingLists/",
        "FilterByUploadedDate(YYYY-MM-DD)":f"{domain}filter?date=[date]",
        "FilterBySizeRange(MB)":f"{domain}filter?size1=[size1]&size2=[size2]",
        "Charges":f"{domain}charges/",
        "AllVideos":f"{domain}allVideos/"
    })

@app.route('/uploadvideo/',methods=["Post"])
def uploadVideo():
    """
        This function is called when user sends post request with file
        Input:: file
        Output:: Video Upload Status
    """

    if 'file' not in request.files:
        resp=jsonify({"message":"No File in Request"})
        resp.status_code=400
    else:
        file=request.files['file']
        if file.filename=='':
            resp=jsonify({"message":"No Video File Selected For Uploading"})
            resp.status=400
        
        # Check File extension for .mp4 and .mkv
        if file and checkVideoExtension(file.filename):
            # Status is True if length of video is less than 10min 
            # Duration returns the video time in minutes 
            status,duration=checkVideoDuration(file)
            if status:

                filename=secure_filename(file.filename)
                
                # Add filename to the being Uploaded list
                UploadingList.append(filename)

                newfilename=str(dt.now().strftime("%Y%m%d%H%M%S%p"))+filename

                # time.sleep(20)
                file.seek(0)
                # Saves File in Static/Videos Directory 
                file.save(os.path.join(app.config["VIDEO_UPLOADS"],newfilename))

                # Get Size of the Video in MB
                videoSize=getVideoSize(file)
                domain=request.host_url
                video=Videos(f"{domain}static/Videos/"+newfilename,videoSize,duration)
                
                # Adding Video reference to the database table
                db.session.add(video)
                db.session.commit()

                # Removing Uploading Filename from uploading list
                UploadingList.remove(filename)

                resp=jsonify({"success":"Video Successfully Uploaded"})
                resp.status_code=201
            else:
                # In case of Video Length > 10 minutes
                resp=jsonify({"error":"Video duration must be less than 10 minutes"})
                resp.status_code=400
        else:
            # Extension Validation Error Message
            resp=jsonify({"error":"Only mp4 and mkv video types are allowed"})
            resp.status=400
    return resp

@app.route("/uploadingLists/")
def getUploadingVideosList():
    """
        --- This function returns the list of videos currently being uploaded
        --- Current uploads are being tracked on Uploading Lists
    """
    resp=jsonify({"list":UploadingList})
    resp.status_code=200
    return resp


@app.route("/allVideos/",methods=['Get'])
def getAllVideos():
    """
        --- This function returns the json List of all the video details stored on the server    
    """
    videos=Videos.query.all()
    videosList=[video.as_dict() for video in videos]
    resp=jsonify(videosList)
    resp.status_code=200
    return resp


@app.route('/filter',methods=['GET'])
def filter():
    """
        --- This function takes date or size range as input
        
        --- For url?date=YYYY-MM-DD 
                It fetches the videos of that date from database
        
        --- For url?size1={size1}&size2={size2}
                It fetches the videos of size of that range

        --- Returns the list of Video Details
    """
    # Get Request Arguments 
    args=request.args
    dateArg=args.get('date')
    sizeArg=args.get('size1')
    sizeArg2=args.get('size2')

    # If Date Argument is given
    if dateArg:
        try:
            # String to Date Conversion
            newdate=convertStringToDate(dateArg)
        except:
            # For Conversion Exception
            resp=jsonify({"Error":"Enter date in correct yy-mm-dd format"})
            resp.status_code=400
            return resp
        
        #List to Store Video Objects
        videosList=[]
        result=Videos.query.all()
        
        # Loop in result queryset and comparing input date and date from queryset 
        for video in result:
            if video.uploadedAt.date()==newdate:
                videosList.append(video.as_dict())
        # print(videosList)
        
        resp=jsonify(videosList)
        resp.status_code=200
    
    # For Size Range Filter
    elif sizeArg and sizeArg2:
        # Query in database for size in between size1 and size2 
        result=db.session.query(Videos).filter(Videos.videosize.between(sizeArg,sizeArg2))
        
        # Dictionary Conversion of Video Objects for Json
        videos=[video.as_dict() for video in result]
        resp=jsonify(videos)
        resp.status_code=200
    else:
        domain=request.host_url
        resp=jsonify({"urlmismatched":f"No Arguments.. Please supply arguments as {domain}filter?date=[date] or {domain}filter?size1=?&size2=?"})
        resp.status_code=400
    return resp

@app.route("/charges/",methods=['Post'])
def getCharges():
    """
        --- This function takes a json as input (length in minutes, size in MB, Type) Example
            {
                "length":10.8,
                "size":200,
                "type":"mp4"
            }
            Returns Charge accordingly
    """
    data=request.json

    videoSize=data.get("size")
    videoLength=data.get("length")
    videoType=data.get("type")

    # # Charge Accordingly
    # sizecharge=0
    # totalcharge=0
    # lengthcharge=0
    
    if videoSize<500:
        sizecharge=5
    else:
        sizecharge=12.5

    if videoLength<6.18:
        lengthcharge=12.5
    else:
        lengthcharge=20

    # Total Charge Calculation
    totalcharge=sizecharge+lengthcharge

    return jsonify({
        "Size Charge":f"{sizecharge}$",
        "Length Charge":f"{lengthcharge}$",
        "Total Charge":f"{totalcharge}$"
        })    


def checkVideoExtension(filename):
    """
        --- Input :: Filename.extension
        --- Returns
                -- True :: If mp4 or mkv
                -- False :: Otherwise 
    """
    if not "." in filename:
        return False
    extension=filename.rsplit(".",1)[1]
    if extension.lower() in app.config["ALLOWED_VIDEO_EXTENSIONS"]:
        return True
    else:
        return False


@app.errorhandler(413)
def request_entity_too_large(error):
    """
        --- This is a handled error for too large entity than the limit 1GB 
        --- Returns video size error 
    """
    resp=jsonify({"error":"Video File should be less than 1 GB"})
    resp.status_code=413
    return resp

# Driver Code
if __name__=='__main__':
    app.run(debug=1)