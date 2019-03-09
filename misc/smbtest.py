from smb.SMBConnection import SMBConnection


dest_dir = 'smb://192.168.4.10/media/test'
from_dir = 'smb://192.168.4.18/share/Downloads/from'

print('Hello')
conn = SMBConnection('osmc', 'osmc', 'my_name', 'osmc')
assert conn.connect('192.168.4.10', 139)

#conn = SMBConnection(userid, password, client_machine_name, remote_machine_name, use_ntlm_v2 = True)
#conn.connect(server_ip, 139)
filelist = conn.listPath('media', '/')

for fl in filelist:
    print(fl.filename)