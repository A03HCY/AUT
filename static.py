#-*- coding:utf-8 -*-

from   flask         import *
from   flask_uploads import *
from   datetime      import *
import socket   as  line
import os
import configparser
import json
import mimetypes
import time

__version__ = '0.0.1'

# File size
def Sizeset(B):
   B = float(B)
   KB = float(1024)
   MB = float(KB ** 2)
   GB = float(KB ** 3)
   TB = float(KB ** 4)
   if B < KB:
      return '{0} {1}'.format(B,'B' if 0 == B > 1 else 'B')
   elif KB <= B < MB:
      return '{0:.2f} KB'.format(B/KB)
   elif MB <= B < GB:
      return '{0:.2f} MB'.format(B/MB)
   elif GB <= B < TB:
      return '{0:.2f} GB'.format(B/GB)
   elif TB <= B:
      return '{0:.2f} TB'.format(B/TB)

# Get host IP
def HostIP():
    try:
        s = line.socket(line.AF_INET, line.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

# Debug
basedir = os.path.dirname(__file__)
app = Flask(__name__)
app.secret_key = 'C-i6tyW8~gm^ckBS'
app.config.update(DEBUG=True)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

fileid = {
    'video':['.mp4','webm','.avi','.mov','.flv','.m4v'],
    'image':['.png','.jpg','.ico'],
    'music':['.mp3','.wav'],
    'word':['.doc','.docx','.pdf'],
    'powerpoint':['.ppt'],
    'excel':[],
    'code':['.java','.py','.pyw','.c','.h','.cpp','.php','.htm','.html','.css']
}

class User:
    def __init__(self, base=None):
        if base:self.base = base
        else:self.base = os.path.dirname(__file__)
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(self.base, "data", "Acdp.cot"), encoding="utf-8")
    
    def getuid(self, uname):
        for section in self.config.sections():
            allnum = self.config[section]
            for uid in allnum:
                name = self.config.get(section, uid)
                if name == uname:
                    return uid
        return False
    
    def getinfo(self, uid):
        path = os.path.join(self.base, "data", str(uid), "acc.cot")
        if not os.path.exists(path):return False
        tmpu = configparser.ConfigParser()
        tmpu.read(path, encoding="utf-8")
        data = {}
        for section in tmpu.sections():
            udat = {}
            allnum = tmpu[section]
            for op in allnum:
                udat[op] = tmpu.get(section, op)
            data[section] = udat

        for section in  self.config.sections():
            udat = {}
            allnum = self.config[section]
            for op in allnum:
                if op == uid:
                    udat['head'] = self.config.get(section, op)
            data[section] = udat
                    
        return data
    
    def headpath(self, uid):
        path = os.path.join(self.base, "data", str(uid), "head.png")
        if os.path.exists(path):return path
        path = os.path.join(self.base, "data", str(uid), "head.jpg")
        if os.path.exists(path):return path
        return False
    
    def addinfo(self, dic):
        pass

UID = User()

def GetHead(session, htmlname='', title='', mode='no'):
    head = {
        'html':{
            'title':htmlname,
            'acdp':True,
            'ding':True,
            'botp':True,
            'search':True,
            'uid':True
        },
        'title':title,
        'uid':session.get('uid'),
    }
    if mode == 'search':
        head['search'] = {
            'word':'',
            'results':[]
        }
    if mode == 'space':
        info = UID.getinfo(session.get('uid'))
        head['una'] = info['una']['head']
        head['html']['acdp'] = False
        head['html']['botp'] = False
    return head

# Home and space
@app.route('/', methods=['GET','POST'])
def home():
    head = GetHead(session, '主页 Acdp', '主页')
    return render_template('home.html', data=head)

# Sign up or in
@app.route('/sign', methods=['GET','POST'])
def sign():
    if session.get('uid', None):
        return redirect('/')
    if request.method == 'POST':
        if request.form.get('submit') == 'signin':
            uname = request.form.get('name', None)
            upwd = request.form.get('pwd', None)
            rem = request.form.get('rem', None)

            uid = UID.getuid(uname)
            data = UID.getinfo(uid)
            if not data:return redirect('/sign')

            if upwd == data['ubas']['pwd']:
                session['uid'] = uid
                if rem:session.permanent = True
            return redirect('/')

        if request.form.get('submit') == 'signup':
            uname = request.form.get('name', None)
            upwd = request.form.get('pwd', None)
            # 验证
    head = GetHead(session, '登录 Acdp', '登录')
    return render_template('sign.html', data=head)

@app.route('/head')
@app.route('/head/<uid>')
def apihead(uid=None):
    if not uid:
        uid = session.get('uid', None)
        if not uid:return ''
    path = UID.headpath(uid)
    print(path)
    if not path:return ''
    pathname = path
    f = open(pathname, "rb")
    response = Response(f.readlines())
    mime_type = mimetypes.guess_type(os.path.split(path)[1])[0]
    response.headers['Content-Type'] = mime_type
    response.headers['Content-Disposition'] = 'attachment; filename={}'.format(os.path.split(path)[1].encode().decode('latin-1'))
    return response

@app.route('/signout')
def out():
    if not session.get('uid'):
        return redirect('/')
    del session['uid']
    return redirect('/')

# Search
@app.route('/search', methods=['GET','POST'])
def search():
    head = GetHead(session, '搜索 Acdp', '搜索', 'search')
    head['html']['search'] = False
    head['search']['results'].append({'title':'Hi','point':'.doc','ano':'A03HCY','size':'13MB'})
    return render_template('search.html', data=head)

# User's information
@app.route('/space', methods=['GET','POST'])
@app.route('/space/<uid>', methods=['GET','POST'])
def user(uid=None):
    if not session.get('uid', None):
        return redirect('/sign')
    info = UID.getinfo(session.get('uid'))
    
    head = GetHead(session, 'Acdp', '你好', 'space')
    return render_template('space.html', data=head)

# View the article
@app.route('/article/<number>', methods=['GET','POST'])
def article(number=None):
    head = GetHead(session, '预览 Acdp', '预览')
    return render_template('article.html', data=head)

# View the video
@app.route('/video/<number>', methods=['GET','POST'])
def video(number=None):
    head = GetHead(session, '预览 Acdp', '预览')
    return render_template('video.html', data=head)

# Download in fast
@app.route('/downloadfast/<name>', methods=['GET','POST'])
def downlaodfast(name):
    pathname = "I://"+name
    def send_chunk():
        store_path = pathname
        with open(store_path, 'rb') as target_file:
            while True:
                chunk = target_file.read(30 * 1024 * 1024)
                if not chunk:
                    break
                yield chunk
    return Response(send_chunk(), content_type='application/octet-stream')

def data():
    forpath = os.path.join(basedir,'data',session.get('uid'))
    filef = request.args.get('filepwd')
    basedir = os.path.dirname(__file__)
    filet = None
    for f in os.listdir(forpath):
        pwd = os.path.splitext(f)[0].split('-')[-1]
        if not pwd == filef:continue
        filet = os.path.join(forpath, f)
        break
    if not filet:return ''
    filef = filet
    try:
        filename = filef.split('\\')[-1]
        path, name = os.path.split(os.path.join(basedir, filef))
        response = make_response(send_from_directory(path, name, as_attachment=True))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('utf-8'))
        return response
    except Exception as err:
        return 'download_file error: {}'.format(str(err))
    return data

# Download
@app.route('/download/<name>', methods=['GET','POST'])
def download(name):
    pathname = "E://"+name
    f = open(pathname, "rb")
    response = Response(f.readlines())
    # response = make_response(f.read())
    mime_type = mimetypes.guess_type(name)[0]
    response.headers['Content-Type'] = mime_type
    response.headers['Content-Disposition'] = 'attachment; filename={}'.format(name.encode().decode('latin-1'))
    return response

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)