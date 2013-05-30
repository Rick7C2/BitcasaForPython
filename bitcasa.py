import requests
import re
import sys
import os.path
from os import listdir
import pickle
import json
from Tkinter import *
from tkFileDialog import askopenfilename
from tkFileDialog import askdirectory
from multiprocessing import Pool

save_path = os.path.abspath('./bitcasa_saves')
credentials_path = os.path.join(save_path, "credentials.save")
session_path = os.path.join(save_path, "session.save")

def setup_saves_dir():
	if not os.path.isdir(save_path):
		os.mkdir(save_path)

def session_saved():
	try:
		session = load_session()
	except:
		return False
	return session.get and session.post

def load_session():
	session_file = open(session_path, 'rb')
	session = pickle.load(session_file)
	session_file.close()
	return session

def save_session(session):
	session_file = open(session_path, 'wb')
	pickle.dump(session, session_file)
	session_file.close()

def get_session(credentials):
	if session_saved():
		return load_session()
	else:
		session = create_session(credentials)
		save_session(session)
		return session

def create_session(credentials):
	session = requests.Session()
	form_values = get_login_form_values(session)
	post_path = login(session, form_values, credentials)
	return session

def close_session(session):
	session.get("https://my.bitcasa.com/logout")
	session.close()

def credentials_saved():
	try:
		credentials = load_credentials()
	except:
		return False
	return credentials['user'] and credentials['password']

def load_credentials():
	credentials_file = open(credentials_path, 'r')
	credentials = pickle.load(credentials_file)
	credentials_file.close()
	return credentials

def save_credentials(credentials_dictionary):
	credentials_file = open(credentials_path, 'wb')
	pickle.dump(credentials_dictionary, credentials_file)
	credentials_file.close()

def get_credentials():
	if credentials_saved():
		credentials_dictionary = load_credentials()
	else:
		user = raw_input("User: ")
		password = raw_input("Password: ")
		credentials_dictionary = {'user' : user, 'password' : password}
		remember_credentials = raw_input("Save your credentials in plain text on your hard drive?[n] ")
		if remember_credentials == "y":
			save_credentials(credentials_dictionary)
	return credentials_dictionary

def get_login_form_values(session):
	login_page = session.get("https://my.bitcasa.com/logout")
	#sessionid = requests.utils.dict_from_cookiejar(login_page.cookies)['sessionid']
	csrf_token = re.search('input type="hidden" name="csrf_token" value="(.*)"/>', login_page.text).group(1).encode('ascii','ignore')
	code = re.search('input type="hidden" name="code" value="(.*)"/>', login_page.text).group(1).encode('ascii','ignore')
	url = re.search('form method="POST" action="(.*)">', login_page.text).group(1).encode('ascii','ignore')
	url = "https://my.bitcasa.com/" + url
	
	return {'csrf_token' : csrf_token, 'code' : code, 'url' : url}

def login(session, form_values, credentials):
	post_data = {'csrf_token' : form_values['csrf_token'], 'code' : form_values['code'], 'user' : credentials['user'], 'password' : credentials['password']}
	response = session.post(form_values['url'], post_data, allow_redirects=True)

def get_directory_contents(session, directory_path):
	contents = []
	response = session.get("https://my.bitcasa.com/directory/"+directory_path+"?show-incomplete=true")
	parsed_json = json.loads(response.text)
	for directory in parsed_json:
		contents.append({'name':directory['name'], 'path':directory['path']})
	return contents
	
def get_root_directories(session):
	directories = []
	root_path = None
	response = session.get("https://my.bitcasa.com/directory/?show-incomplete=true")
	parsed_json = json.loads(response.text)
	for directory in parsed_json:
		directories.append({'name':directory['name'], 'path':directory['path']})
		if "Bitcasa Infinite Drive" in directory['name']:
			root_path = directory['path']
	if root_path != None:
		directories += get_directory_contents(session, root_path)
	return directories

def get_upload_directory(session):
	directories = get_root_directories(session)
	upload_directory = -1
	for x in range(len(directories)):
		print x, directories[x]['name']
	while upload_directory >= len(directories) or upload_directory < 0: 
		upload_directory = int(raw_input("Which directory would you like to upload to? (Enter the index): "))
	print "Will upload to", directories[upload_directory]['name']
	return directories[upload_directory]['path'].encode('utf-8','replace')

def get_one_local_file():
	Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
	filename = askopenfilename()
	return filename

def upload_file(session, upload_dir_path, files):
	for local_file_path in files:
		print "Uploading", local_file_path,
		file_to_upload = {'file':open(local_file_path, 'rb')}
		url = "https://my.bitcasa.com/files?path=" + upload_dir_path + "&access_token=undefined"
		response = session.post(url, files=file_to_upload, allow_redirects=True)
		print "-",
		if response.status_code == 200:
			print "Success!"
		else:
			print "Failed:", response.status_code

def get_all_files_in_directory():
	Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
	directory_path = askdirectory()	
	onlyfiles = [ os.path.join(directory_path,f) for f in listdir(directory_path) if os.path.isfile(os.path.join(directory_path,f)) ]
	return onlyfiles

def remove_duplicate_files(local_files, remote_files):
	parsed_remote_files = []
	for remote_file in remote_files:
		parsed_remote_files.append(remote_file['name'])
	new_local_files = []
	for local_file in local_files:
		if os.path.basename(local_file) in parsed_remote_files:
			print "Found Duplicate:", os.path.basename(local_file)
		else:
			new_local_files.append(local_file)
	return new_local_files

def subprocess_init(*args):
	global upload_dir_path
	upload_dir_path = args[0]
	global credentials
	credentials = args[1]

def subprocess_function(curr_file):
	session = create_session(credentials)
	files = [curr_file]
	upload_file(session, upload_dir_path, files)
	close_session(session)

def get_files_to_upload():
	input = ''
	while not (input == 'w' or input == 'f'):
		input = raw_input("Would you like to upload one file [f] or a whole directory [w]: ")
	files = []
	if input == 'w':
		files = get_all_files_in_directory()
	else:
		files.append(get_one_local_file())
	return files

def launch_subprocesses(credentials, upload_dir_path, files):
	pool = Pool(processes=2, initializer=subprocess_init, initargs=[upload_dir_path, credentials])
	pool.map(subprocess_function, files)
	pool.close()
	pool.join()

def main():
	setup_saves_dir()
	credentials = get_credentials()
	session = get_session(credentials)
	upload_dir_path = get_upload_directory(session)
	files = get_files_to_upload()
	files = remove_duplicate_files(files, get_directory_contents(session, upload_dir_path))
	launch_subprocesses(credentials, upload_dir_path, files)
	save_session(session)

if __name__ == "__main__":
	main()
