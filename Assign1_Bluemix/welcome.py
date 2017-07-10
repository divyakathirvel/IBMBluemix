import os, sys
import keystoneclient.v3 as keystoneclient
import swiftclient.client as swiftclient
import gnupg
from cStringIO import StringIO
from pprint import pprint
from cryptography.fernet import Fernet

auth_url = 'https://identity.open.softlayer.com' + '/v3'
project_name = '<project_name>'
password = '<password>'
user_domain_name = '<user_domain_name>'
project_id = '<project_id>'
user_id = '<user_id>'
region_name = '<region_name>'

# Get a Swift client connection object
conn = swiftclient.Connection(
    key=password,
    authurl=auth_url,
    auth_version='3',
    os_options={"project_id": project_id,
                "user_id": user_id,
                "region_name": region_name})

# Variable declaration
my_enc_file = {}

##Create a new container
container_name = 'new-container'
conn.put_container(container_name)
print "\nContainer %s created successfully." % container_name

# Allow user to enter File name and upload the cipher text after encrypting the file
def upload():
    file_name = raw_input('Enter the File name to upload : ')
    try:
        file = open(file_name)
    except IOError:
        print >> sys.stderr, "No such file", file_name
        sys.exit()
    en_file = 'new_' + file_name
    file_size = os.path.getsize(file_name)
    for container in conn.get_account()[1]:
        for data in conn.get_container(container['name'])[1]:
            if en_file == data['name']:
                status= 2
        status= 1
    if status == 1:
        file = open(file_name)
        contents = file.read()
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        my_enc_file[file_name] = cipher_suite
        cipher_text = cipher_suite.encrypt(contents)
        file = open(en_file, "w")
        file.write(cipher_text)
        conn.put_object(container_name, en_file, contents=cipher_text)
        file.close()
    elif status == 2:
        print "File already exists in the Server"
        exit

### Download the file specified file if exists, after decrypting its content
def download():
    downloadedfile = raw_input('Enter the file name to download :')
    cipher_suite = my_enc_file.get(downloadedfile,'File not present in container')
    #Encrypted file name
    d_en_file = 'new_'+downloadedfile
    tmp = "tmp.txt"
    d_file = conn.get_object(container_name, d_en_file)
    file = open(tmp, 'w')
    file.write(d_file[1])
    file.close()
    file = open(tmp, 'r')
    cipher_text = file.read()
    plain_text = cipher_suite.decrypt(cipher_text)
    file = open(downloadedfile, 'w')
    file.write(str(plain_text))
    file.close()
    print "\n File has been downloaded"

# List of all containers, objects in a container, and prints out each object name, the file size, and last modified date
def list_files():
    sum = 0
    # List your containers
    print ("\nContainer List:")
    for container in conn.get_account()[1]:
        print container['name']
    print ("\nObject List:")
    for container in conn.get_account()[1]:
        for data in conn.get_container(container['name'])[1]:
            print 'object: {0}\t size: {1}\t date: {2}'.format(data['name'], data['bytes'], data['last_modified'])
            sum = sum + data['bytes']
    print sum

# List Local Files in a Directory, and prints out each file name
def list_local_files():
    print 'Local directory files'
    dirlist = os.listdir("C:\Users\Admin\Desktop\Files")
    print(dirlist)

# Delete the object if size of the file is greater than 100 bytes
def delete():
    for container in conn.get_account()[1]:
        for data in conn.get_container(container['name'])[1]:
            size=data['bytes']
            print 'object: {0}\t size: {1}\t date: {2}'.format(data['name'], data['bytes'], data['last_modified'])
            print()
            if(size>100):
                conn.delete_object(container_name, data['name'])
                print '{0} file deleted from container'.format(data)

# Menu
def menu():
    print('Enter options')
    print('1. List Local files 2. Upload 3. Download 4.List Cloud Files 5. Delete files  4. Exit')
    option = input('Select options : ')
    print''
    if option == 1:
        list_local_files()
        menu()
    elif option == 2:
        upload()
        menu()
    elif option == 3:
        download()
        menu()
    elif option == 4:
        list_files()
        menu()
    elif option == 5:
        delete()
        menu()
    elif option == 6:
        sys.exit(0)
    else:
        sys.exit(0)

menu()
