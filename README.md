Design of the KwikMedical System Implementation 

This implementation of the KwikMedical system uses a Service-Oriented Architecture 
design splitting the functionalities into three services: Incident Report, Hospital, and 
Ambulance. Each can be accessed through a web front-end and uses an SQL 
database to store patient data.(Papazoglou and Van Den Heuvel, 2007) 

Reporting Incident Service 
The Incident report service is the entry point for new incidents, allowing users, such 
as emergency call operators, to input incident data, such as Patient name, NHS 
number, Incident Address, and condition. Once the data is inputted the incident 
report is shown below the input form with the message “Rescue request generated 
and sent” the generated request is sent to the nearest hospital. 

Geolocation Integration 
Geopy was used to calculate the nearest hospital to the incident’s location. Geopy 
uses multiple APIs such as Google Maps, Nominatim, and Bing Maps to collect data. 
Geopy takes in the incident address and outputs its longitude and latitude, the 
hospital longitude and latitude are stored in the Scottish hospitals database. Geopys 
geodesic is used to find the distance between these two points in kilometres.  
Incident Report Generation & Data transfer: 
Once the nearest hospital is found, the incident report is generated including all the 
relevant details, this will be shown in the image of the page below. The Data transfer 
is facilitated using RESTful API protocols. The incident report is also saved to a 
database, but this database is not used to allow other services to receive the data 
and is unnecessary as it was just used in testing. 

Hospital Service 
The hospital service acts as a hub to view incidents and patient records, it allows 
hospital staff to monitor the updates to the incident report, as well as reviewing the 
actions taken by ambulance staff in the patient record.  
The hospital service opens with a login page allowing hospitals to log in with a 
secure password saved in the Scottish hospitals database. Once logged in a 
navigation page allows users to choose to view either incoming incident reports or 
patient records. The incoming incidents are filtered by the hospital name logged in to 
only show the needed reports. The incoming rescue requests page is shown below.  

Interaction with Ambulance Service 
The rescue request is received and matched with the data from patient records using 
the NHS number. Both the rescue request and patient records data are then sent to 
the ambulance using RESTful API protocols. 
The status of incoming rescue requests is shown as “Pending” before ambulance 
service accepts them, “Taken” once accepted, and “Completed” after the actions 
taken has been sent back to the hospital. This is done by an update request status 
function that receives data from the ambulance and updates the status of incident 
requests using the NHS number to verify the correct patient. 
The patient records are stored in an SQL database, once the hospital receives 
actions taken, it opens the patient records and updates actions taken for each 
patient using their NHS number, this data is appended to the database as a list of 
strings. 

Ambulance Service 
The Ambulance service provides real-time interactions for ambulance staff, allowing 
them to choose from a list of patients with conditions and address of incident shown 
and log their actions taken. The Ambulance Dashboard is shown below. 
The Ambulance services open with a log in page which takes in the registration 
number of the ambulance crew, this data is saved locally but was never added to the 
patient records, only to be used in future implementations. Once logged in, accepting 
a callout sends status update data back to hospital changing the status to “Taken” 
using RESTful API protocols 

Logging Actions 
After the ambulance crew has helped the patient, they can easily log their actions 
taken on the callout details page which shows all the relevant information. The 
actions taken data is sent back to the hospital service via RESTful API protocols, the 
same function also sends a status change of the incident report to “Complete”. The 
Ambulance service ensures real-time updates for the staff at the hospital, whilst 
maintaining a seamless workflow for the ambulance staff.  

Conclusion 
The use of Service-Orientated approach such as centralised governance, modular 
services and reuseable components made this implementation of KwikMedical 
simple but effective. As a base model this implementation is a great starting point for 
further development, such as integrating GPS tracking for ambulances or map route 
suggestions. The modularity of the system allows each service to be focused, 
efficient and easily maintainable, creating a robust solution for emergency response 
management.
