from ReqAndAuth import canvas
import requests
from collections import Counter
from bs4 import BeautifulSoup
import regex as re
import csv

class dependencies():
    def updateResult(result, resp):
        if type(result) == list:
            result += resp.json()
            return(result)
        else:    
            if resp.json().keys() == result.keys():
                for key in result.keys():
                    if type(result[key]) == list:
                        result[key] += resp.json()[key]
                    else:
                        result[key].update(resp.json()[key])
            else:
                result.update(resp.json())
            return(result)   
    def canvasGet(self,extension, header):
        resp = self.session.get(extension, headers = header)
        if resp.status_code != 200:
            return {"error": "error"}
        else:
            result = resp.json()
            try:
                nextLink = resp.links['next']['url']
                while 'next' in resp.links.keys():
                    nextLink = resp.links['next']['url']
                    resp = self.session.get(nextLink, headers = header)
                    result= self.updateResult(result, resp)
                if 'last' in resp.links.keys():
                    lastLink = resp.links['last']['url']
                    resp = self.session.get(lastLink, headers = header)
                    result= self.updateResult(result, resp)
                return(result)
            except:
                return(result)         
    def __init__(self):
        self.canvasClient = canvas()
        self.session = requests.Session()

class program():
    def addGradeActivity(self):
        for course in self.courseList:
            course.getGrading()
            print(course.name + ": Grading Activity Added: " + str(len(course.gradingActivity.gradeLog.events)) + " event[s] added")
        self.GradeActivityAdded=True
    def addUsers(self):
        for course in self.courseList:
            course.getUsers()
            print(course.name + ": Users Added: " + str(len(course.users.teachers)) + " teachers added")
            print(course.name + ": Users Added: " + str(len(course.users.tas)) + " TAs added")
            print(course.name + ": Users Added: " + str(len(course.users.students)) + " students added")
        self.UsersAdded=True
    def addSyllabiFiles(self):
        for course in self.courseList:
            course.getSyllabi()
            print(course.name + ": Syllabi Added: " + str(len(course.syllabi.syllabiFiles)) + " syllabi added")
        self.SyllabiAdded=True
    def addPages(self):
        for course in self.courseList:
            course.getPages()
            print(course.name + ": Pages Added: " + str(len(course.coursePages.pages)) + " pages added")
        self.PagesAdded=True
    def addZoomRecordings(self):
        for course in self.courseList:
            course.getZoomRecordings()
            print(course.name + ": Zoom Recordings Added: " + str(len(course.zoomRecordings)) + " recordings added")
        self.ZoomRecordingsAdded=True
    def makeGradeActivityLog(self):
        if hasattr(self, "GradeActivityAdded") == False:
            self.addGradeActivity()
        gradeKeys = [list(course.gradingActivity.gradeLog.submissionCount.keys()) for course in self.courseList]
        gradeKeys = list(set([item for sublist in gradeKeys for item in sublist]))
        result=[gradeKeys]
        for item in self.courseList:
            row =[0]*len(gradeKeys)
            for key in item.gradingActivity.gradeLog.submissionCount.keys():
                if key in gradeKeys:
                    row[gradeKeys.index(key)] = item.gradingActivity.gradeLog.submissionCount[key]
            result.append(row)
        return(result)
    def makeRowHeaders(self):
        if hasattr(self, "UsersAdded") == False:
            self.addUsers()
        result = [["Course Name", "CourseID", "Term", "Teachers", "TAs"]]
        for item in self.courseList:
            row =[0]*len(result[0])
            row[0] = item.name
            row[1] = item.id
            row[2] = self.term
            row[3] = ", ".join([i.name for i in item.users.teachers])
            row[4] = ", ".join([i.name for i in item.users.tas])
            result.append(row)
        return(result)
    def joinColumns(self,headerList, dataList):
        result = []
        for i in range(len(dataList)):
            result.append(headerList[i]+dataList[i])
        return result
    def writeCSV(self, joinedColumns, reportName):
        with open("{0}-{1}.tsv".format(self.term,reportName), 'w') as f:
            write = csv.writer(f,delimiter='\t')
            write.writerows(joinedColumns)
    def __init__(self, term):
        self.term = term
        self.courseList = courseCollector(term).courses      

class courseCollector():
    def searchCourses(self):
        return dep.canvasGet(dep.canvasClient.serverURL + self.courseSearchEndpoint, dep.canvasClient.header)
    def makeCourse(self,courseJson):
        result = course(courseJson)
        print("Course Added: " + result.name)
        return result
    def __init__(self, term):
        self.term = term
        self.courseSearchEndpoint = "/api/v1/accounts/{0}/courses?per_page=100&search_term={1}".format(dep.canvasClient.tenantId, term)
        self.courses = [self.makeCourse(course) for course in self.searchCourses()]

class course():
    def getUsers(self):
        self.users = courseUsers(self.id)
    def getSyllabi(self):
        self.syllabi = courseSyllabi(self.id)
    def getGrading(self):
        self.gradingActivity= courseGrading(self.id) 
    def getPages(self):
        self.coursePages = coursePages(self.id)
    def getZoomRecordings(self):
        self.zoomRecordings = canvasZoomLTI(self.id).zoomSessionsAll
    def __init__(self, jsonString):
        self.id = jsonString["id"]
        self.name = jsonString["name"]
        self.account_id = jsonString["account_id"]
        self.uuid = jsonString["uuid"]
        self.start_at = jsonString["start_at"]
        self.grading_standard_id = jsonString["grading_standard_id"]
        self.is_public = jsonString["is_public"]
        self.created_at = jsonString["created_at"]
        self.course_code = jsonString["course_code"]
        self.default_view = jsonString["default_view"]
        self.root_account_id = jsonString["root_account_id"]
        self.enrollment_term_id = jsonString["enrollment_term_id"]
        self.license = jsonString["license"]
        self.grade_passback_setting = jsonString["grade_passback_setting"]
        self.end_at = jsonString["end_at"]
        self.public_syllabus = jsonString["public_syllabus"]
        self.public_syllabus_to_auth = jsonString["public_syllabus_to_auth"]

class coursePages():
    def __init__(self, courseID):
        print(courseID)
        self.modulesEndPoint = "/api/v1/courses/{0}/pages?include[]=body".format(courseID)
        self.pageResp = dep.canvasGet(dep.canvasClient.serverURL + self.modulesEndPoint, dep.canvasClient.header)
        self.pages = [coursePage(i) for i in self.pageResp if type(i) != str]

class coursePage():
    def __init__(self, page):
        if type(page) == str:
            print(page)
        self.id = page["page_id"]
        self.title = page["title"]
        self.createdAt = page["created_at"]
        self.url = page["url"]
        self.editing_roles = page["editing_roles"]
        self.published = page["published"]
        self.hide_from_students = page["hide_from_students"]
        self.front_page = page["front_page"]
        self.html_url = page["html_url"]
        self.todo_date = page["todo_date"]
        self.publish_at = page["publish_at"]
        self.updated_at = page["updated_at"]
        self.locked_for_user = page["locked_for_user"]
        self.body = page["body"]
        if self.body != None:
            self.bodyParsed = coursePageBody(self.body)
class coursePageBody():
    def __init__(self, body):
        self.body = body
        self.bodySoup = BeautifulSoup(self.body, 'html.parser')
        self.embeddedVideos = self.bodySoup.find_all('iframe')
        self.embeddedLinks = self.bodySoup.find_all('a')
        if len(self.embeddedLinks) > 0:
            self.href = [link.get('href') for link in self.embeddedLinks]
       

class courseUsers():
    def getUsers(self, role):
        endpoint = self.endpoint+"&enrollment_type[]={0}".format(role)
        result = dep.canvasGet(dep.canvasClient.serverURL + endpoint, dep.canvasClient.header)
        return self.deserializeUsers(result)
    def deserializeUsers(self, jsonString):
        return([canvasUser(i) for i in jsonString])
    def __init__(self, courseID):
        self.endpoint = "/api/v1/courses/{0}/users?per_page=100".format(courseID)
        self.teachers = self.getUsers("teacher")
        self.tas = ''#self.getUsers("ta")
        self.students = ""#self.getUsers("student")

class courseSyllabi():
    def getSyllabi(self):
        endpoint = self.filesEndpoint
        result = dep.canvasGet(dep.canvasClient.serverURL + endpoint, dep.canvasClient.header)
        return(self.deserializeSyllabi(result))
    def deserializeSyllabi(self, jsonString):
        return([canvasFile(i) for i in jsonString])
    def __init__(self, courseID):
        self.filesEndpoint = "/api/v1/courses/{0}/files?search_term=syllabus".format(courseID)
        self.syllabiFiles = self.getSyllabi()

class courseGrading():
    def getGradeActivity(self):
        result = dep.canvasGet(dep.canvasClient.serverURL + self.gradeChangeEndpoint, dep.canvasClient.header)
        return self.deserializeGradeActivity(result)
    def deserializeGradeActivity(self, jsonString):
        return(canvasGradeLog(jsonString))
    def __init__(self, courseID):
        self.gradeChangeEndpoint = "/api/v1/audit/grade_change/courses/{0}?per_page=100".format(courseID)
        self.gradeLog= self.getGradeActivity()

class canvasUser():
    def checkLogin(self, jsonString):
        if "login_id" in jsonString.keys():
            return jsonString["login_id"]
        else:
            return "No Login"
    def checkEmail(self, jsonString):
        if "email" in jsonString.keys():
            return jsonString["email"]
        else:
            return "No Email"
    def __init__(self, jsonString):
        self.id = jsonString["id"]
        self.name = jsonString["name"]
        self.created_at = jsonString["created_at"]
        self.sortable_name = jsonString["sortable_name"]
        self.short_name = jsonString["short_name"]
        self.login_id = self.checkLogin(jsonString)
        self.email = self.checkEmail(jsonString)

class canvasGradeLog():
    def makeUserDict(self):
        result ={}
        for user in self.linked['users']:
            result[user['id']] = user['name']
        return result
    def makeSubmissionsDict(self):
        result = {}
        for assignment in self.linked['assignments']:
            result[assignment['id']] = ", ".join(assignment["submission_types"])
        return result
    def getLabeledAssignments(self):
        return([self.submissionsDict[i['links']['assignment']] for i in self.events if i['links']['assignment'] in self.submissionsDict.keys()])
    def __init__(self,jsonString):
        self.links = jsonString["links"]
        self.events = jsonString["events"]
        self.linked = jsonString["linked"]
        self.userIds = self.makeUserDict()
        self.submissionsDict = self.makeSubmissionsDict()
        self.submissionCount = Counter(self.getLabeledAssignments())

class canvasFile():
    def __init__(self, jsonString):
        self.id = jsonString["id"]
        self.uuid = jsonString["uuid"]
        self.folder_id = jsonString["folder_id"]
        self.display_name = jsonString["display_name"]
        self.filename = jsonString["filename"]
        self.upload_status = jsonString["upload_status"]
        self.content_type = jsonString["content-type"]
        self.url = jsonString["url"]
        self.size = jsonString["size"]
        self.created_at = jsonString["created_at"]
        self.updated_at = jsonString["updated_at"]
        self.unlock_at = jsonString["unlock_at"]
        self.locked = jsonString["locked"]
        self.hidden = jsonString["hidden"]
        self.lock_at = jsonString["lock_at"]
        self.hidden_for_user = jsonString["hidden_for_user"]
        self.thumbnail_url = jsonString["thumbnail_url"]
        self.modified_at = jsonString["modified_at"]
        self.mime_class = jsonString["mime_class"]

class canvasZoomLTI():
    def launchSession(self):
        result = dep.session.get(self.launchSessionURL, headers = dep.canvasClient.header).json()
        if "url" in result.keys():
            self.redirectURL = result["url"]
    def postRedirect(self):
        redirectContent = dep.session.post(self.redirectURL, allow_redirects=True)
        self.redirectContent= BeautifulSoup(redirectContent.content,'html.parser')
    def getFormDetails(self, form):
        #Adapted from thepythoncode.com
        details = {}
        action = form.attrs.get("action").lower()
        method = form.attrs.get("method", "get").lower()
        inputs = []
        for input_tag in form.find_all("input"):
            input_type = input_tag.attrs.get("type", "text")
            input_name = input_tag.attrs.get("name")
            input_value =input_tag.attrs.get("value", "")
            inputs.append({"type": input_type, "name": input_name, "value": input_value})
        details["action"] = action
        details["method"] = method
        details["inputs"] = inputs
        return details
    def composeFormData(self, form_details):
        #Adapted from thepythoncode.com
        data = {}
        for input_tag in form_details["inputs"]:
            if input_tag["type"] == "hidden":
                data[input_tag["name"]] = input_tag["value"]
            elif input_tag["type"] == "select":
                for i, option in enumerate(input_tag["values"], start=1):
                    if option == input_tag["value"]:
                        print(f"{i} # {option} (default)")
                    else:
                        print(f"{i} # {option}")
                choice = input(f"Enter the option for the select field '{input_tag['name']}' (1-{i}): ")
                try:
                    choice = int(choice)
                except:
                    value = input_tag["value"]
                else:
                    value = input_tag["values"][choice-1]
                data[input_tag["name"]] = value
            elif input_tag["type"] != "submit":
                value = input(f"Enter the value of the field '{input_tag['name']}' (type: {input_tag['type']}): ")
                data[input_tag["name"]] = value
        return(data)
    def buildForms(self):
        redirectForm= self.redirectContent.find("form")
        self.redirectFormDetails = self.getFormDetails(redirectForm)
        self.redirectData= self.composeFormData(self.redirectFormDetails)
    def postLTIRedirect(self):
        zoomLTIRedirect = dep.session.post(self.redirectFormDetails['action'], data=self.redirectData)
        self.zoomLTIRedirect = BeautifulSoup(zoomLTIRedirect.content, 'html.parser')
    def parseForms(self):
        self.zoomScript = self.zoomLTIRedirect.find("script")  
        self.ajaxHeaders = re.findall(r"value: \"(.*?)\"", self.zoomScript.text)
        self.scid = re.findall(r"scid:\"(.*?)\"",self.zoomScript.text)[0]
        self.oauthConsumerKey = re.findall(r"oauthConsumerKey:\"(.*?)\"",self.zoomScript.text)[0]
        self.zoomServer = self.redirectFormDetails['action']
    def buildHeader(self):
        result ={
        "Content-Type":"application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Referer": self.zoomServer +"?lti_scid={0}&oauth_consumer_key={1}".format(self.scid,self.oauthConsumerKey),
        "Connection": "keep-alive",
        "x-zm-cluster-id":self.ajaxHeaders[0],
        "x-zm-aid":self.ajaxHeaders[1],
        "x-zm-haid":self.ajaxHeaders[2],
        "x-zm-region":self.ajaxHeaders[3],
        "X-XSRF-TOKEN":self.ajaxHeaders[4]}
        self.zHeader = result
    def buildEndpoint(self):
        reqLink = "https://applications.zoom.us/api/v1/lti/rich/recording/COURSE"
        reqLink +="?startTime=&endTime=2023-09-18&keyWord=&searchType=1&status=&page=1&total=0"
        reqLink += "&lti_scid="+self.scid
        self.reqLink = reqLink
    def __init__(self, courseID):
        self.courseID = courseID
        self.launchSessionURL = dep.canvasClient.serverURL + "/api/v1/courses/{0}/external_tools/sessionless_launch?id=23490000000002028".format(courseID)
        self.launchSession()
        if hasattr(self, "redirectURL") == True:
            self.postRedirect()
        if hasattr(self, "redirectContent") == True:
            self.buildForms()
        if hasattr(self, "redirectData") == True and hasattr(self, "redirectFormDetails") == True:
            self.postLTIRedirect()
            self.parseForms()
        if hasattr(self, "zoomServer") == True:
            self.buildHeader()
            self.buildEndpoint()
        if hasattr(self, "reqLink") == True:
            self.zoomRedirect=dep.session.get(self.reqLink, headers=self.zHeader)
            self.zoomSessions = self.zoomRedirect.json()
            self.zoomSessionsAll = [canvasZoomLTIMeetings(i) for i in self.zoomSessions['result']['list']]

class canvasZoomLTIMeetings():
    def __init__(self, jsonString):
        self.meetingID = jsonString['meetingId']
        self.meetingNumber = jsonString['meetingNumber']
        self.accountID = jsonString['accountId']
        self.topic = jsonString['topic']
        self.startTime = jsonString['startTime']
        self.hostID = jsonString['hostId']
        self.duration = jsonString['duration']
        self.status = jsonString['status']
        self.hostEmail = jsonString['hostEmail']
        self.totalSize = jsonString['totalSize']
        self.recordingCount = jsonString['recordingCount']
        self.disabled = jsonString['disabled']
        self.timezone = jsonString['timezone']
        self.totalSizeTransform = jsonString['totalSizeTransform']
        self.createTime = jsonString['createTime']
        self.modifyTime = jsonString['modifyTime']
        self.key = jsonString['key']
        self.publish = jsonString['publish']
        self.value = jsonString['value']
        self.recordingFiles = jsonString['recordingFiles']
        self.sectionID = jsonString['sectionId']
        self.recordingSectionID = jsonString['recordingSectionId']
        self.recordingGroupID = jsonString['recordingGroupId']
        self.listStartTime = jsonString['listStartTime']
        self.published = jsonString['published']
        self.enable = jsonString['enable']
        self.enableAndPublished = jsonString['enableAndPublished']
        self.student = jsonString['student']

dep = dependencies()

