import csv
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import storage
from google.oauth2 import service_account
from io import BytesIO
# # Instantiates a client

"""Uploads a file to the bucket."""
with open('auth/graceful-smithy-324300-38b121953fd6.json') as source:
    info = json.load(source)

storage_credentials = service_account.Credentials.from_service_account_info(info)

storage_client = storage.Client(project='graceful-smithy-324300', credentials=storage_credentials)

bucket = storage_client.get_bucket('caper-images')

# Use the application default credentials

cred = credentials.Certificate('auth/graceful-smithy-324300-38b121953fd6.json') 
firebase_admin.initialize_app(cred, {
  'projectId': 'graceful-smithy-324300',
})
db = firestore.client()

batch = db.batch()
db_col =db.collection('caper-data')
#batch = db_col.batch()
#storage_client = storage_client.batch()

class Storage():
    def __init__(self,path):
        self.path=path
        self.image_list = []

    def read_csv(self):
        with open(self.path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                self.image_list.append(row)

        return self.image_list
                
    def make_google_storage_blob_public(self,blob_object):
            ''' Makes the blob object for google storage publicly accessible. 
                Anyone with the link can access the the resource for the blob
                Params:
                blob_object : For the resource. 
                Returns: 
                True: If blob is made public.
                False: Otherwise. '''
            try:        
                acl = blob_object.acl
                acl.all().grant_read()
                acl.save()
                return True
            except:
                return False

    
    def upload_info(self):

        up = self.read_csv()
        for i in up:
            doc = db_col.document(i['Unique_id'])
            batch.set(doc ,{
            'name': i['name'],
            'store_id': i['store_id'],
            'camera_id':i['camera_id'],
            'barcode_info(cost)': i['barcode_info(cost)'],
            'time_stamp': i['time_stamp']
                        })
            
            
            blob = bucket.blob("{}.jpg".format(i['Unique_id']))
            blob.content_type = "image/jpeg"

            with open(i['path'], 'rb') as f:
                blob.upload_from_file(f)
                self.make_google_storage_blob_public(blob)
                print(blob.public_url)
                print("sfsfbsf")
        batch.commit()




    def download_blob(self,source_blob_name, destination_file_name):
        """Downloads a blob from the bucket."""

        blob = bucket.blob(source_blob_name+'.jpg')
        blob.download_to_filename(destination_file_name+'.jpg')

        print("Downloaded storage object to local file.")



    def read_image(self,dest):
        
        docs = db_col.stream()

        for doc in docs:

            attri=doc.to_dict()
            name=attri['name']

            self.download_blob(doc.id,dest+name)


    # def query(self,key):
    #     docs = db_col.where(u'store_id', u'=='u"1").stream()

    #     for doc in docs:
    #         print(f'{doc.id} => {doc.to_dict()}')

S=Storage('/Users/abhisheksingh/Desktop/caper/image_data.csv')

S.upload_data()

S.read_image(dest='/Users/abhisheksingh/Desktop/caper/img/')

# S.query('1')