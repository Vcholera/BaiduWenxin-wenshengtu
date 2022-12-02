# -*- coding: utf-8 -*
import wenxin_api, requests, time, threading, os, webbrowser, sys, json
from wenxin_api.tasks.text_to_image import TextToImage
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

global text, style, resolution

count = 0
dot = '.'
flag = 0
dic_style = {0:'古风', 1:'油画', 2:'水彩画', 3:'卡通画', 4:'二次元', 5:'浮世绘', 6:'蒸汽波艺术', 7:'low poly', 8:'像素风格', 9:'概念艺术', 10:'未来主义', 11:'赛博朋克', 12:'写实风格', 13:'洛丽塔风格', 14:'巴洛克风格', 15:'超现实主义'}
dic_resolution = {0:'1024*1024',1:'1024*1536',2:'1536*1024'}
dic_resize = {'1024*1024':[1024, 1024], '1024*1536':[1024, 1536], '1536*1024':[1536, 1024]}
file = 'picture'
img = {}
imgr = {}
pic = {}

wenxin_api.ak = ' '
wenxin_api.sk = ' '

#生成资源文件目录访问路径
def resource_path(relative_path):
    if getattr(sys, 'frozen', False): #是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

#判断文件夹是否存在
def mkdir(path):
    folder = os.path.exists(path)
    # 判断是否存在文件夹如果不存在则创建为文件夹
    if not folder:
        # os.makedirs 传入一个path路径，生成一个递归的文件夹；如果文件夹存在，就会报错,因此创建文件夹之前，需要使用os.path.exists(path)函数判断文件夹是否存在；
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径


#按钮“重置”逻辑程序
def reset_data():
    global entry_prompt, frame_output
    entry_prompt.delete(0,END)
    ai_resolution.set(0)
    ai_style.set(0)
    try :
        progress_bar.set(' ')
    except:
        NONE

#按钮“生成”逻辑程序
def generate():
    global text, style, resolution, flag, input_dict, start, rst, progress_bar, file, gene

    mkdir(file)

    if flag :
        if messagebox.askyesno('确认中断','确定要中断此次生成？'):
            reset_data()
            flag = 0
            text_gene.set('生成')
            return
    
    if wenxin_api.ak ==' ':
        messagebox.showerror('缺少API Key','您还未输入API Key, 请点击右上角设置图标设置API Key!')
        login()
        return
    
    if wenxin_api.sk ==' ':
        messagebox.showerror('缺少Secret Key','您还未输入Secret Key, 请点击右上角设置图标设置Secret Key!')
        login()
        return

    if entry_prompt.get() == '':
        messagebox.showerror('缺少Prompt','您还未输入Prompt, 请输入Prompt后再点击“生成”按钮!')
        return

    text=entry_prompt.get()
    resolution=dic_resolution.get(ai_resolution.get())
    style=dic_style.get(ai_style.get())

    fr_output()    
    frame_output.place(relx=0.5, y=410, width=700, height=3000, anchor=N)


    input_dict = {
        "text": f"{str(text)}",
        "style": f"{str(style)}",
        "resolution":f"{str(resolution)}"
    }

    start = time.perf_counter()

    gene = threading.Thread(target=generating)
    gene.setDaemon(True)
    gene.start()
    
    progress = threading.Thread(target=prog_bar)
    progress.setDaemon(True)
    progress.start()
  
def prog_bar():
    try:
        global localtime, flag, dot, count, progress_bar, img, imgr, pic
        text_gene.set('中断')
        flag = 1
        while flag:
            progress_bar.set(f'正在生成中，请稍后{dot}')
            time.sleep(0.5)
            count += 1
            dot += '.'
            if count == 4:
                count = 0
                dot = '.'
        end = time.perf_counter()

        progress_bar.set('图片生成结束，正在打开图片')

        localtime=time.strftime("%Y%m%d%H%M", time.localtime())



        pic_num = 1
        for urls in rst["imgUrls"]:
            content  = requests.get(urls).content
            with open(f'.\picture\{text}_{style}_{localtime}_{pic_num}.jpg','wb') as fp:
                fp.write(content)
            pic_num += 1

        pic_time = round(end-start)
        progress_bar.set(f'---生成结束，本次生成{pic_num-1}张图片，共耗时{pic_time}秒---')

        text_gene.set('生成')
        info.set(f'Prompt   :   {text}\n风格  : {style}\n分辨率   : {resolution}')

        #提示词
        label_note = Label(frame_output, text='点击图片查看原图', font=('微软雅黑',12), bg='white')
        label_note.place(relx=0.5, y=120, anchor=N)

        for i in range(pic_num-1):
            img[i] = Image.open(f'.\picture\{text}_{style}_{localtime}_{i+1}.jpg')
            imgr[i] = img[i].resize((200, 200))
            pic[i] = ImageTk.PhotoImage(imgr[i])
            if i<=2:
                Button(frame_output, image=pic[i], command=popen(i+1).pic_open).place(x=(i+1)*25+i*200, y=150)
            elif i<=5:
                Button(frame_output, image=pic[i], command=popen(i+1).pic_open).place(x=(i-2)*25+(i-3)*200, y=375)
            elif i<=8:
                Button(frame_output, image=pic[i], command=popen(i+1).pic_open).place(x=(i-5)*25+(i-6)*200, y=700)
            elif i<=11:
                Button(frame_output, image=pic[i], command=popen(i+1).pic_open).place(x=(i-8)*25+(i-9)*200, y=925)
        pic_num = 0
    except:
        NONE
 

def generating():
    try:
        global rst, flag
        rst = TextToImage.create(**input_dict)
        flag = 0
    except:
        NONE
    

def open_fold():
    mkdir(file)
    os.startfile('.\picture')

class popen():
    def __init__(self, i):
        self.i = i
    def pic_open(self):
        os.system(f'.\picture\{text}_{style}_{localtime}_{self.i}.jpg')

def wx_login():
    if entry_ak.get() =='':
        messagebox.showerror('缺少API Key','您还未输入API Key, 请填写API Key')
        login()
        return
    if entry_sk.get() =='':
        messagebox.showerror('缺少Secret Key','您还未输入Secret Key, 请填写Secret Key')
        login()
        return

    wenxin_api.ak = entry_ak.get()
    wenxin_api.sk = entry_sk.get()

    save()

    messagebox.ABORT
    tl_login.destroy()

def login():
    global entry_ak, entry_sk, tl_login, check_save

    try:
        tl_login.destroy()
    except:
        NONE

    #---login---#
    tl_login = Toplevel(window,)
    tl_login.geometry('480x220+200+200')
    tl_login.title('登录到 Baidu百度文心ERNIE-ViLG 文生图')
    tl_login.resizable(width=False, height= False)

    #信息
    label_login_note = Label(tl_login, text='请输入您的百度文心 API Key 和 Secret Key')
    label_login_note.place(y=30, relx=0.5, anchor=N)

    #api key
    label_ak = Label(tl_login, text='API Key')
    label_ak.place(x=30, y=70)

    entry_ak = Entry(tl_login)
    entry_ak.place(x=130, y=70)

    #secret key
    label_sk = Label(tl_login, text='Secret Key')
    label_sk.place(x=30, y=100)

    entry_sk = Entry(tl_login)
    entry_sk.place(x=130, y=100)

    #自动填充已保存的api
    try:
        config_file = open('api.config','r')
        api_info = json.loads(config_file.read())
        saved_ak = api_info['ak']
        saved_sk = api_info['sk']
        entry_ak.delete(0, 'end')
        entry_sk.delete(0, 'end')
        entry_ak.insert(0, saved_ak)
        entry_sk.insert(0, saved_sk)
        config_file.close()
    except:
        NONE

    #button
    button_login = Button(tl_login, text='确定', command=wx_login)
    button_login.place(x=330, y=85)

    #save
    check_save=IntVar()
    cb_save=Checkbutton(tl_login, text='是否保存API?', variable=check_save, onvalue=0, offvalue=1)
    cb_save.place(x=130, y= 130)
    
    #guide
    label_guide = Label(tl_login, text='没有百度文心API Key? 点击跳转百度文心API')
    label_guide.place(relx=0.5, y=170, anchor=N)

    def open_url(event):
        webbrowser.open("https://wenxin.baidu.com/api/key", new=0)

    label_guide.bind("<Button-1>", open_url)

def save():
    save_d=check_save.get()
    if not save_d:
        config = open('api.config','w+')
        api_ak = entry_ak.get()
        api_sk = entry_sk.get()
        config.write('{"ak":"%s", "sk":"%s"}'%(api_ak, api_sk))
        config.close()
    else :
        os.unlink('api.config')



###-----------------window----------------###

window = Tk()
window.geometry('720x960+50+14')
window.title('Baidu百度文心ERNIE-ViLG 文生图')
window.resizable(width=True, height=True)

#设置多个Frame用于分别存放按钮和输出
frame_bg = Frame(window, bg= '#e6f2ff')
frame_top = Frame(window,bg='#3464fe')
frame_main = Frame(window, bg='white')


#-----background-----#
frame_bg.place(relx=0.5 ,rely=0, width=3200, height=3200, anchor=N)

file_background = resource_path(os.path.join("res","background.png"))
back_bg=ImageTk.PhotoImage(Image.open(file_background).resize((1700,1700)))
label_backpic=Label(frame_bg, image=back_bg, bg='#e6f2ff')
label_backpic.place(relx=0.5, anchor=N)

#-----top-----#
frame_top.place(x=0, y=0, width= 19200, height=110)

file_title = resource_path(os.path.join("res","title.png"))
top_bg=ImageTk.PhotoImage(Image.open(file_title).resize((960,108)))
label_toppic=Label(frame_top, image=top_bg, bg='#3464fe')
label_toppic.place(x=0)

label_author=Label(frame_top, text='Powered by Zhou', font=('微软雅黑', 10), fg='white', bg='#3464fe')
label_author.place(x=30, y=0, height=38)

label_toptext=Label(frame_top, text='Baidu百度文心ERNIE-ViLG 文生图', font=('黑体', 14, 'bold'), fg='white', bg='#3464fe')
label_toptext.place(x=30, y=38, height=54)

file_b_active = resource_path(os.path.join("res","button_activated.jpg"))
file_setup = resource_path(os.path.join("res","setup.png"))
pic_button = ImageTk.PhotoImage(Image.open(file_b_active))
pic_setup = ImageTk.PhotoImage(Image.open(file_setup))

#生成按钮
text_gene = StringVar()
text_gene.set('生成')
button_generate=Button(frame_top, textvariable=text_gene, font=('微软雅黑',12), command=generate, activebackground= '#3464fe', activeforeground='white',fg='white', bg='#3464fe',  relief='flat', image=pic_button, compound = "center", bd=0)
button_generate.place(x=410, y=45)

#重置按钮
button_reset=Button(frame_top, text='重置',font=('微软雅黑',12), command=reset_data, activebackground= '#3464fe', activeforeground='white',fg='white', bg='#3464fe',  relief='flat', image=pic_button, compound = "center", bd=0)
button_reset.place(x=510, y=45)

#打开文件夹
button_openfold=Button(frame_top, text='图片', font=('微软雅黑',12), command=open_fold, activebackground= '#3464fe', activeforeground='white',fg='white', bg='#3464fe',  relief='flat', image=pic_button, compound = "center", bd=0)
button_openfold.place(x=610, y=45)

#设置按钮
button_setup=Button(frame_top, command=login, activebackground= '#3464fe', activeforeground='white',fg='white', bg='#3464fe',  relief='flat', image=pic_setup, compound = "center", bd=0)
button_setup.place(x=632, y=8)

#-----main-----#
frame_main.place(relx=0.5, y=120,width=700, height=280, anchor=N)

#Prompt
label_prompt=Label(frame_main,text='在此输入Prompt: ',font=('微软雅黑',14), bg='white')
label_prompt.place(x=10, y=10)

entry_prompt=Entry(frame_main,font=('微软雅黑',12), relief='ridge', width=50)
entry_prompt.place(x=180, y=12)


#风格选择
label_style=Label(frame_main,text='风格', justify='left', font=('微软雅黑',14),bg='white')
label_style.place(x=10, y=50)

ai_style=IntVar()
rd_gufeng=Radiobutton(frame_main,text='古风',font=('微软雅黑',12),bg='white',variable=ai_style, value=0)
rd_gufeng.place(x=20,y=80)

rd_youhua=Radiobutton(frame_main,text='油画',font=('微软雅黑',12),bg='white',variable=ai_style, value=1)
rd_youhua.place(x=185,y=80)

rd_shuicai=Radiobutton(frame_main,text='水彩画',font=('微软雅黑',12),bg='white',variable=ai_style, value=2)
rd_shuicai.place(x=350,y=80)

rd_katong=Radiobutton(frame_main,text='卡通画',font=('微软雅黑',12),bg='white',variable=ai_style, value=3)
rd_katong.place(x=515,y=80)

rd_erciyuan=Radiobutton(frame_main,text='二次元',font=('微软雅黑',12), bg='white', variable=ai_style, value=4,)
rd_erciyuan.place(x=20,y=110)

rd_fushihui=Radiobutton(frame_main,text='浮世绘',font=('微软雅黑',12), bg='white', variable=ai_style, value=5)
rd_fushihui.place(x=185,y=110)

rd_zhengqibo=Radiobutton(frame_main,text='蒸汽波艺术',font=('微软雅黑',12), bg='white', variable=ai_style, value=6)
rd_zhengqibo.place(x=350,y=110)

rd_lowpoly=Radiobutton(frame_main,text='low poly',font=('微软雅黑',12), bg='white', variable=ai_style, value=7)
rd_lowpoly.place(x=515,y=110)

rd_xiangsu=Radiobutton(frame_main,text='像素风格',font=('微软雅黑',12), bg='white', variable=ai_style, value=8)
rd_xiangsu.place(x=20,y=140)

rd_gainian=Radiobutton(frame_main,text='概念艺术',font=('微软雅黑',12), bg='white', variable=ai_style, value=9)
rd_gainian.place(x=185,y=140)

rd_weilai=Radiobutton(frame_main,text='未来主义',font=('微软雅黑',12), bg='white', variable=ai_style, value=10)
rd_weilai.place(x=350,y=140)

rd_saibopk=Radiobutton(frame_main,text='赛博朋克',font=('微软雅黑',12), bg='white', variable=ai_style, value=11)
rd_saibopk.place(x=515,y=140)

rd_xieshi=Radiobutton(frame_main,text='写实风格',font=('微软雅黑',12), bg='white', variable=ai_style, value=12)
rd_xieshi.place(x=20,y=170)

rd_lolita=Radiobutton(frame_main,text='洛丽塔风格',font=('微软雅黑',12), bg='white', variable=ai_style, value=13)
rd_lolita.place(x=185,y=170)

rd_baluok=Radiobutton(frame_main,text='巴洛克风格',font=('微软雅黑',12), bg='white', variable=ai_style, value=14)
rd_baluok.place(x=350,y=170)

rd_chaoxianshi=Radiobutton(frame_main,text='超现实主义',font=('微软雅黑',12), bg='white', variable=ai_style, value=15)
rd_chaoxianshi.place(x=515,y=170)


#分辨率选择
label_resolution = Label(frame_main,text='分辨率', justify='left', font=('微软雅黑',14), bg='white')
label_resolution.place(x=10,y=210)

ai_resolution = IntVar()
rd_square = Radiobutton(frame_main,text='1024*1024 方图',font=('微软雅黑',12), bg='white', variable=ai_resolution, value=0)
rd_square.place(x=20,y=240)

rd_vert = Radiobutton(frame_main, text='1024*1536 长图', font=('微软雅黑',12), bg='white', variable=ai_resolution, value=1)
rd_vert.place(x=185,y=240)

rd_cross=Radiobutton(frame_main,text='1536*1024 横图',font=('微软雅黑',12), bg='white', variable=ai_resolution, value=2)
rd_cross.place(x=350,y=240)

##frame_output
#进度条
def fr_output():
    global frame_output, info, progress_bar

    frame_output = Frame(window, bg='white')

    progress_bar = StringVar()
    progress_bar.set(' ')
    label_progress=Label(frame_output, textvariable = progress_bar, font=('微软雅黑',12), bg='white')
    label_progress.place(relx=0.5, y=10, anchor=N)

    info = StringVar()
    info.set(' ')
    label_info = Label(frame_output, textvariable=info, font=('微软雅黑',14), bg='white')
    label_info.place(relx=0.5,y=40, anchor=N)

fr_output()

window.mainloop()