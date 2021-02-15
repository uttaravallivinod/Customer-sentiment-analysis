from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login as log
from sentiment.models import Org,Product,Review,Video,Audio
from textblob import TextBlob
import cv2
from tensorflow.keras.models import model_from_json
import numpy as np
import json
import speech_recognition as sr
from django.http import HttpResponse
import re
import tweepy
from tweepy import OAuthHandler


# Create your views here.


with open(r'C:\Users\upend\model.json', "r") as json_file:
    loaded_model_json = json_file.read()
    loaded_model = model_from_json(loaded_model_json)
facec = cv2.CascadeClassifier(r'C:\Users\upend\haarcascade_frontalface_default.xml')
loaded_model.load_weights(r'C:\Users\upend\model_weights.h5')
loaded_model.compile()

def login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user is not None:
            log(request,user)
            og=Org.objects.filter(user=user)
            if og:
                return redirect('/sentiment/dashboard')
            else:
                return redirect('/sentiment/addorg')
        else:
            messages.info(request,'Invalid details')
            return redirect('/sentiment/')
    return render(request,'registration/login.html')


def addorg(request):
    if request.method=='POST':
        user=request.user
        name=request.POST['name']
        og=Org.objects.create(user=user,name=name)
        og.save()
        return redirect('/sentiment/dashboard')
    else:
        return render(request,'org.html')









def signup(request):
    if request.method=='POST':
        fname=request.POST['fname']
        lname=request.POST['lname']
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        if fname.isalpha() and lname.isalpha():
            if User.objects.filter(username=username).exists():
                messages.info(request,"Username Already Exists")
                return redirect('/sentiment/signup')
            else:
                user=User.objects.create_user(username=username,email=email,first_name=fname,last_name=lname,password=password)
                user.save()
                return redirect('/sentiment')
        else:
            messages.info(request,'invalid first name or last name')
            return redirect('/sentiment/signup')
        return redirect('/')
    return render(request,'signup.html')







def addproduct(request,pk):
    if request.method=='POST':
        user=User.objects.get(id=pk)
        org=Org.objects.get(user=user)
        title=request.POST['name']
        info=request.POST['info']
        pr=Product.objects.create(org=org,name=title,description=info)
        pr.save()
    return redirect('/sentiment/dashboard')


def dashboard(request):
    user=request.user
    org=Org.objects.filter(user=user)[0]
    products=Product.objects.filter(org=org)
    return render(request,'dashboard.html',{'products':products,'name':org.name})

def senti(request,pk):
    product=Product.objects.get(id=pk)
    org=Org.objects.get(id=product.org.id)
    products=Product.objects.filter(org=org)
    polarity_list=list(Review.objects.filter(product=product).order_by('polarity').values_list('polarity','subject','text'))
    polarity=[]
    subject=[]
    if len(polarity_list)==0:
        top_review='no reviews yet'
        bad_review='no reviews yet'
        review_data={'positive':0,'negetive':0,'neutral':0}
        polarity=[]
        pos_pol=[]
        neg_pol=[]

    else:
        top_review=polarity_list[-1][2]
        bad_review=polarity_list[0][2]
        for i in polarity_list:
            polarity.append(i[0])
            subject.append(i[1])
        pos_pol=[]
        neg_pol=[]
        nut_pol=[]
        for i in polarity:
            if i>0:
                pos_pol.append(i)
            elif i<0:
                neg_pol.append(i)
            else:
                nut_pol.append(i)

        review_data={'positive':(len(pos_pol)/len(polarity))*100,'negetive':(len(neg_pol)/len(polarity))*100,'neutral':(len(nut_pol)/len(polarity))*100}


    # video details

    video_data=Video.objects.filter(product=product)
    video_count=len(video_data)
    if video_count==0:
        video_data={'happy':0,'angry':0,'neutral':0,'sad':0}
        angry_count,happy_count,neutral_count,sad_count=0,0,0,0
    else:



        jsonDec = json.decoder.JSONDecoder()
        v_data=video_data.values_list('data')
        v_list=[]
        for i in v_data:

            v_list.extend(jsonDec.decode(i[0]))


        EMO = ["Angry", "Disgust","Fear", "Happy","Neutral", "Sad","Surprise"]
        angry_count,happy_count,neutral_count,sad_count=v_list.count(0),v_list.count(3),v_list.count(4),v_list.count(5)
        video_data={'happy':(happy_count/len(v_list))*100,'angry':((angry_count)/len(v_list))*100,'neutral':((neutral_count)/len(v_list))*100,'sad':((sad_count)/len(v_list))*100}



    # audio details

    audio_polarity_list=list(Audio.objects.filter(product=product).order_by('polarity').values_list('polarity','subject','text'))
    audio_polarity=[]
    audio_pos_pol=[]
    audio_neg_pol=[]
    audio_nut_pol=[]
    if len(audio_polarity_list)==0:

        audio_review_data={'positive':0,'negetive':0,'neutral':0}
        audio_top_review='no reviews yet'
        audio_bad_review='no reviews yet'
    else:


        audio_top_review=polarity_list[-1][2]
        audio_bad_review=polarity_list[0][2]
        for i in audio_polarity_list:
            audio_polarity.append(i[0])

        for i in audio_polarity:
            if i>0:
                audio_pos_pol.append(i)
            elif i<0:
                audio_neg_pol.append(i)
            else:
                audio_nut_pol.append(i)



        audio_review_data={'positive':(len(audio_pos_pol)/len(audio_polarity))*100,'negetive':(len(audio_neg_pol)/len(audio_polarity))*100,'neutral':(len(audio_nut_pol)/len(audio_polarity))*100}


    return render(request,'senti.html',{'products':products,'name':org.name,'review':review_data,'video':video_data,'review_count':len(polarity),'pos_review_count':len(pos_pol),'neg_review_count':len(neg_pol),'top_review':top_review,'bad_review':bad_review,'happy':happy_count,'sad':sad_count,'neutral':neutral_count,'angry':angry_count,'video_count':video_count,'audio_review':audio_review_data,'audio_review_count':len(audio_polarity),'audio_pos_review_count':len(audio_pos_pol),'audio_neg_review_count':len(audio_neg_pol),'audio_top_review':audio_top_review,'audio_bad_review':audio_bad_review,'pk':pk})

def fhome(request):
    org=Org.objects.all()

    return render(request,'feedback/orghome.html',{'org':org})





def text_feedback(request,pk):
    product=Product.objects.get(id=pk)
    if request.method=='POST':
        text=request.POST['text']
        analysis = TextBlob(text).sentiment
        polarity=float(analysis.polarity)
        subject=float(analysis.subjectivity)
        messages.info(request,'Successfully feedback submitted')
        rv=Review.objects.create(product=product,text=text,polarity=polarity,subject=subject)
        rv.save()

    return render(request,'feedback/feedback.html',{'name':product.name,'pk':pk})




def products(request,pk):
    org=Org.objects.get(id=pk)
    products=Product.objects.filter(org=org)
    return render(request,'feedback/home.html',{'products':products,'name':org.name})



def video(request,pk):
    product=Product.objects.get(id=pk)
    cap=cv2.VideoCapture(0)
    EMO = ["Angry", "Disgust","Fear", "Happy","Neutral", "Sad","Surprise"]
    data=[]
    font = cv2.FONT_HERSHEY_SIMPLEX
    while(True):
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = facec.detectMultiScale(gray, 1.3, 5)
        if len(faces)==0:
            image=cv2.putText(frame, 'no faces detected', (50, 50), font, 1, (255, 255, 0), 2)
            cv2.imshow('frame',image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue
        for (x, y, w, h) in faces:
            fc = gray[y:y+h, x:x+w]
            roi = cv2.resize(fc, (48, 48))
            predictions = loaded_model.predict(roi[np.newaxis, :, :, np.newaxis])
            data.append(int(np.argmax(predictions)))


        image=cv2.putText(frame, EMO[np.argmax(predictions)], (x, y), font, 1, (255, 255, 0), 2)
        image=cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)

        cv2.imshow('frame',image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    messages.info(request,'video call ended :)')
    data=json.dumps(data)
    product=Product.objects.get(id=pk)
    vd=Video.objects.create(product=product,data=data)
    vd.save()
    cap.release()
    cv2.destroyAllWindows()
    return redirect('/sentiment/feed/{}'.format(pk))


def audio(request,pk):
    product=Product.objects.get(id=pk)
    try:
        record=sr.Recognizer()
        with sr.Microphone() as source:
            record.adjust_for_ambient_noise(source)
            rec_audio=record.listen(source)
        rec_data=record.recognize_google(rec_audio)
        analysis = TextBlob(rec_data).sentiment
        polarity=float(analysis.polarity)
        subject=float(analysis.subjectivity)
    except:
        messages.info(request,'something went wrong')
        return redirect('/sentiment/feed/{}'.format(pk))
    aud=Audio.objects.create(product=product,text=rec_data,polarity=polarity,subject=subject)
    aud.save()
    messages.info(request,"audio review successfully submitted")
    return redirect('/sentiment/feed/{}'.format(pk))

def clean_tweet(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

def get_sentiment( tweet):
    analysis = TextBlob(clean_tweet(tweet))

    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'

def getsenti(query):

    consumer_key = 'nU29NUOxn8gEx2IvGzl5zDmJE'
    consumer_secret = '8oZA1ek6k0KNn1iFhW9bxmDdvwZGR9aw8j78cWLjrlb8o4Et0o'
    access_token = '1353636277837574144-6vlHCCwtQgieGO8BfgHkp1N0G8I6BK'
    access_token_secret = 'ito6b2N028X5dvtUU5ekNnvIRyjOe67nZxV8CWNAH82oA'
    try:
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
    except:
        return HttpResponse('authentication failed')

    tweets=[]

    fetched_tweets = api.search(q = query, count=1500)

    for tweet in fetched_tweets:

        pt={}

        pt['text']=tweet.text
        pt['sentiment']=get_sentiment(tweet.text)

        if tweet.retweet_count > 0:
            if pt not in tweets:
                tweets.append(pt)
            else:
                tweets.append(pt)
    if len(tweets)==0:
        pos_rev=[]
        neg_rev=[]
        nut_rev=[]
    else:


        ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']

        ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']

        pos_rev=(100*len(ptweets)/len(tweets))

        neg_rev=(100*len(ntweets)/len(tweets))
        nut_rev=(100*(len(tweets) -(len( ntweets )+len( ptweets)))/len(tweets))

    return [{'positive_tweets':pos_rev,'negative_tweets':neg_rev,'nuetral_tweets':nut_rev},{'tweets':len(tweets),'positive tweets':len(ptweets),'negative tweets':len(ntweets),'neutral tweets':len(tweets)-(len(ptweets)+len(ntweets))}]


def smedia(request,pk):
    product=Product.objects.get(id=pk)
    org=Org.objects.get(id=product.org.id)
    products=Product.objects.filter(org=org)
    key_list=product.description.split(',')
    res_dic={}
    count_dic={}
    for i in key_list:
        data=getsenti(i)
        res_dic[i]=data[0]
        count_dic[i]=data[1]


    print(res_dic)
    return render(request,'smedia.html',{'data':res_dic,'count_data':count_dic,'name':org.name,'products':products})
