import csv
import json
from ImageStorageClient import ImageStorageClient
from ImageManager import ImageManager

def main():

    path = input("Enter path of folder: ") #'/Users/abhisheksingh/Desktop/image_data_management/'

    client=ImageStorageClient(path)


    key=input('''Update storage: Press 1 
            \nRead stored data: Press 2
            \nDownload images: Press 3\n ''')



    if key == '1':
        print("Uploading Images")
        client.upload_info()
        print("Done")

        
    elif key == '2':
        print("read the images information that exsit on cloud")
        client.read_csv()
        

    if key == '3':
        print("downloading images from storage to local")
        client.download_local(path+'/downloaded_img/')
    


if __name__ == "__main__":
    main()