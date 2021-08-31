import os
import json
import glob
from pathlib import Path
from ImageManager import ImageManager
import csv

'''
This class contain fuction to perform task.
'''
class ImageStorageClient():
    #Initialization of image manager methods and path
    def __init__(self,local_location):
        self.ImageManager= ImageManager(local_location)
        self.local_location = local_location
        self.bucket = self.ImageManager.bucket()
        self.db,self.batch = self.ImageManager.db()

    #read the data from the frontend in csv
    def read_csv(self):
        path_csv = self.local_location+'/data' 
        #read all the csv file that exsit
        csv_files = glob.glob(os.path.join(path_csv, "*.csv"))
        self.image_list=[]
        for f in csv_files:
            with open(f, mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    json_formatted_str = json.dumps(row, indent=2)
                    print(json_formatted_str)
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

    def upload_bucket(self,data):
        #Upload the images from frontend to the google cloud bucket
        for i in data:
            blob = self.bucket.blob("{}.jpg".format(i['Unique_id']))
            blob.content_type = "image/jpeg"
            my_file = Path(self.local_location+'/'+i['path'])
            
            if my_file.is_file(): 
                 
                with open(my_file, 'rb') as f:
                    blob.upload_from_file(f)
                    self.make_google_storage_blob_public(blob)
                    print(blob.public_url)
            else:
                print("Image does not exists")


    def upload_info(self):
        #Upload the images metadata from frontend to the google cloud firestore
        self.data = self.read_csv()
        for i in self.data:
            doc = self.db.document(i['Unique_id'])
            self.batch.set(doc ,{
            'name': i['name'],
            'store_id': i['store_id'],
            'camera_id':i['camera_id'],
            'barcode_info(cost)': i['barcode_info(cost)'],
            'time_stamp': i['time_stamp']
                                })
        #process the metadata in batches
        self.batch.commit()
        self.upload_bucket(self.data)


    def download_blob(self,source_blob_name, destination_file_name):
        """Downloads a blob from the bucket."""
        blob = self.bucket.blob(source_blob_name+'.jpg')
        blob.download_to_filename(destination_file_name+'.jpg')
        print(destination_file_name+'.jpg')
        
        #self.make_google_storage_blob_public(blob)
       

    def download_local(self,dest):
        docs = self.db.stream()
        for doc in docs:
            attribute=doc.to_dict()
            name=attribute['name']
            self.download_blob(doc.id,dest+name)



