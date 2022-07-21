import os
import time
from datetime import datetime
from flask import *
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

from helperscript import getVideoLength,convertStringToDate


app=Flask(__name__)
app.config["VIDEO_UPLOADS"]="static/Videos"
app.config["ALLOWED_VIDEO_EXTENSIONS"]=["mp4","mkv"]
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///VideoStore.sqlite3'

UploadingList=[]

db=SQLAlchemy(app)

class Videos(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    videoname=db.Column(db.String(256))
    videosize=db.Column(db.Float)
    videolength=db.Column(db.Float)
    uploadedAt=db.Column(db.DateTime,default=datetime.utcnow)

    def __init__(self,videoname,videosize,videolength):
        self.videoname=videoname
        self.videosize=videosize
        self.videolength=videolength

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
        

db.create_all()

@app.route('/')
def index():
    return jsonify({"message":"Hello Welcome To Video Store Server"})

@app.route('/uploadvideo/',methods=["Post"])
def uploadVideo():
    if 'file' not in request.files:
        resp=jsonify({"message":"No File in Request"})
        resp.status_code=400
    else:
        file=request.files['file']
        if file.filename=='':
            resp=jsonify({"message":"No Video File Selected For Uploading"})
            resp.status=400
        if file and checkVideoExtension(file.filename):
            status,duration=checkVideoDuration(file)
            if status:
                filename=secure_filename(file.filename)
                UploadingList.append(filename)
                newfilename=str(datetime.now().strftime("%Y%m%d%H%M%S%p"))+filename
                
                time.sleep(20)

                file.save(os.path.join(app.config["VIDEO_UPLOADS"],newfilename))
                videoSize=getVideoSize(file)
                video=Videos(newfilename,videoSize,duration)
                db.session.add(video)
                db.session.commit()
                UploadingList.remove(filename)

                resp=jsonify({"message":"Video Successfully Uploaded"})
                resp.status_code=201
            else:
                resp=jsonify({"message":"Video duration must be less than 10 minutes"})
                resp.status_code=200
        else:
            resp=jsonify({"message":"Only mp4 and mkv video types are allowed"})
            resp.status=400
    return resp

@app.route("/uploadingLists/")
def getUploadingVideosList():
    resp=jsonify({"list":UploadingList})
    resp.status_code=200
    return resp


@app.route('/filter',methods=['GET'])
def filter():
    args=request.args
    dateArg=args.get('date')
    sizeArg=args.get('size1')
    sizeArg2=args.get('size2')
    if dateArg:
        try:
            newdate=convertStringToDate(dateArg)
            print("Converted Date Time Type",type(newdate))
            print("Converted Date Time",newdate)
        except:
            resp=jsonify({"Date Format Error":"Enter date in correct yy-mm-dd format"})
            resp.status_code=400
            return resp
        
        videosList=[]
        result=Videos.query.all()
        for video in result:
            if video.uploadedAt.date()==newdate:
                videosList.append(video.as_dict())
        print(videosList)
        resp=jsonify(videosList)
        resp.status_code=200
    elif sizeArg and sizeArg2:
        print(sizeArg,sizeArg2)
        result=db.session.query(Videos).filter(Videos.videosize.between(sizeArg,sizeArg2))
        videos=[video.as_dict() for video in result]
        resp=jsonify(videos)
        resp.status_code=200
    else:
        resp=jsonify({"message":"No Arg Please supply arguments as url?date=?&size1=?&size2=?"})
        resp.status_code=400
        print("No Arg Please supply arguments as url?date=?&size=?")
    return resp

@app.route("/charges/",methods=['Post'])
def getCharges():
    data=request.json
    videoSize=data.get("size")
    videoLength=data.get("length")
    videoType=data.get("type")

    sizecharge=0
    totalcharge=0
    lengthcharge=0
    
    if videoSize<500:
        sizecharge=5
    else:
        sizecharge=12.5

    if videoLength<6.18:
        lengthcharge=12.5
    else:
        lengthcharge=20

    totalcharge=sizecharge+lengthcharge

    return jsonify({"Size Charge":f"{sizecharge}$","Length Charge":f"{lengthcharge}$","Total Charge":f"{totalcharge}$"})    

def checkVideoExtension(filename):
    if not "." in filename:
        return False
    extension=filename.rsplit(".",1)[1]
    if extension.lower() in app.config["ALLOWED_VIDEO_EXTENSIONS"]:
        return True
    else:
        return False


def getVideoSize(file):
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    return byteToMbConversion(file_length)

def byteToMbConversion(btsize):
    return round(btsize/1048576,3)

def checkVideoDuration(file):
    filepath=os.path.join("temp",file.filename)
    file.save(filepath)
    print(filepath)
    return checkVideoLength(filepath)

def checkVideoLength(filepath):
    minutes,duration=getVideoLength(filepath)
    os.remove(filepath)
    if minutes<10:
        return True,duration
    else:
        return False,0

@app.errorhandler(413)
def request_entity_too_large(error):
    resp=jsonify({"error":"Video File should be less than 1 GB"})
    resp.status_code=413
    return resp


if __name__=='__main__':
    app.run(debug=1)