#-*- coding:utf-8 -*-

from   flask          import  *
import socket    as     line
import os
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

fileid = {
    'video':['.mp4','webm','.avi','.mov','.flv','.m4v'],
    'image':['.png','.jpg','.ico'],
    'music':['.mp3','.wav'],
    'word':['.doc','.docx','.pdf'],
    'powerpoint':['.ppt'],
    'excel':[],
    'code':['.java','.py','.pyw','.c','.h','.cpp','.php','.htm','.html','.css']
}

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
    # 已登录则 return redirect('/')
    if request.method == 'POST':
        if request.form.get('submit') == 'signin':
            uname = request.form.get('name', None)
            upwd = request.form.get('pwd', None)
            # 验证
        if request.form.get('submit') == 'signup':
            uname = request.form.get('name', None)
            upwd = request.form.get('pwd', None)
            # 验证
    head = GetHead(session, '登录 Acdp', '登录')
    return render_template('sign.html', data=head)

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

# Download in fast
@app.route('/adl/<name>', methods=['GET','POST'])
def adl(name):
    pathname = "I://"+name
    store_path = pathname
    with open(store_path, 'rb') as target_file:
        return target_file.read()

# Download
@app.route('/download/<name>', methods=['GET','POST'])
def download(name):
    pathname = "I://"+name
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
    print(HostIP())
    app.run(host="0.0.0.0", port=80)