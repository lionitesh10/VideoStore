## To Run This Script

Create your Virtual Environment ::
    **python -m venv venv**
    Activate Virtual Environment :
    Then
    **pip install -r requirements.txt**
    Then Run:
#### **app.py file** python app.py

## API Endpoints

### Get API Endpoints :
    On Get Request on :: http://127.0.0.1:5000/
    Result:
        {
            "APIEndpoints": "Api Endpoints", 
            "BeingUploaded": "http://127.0.0.1:5000/uploadingLists/", 
            "Charges": "http://127.0.0.1:5000/charges/", 
            "FilterBySizeRange(MB)": "http://127.0.0.1:5000/filter?size1=[size1]&size2=[size2]", 
            "FilterByUploadedDate(YYYY-MM-DD)": "http://127.0.0.1:5000/filter?date=[date]", 
            "VideoUpload": "http://127.0.0.1:5000/uploadvideo/"
        }

### To Upload Video (Receive a Video API) : 
    On Post Request on:: http://127.0.0.1:5000/uploadvideo/
        --- Add video on formdata with key **file** and set the type to file
        --- Select file
        --- Hit The Post Request 
        --- This may take some time 1-2 minutes for files greater than 1 GB for Size Check

### To Check Current Uploading Lists (Filenames being currently uploaded) :
    On Get Request on:: http://127.0.0.1:5000/uploadingLists
        --- Just after you request upload post file keep on checking this get request on next tab

### Filter API (Filter Videos according to Uploaded Date or Size Range) :
    On Get Request with Arguments on:: 
        --- For Date Format (YYYY-MM-DD)
                http://127.0.0.1:5000/filter?date={date}
                **Example:** 
                http://127.0.0.1:5000/filter?date=2022-07-21
        --  For Size Range in MB:
                http://127.0.0.1:5000/filter?size1={size(MB)}&size2={size(MB)}
                **Example:**
                http://127.0.0.1:5000/filter?size1=10&size2=200

### Charges API (Post Request Charges according to the Input Length, Size and Type):
    Input Given as Raw JSON data on ::
            http://127.0.0.1:5000/charges/
            Example JSON Data:
            {
                "length":10.8,
                "size":200,
                "type":"mp4"
            }
            Calculates Charges Accordingly
            Returns:
            {
                "Length Charge": "20$",
                "Size Charge": "5$",
                "Total Charge": "25$"
            }
