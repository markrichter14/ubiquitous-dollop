'''
    mediamgr.utils.smb.py
'''
import socket
from smb.SMBConnection import SMBConnection
from mediamgr import app

MEDIA = app.config['MEDIA']

def make_conn(share_info):
    '''
        takes share_info dict
        returns connection dict

        share_info = {
            'server_name' : 'osmc'
            'server_ip'   : '192.168.4.10'
            'username'    : 'osmc'
            'password'    : 'osmc'
            'domain_name' : 'WORKGROUP'
            'share_name'  : 'Media'
        }
    '''
    print('*** Call: make_conn')

    connection = {
        'server_ip': share_info['server_ip'],
        'share_name': share_info['share_name'],
        'conn': SMBConnection(share_info['username'], share_info['password'],
                              socket.gethostname(), share_info['server_name'],
                              domain=share_info['domain_name'], use_ntlm_v2=True,
                              is_direct_tcp=True),
    }
    return connection

def send_file(local, remote, share_info=MEDIA):
    '''
        takes full file paths for local and remote
        copies local file to remote file
    '''
    connection = make_conn(share_info)
    conn = connection['conn']
    assert conn.connect(connection['server_ip'], 445)
    try:
        with open(local, 'rb') as file_obj:
            bytes_uploaded = conn.storeFile(connection['share_name'], remote, file_obj)
    finally:
        conn.close()
    return bytes_uploaded

def get_file(remote, local, share_info=MEDIA):
    '''
        takes full file paths for remote and local
        copies remote file to local file
    '''
    connection = make_conn(share_info)
    conn = connection['conn']
    assert conn.connect(connection['server_ip'], 445)
    file_attribs, bytes_written = None, None
    try:
        with open(local, 'wb') as file_obj:
            res = conn.retrieveFile(connection['share_name'], remote, file_obj)
            file_attribs, bytes_written = res
    finally:
        conn.close()
    return file_attribs, bytes_written

def list_files(top='/', share_info=MEDIA):
    '''
        takes full file paths for remote
        returns a list of all remote files recursively
    '''
    print('*** Call: list_path')
    connection = make_conn(share_info)
    conn = connection['conn']
    assert conn.connect(connection['server_ip'], 445)
    res = []
    if not top.startswith('/'):
        top = '/' + top
    if not top.endswith('/'):
        top += '/'
    paths = [top]
    try:
        while paths:
            cur_path = paths.pop()
            sharefiles = conn.listPath(connection['share_name'], cur_path)
            for sharefile in sharefiles:
                if sharefile.isDirectory:
                    if sharefile.filename not in ['.', '..']:
                        paths.append(cur_path + sharefile.filename + '/')
                else:
                    res.append(cur_path + sharefile.filename)
    finally:
        conn.close()
    return sorted(res)

def list_dirs(top='/', share_info=MEDIA):
    '''
        takes full file path for remote
        returns a list of directories without recursing
    '''
    print('*** Call: list_dirs')
    connection = make_conn(share_info)
    conn = connection['conn']
    assert conn.connect(connection['server_ip'], 445)
    res = []
    if not top.startswith('/'):
        top = '/' + top
    if not top.endswith('/'):
        top += '/'
    try:
        sharefiles = conn.listPath(connection['share_name'], top)
        for sharefile in sharefiles:
            if sharefile.isDirectory:
                if sharefile.filename not in ['.', '..']:
                    res.append(sharefile.filename)
    finally:
        conn.close()
    return sorted(res)
