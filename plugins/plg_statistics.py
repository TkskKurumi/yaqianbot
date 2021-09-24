from bot_backend import *
from pilloWidget import widgets,example
from pilloWidget.widgets import *
import myhash,time,heapq
from threading import Lock
from os import path
import traceback
db=myhash.splitedDict(pth=path.join(mainpth,'saves','function statistics','ts'),splitMethod=lambda x:myhash.hashs(x)[:3].lower())
'''
{
    "Group":{
        "function":{
            "Users":{
                "user":[...]
            }
            "All":[]
        }
    }
}
'''
sid2name=myhash.splitedDict(pth=path.join(mainpth,'saves','function statistics','name'),splitMethod=lambda x:myhash.hashs(x)[:3].lower())
lck=Lock()
def add_multi_timestamp_to_list(ls,tss:list,interval=7*24):
    for ts in tss:
        heapq.heappush(ls,ts)
    ts=time.time()
    while(ls and ls[0]<ts-interval*3600):
        print('ln27')
        heapq.heappop(ls)
    return ls
def add_timestamp_to_list(ls,interval=7*24):    #interval in hours
    ts=time.time()
    heapq.heappush(ls,ts)
    while(ls and ls[0]<ts-interval*3600):
        heapq.heappop(ls)
    return ls
def len_timestamp_list(ls,interval=7*24):
    ts=time.time()
    while(ls and ls[0]<ts-interval*3600):
        heapq.heappop(ls)
    return len(ls)
def count_nctx(gid,uid,func):
    lck.acquire()
    try:
        
        gid=str(gid)
        uid=str(uid)
        print("count",func,type(gid),gid,type(uid),uid)
                                    #{
        d_group=db.get(gid,{})      #group:{
        d_func=d_group.get(func,{})     #function:{
        ls_all=d_func.get('all',[])         #All:[
        add_timestamp_to_list(ls_all)
        d_func['all']=ls_all                #]All-end
        d_users=d_func.get('users',{})      #Users:{
        ls_user=d_users.get(uid,[])             #user:[
        add_timestamp_to_list(ls_user)
        d_users[uid]=ls_user                    #]user-end
        d_func['users']=d_users             #}Usrs-end
        d_group[func]=d_func            #}function-end
        db[gid]=d_group         #}
    except Exception as e:
        lck.release()
        raise e
    lck.release()
def count(ctx,func):
    lck.acquire()
    
    try:
        sctx=simple_ctx(ctx)
        
        gid=sctx.group_id
        uid=sctx.user_id
        print("count",func,type(gid),gid,type(uid),uid)
                                    #{
        d_group=db.get(gid,{})      #group:{
        d_func=d_group.get(func,{})     #function:{
        ls_all=d_func.get('all',[])         #All:[
        add_timestamp_to_list(ls_all)
        d_func['all']=ls_all                #]All-end
        d_users=d_func.get('users',{})      #Users:{
        ls_user=d_users.get(uid,[])             #user:[
        add_timestamp_to_list(ls_user)
        d_users[uid]=ls_user                    #]user-end
        d_func['users']=d_users             #}Usrs-end
        d_group[func]=d_func            #}function-end
        db[gid]=d_group         #}
    except Exception as e:
        lck.release()
        raise e
    lck.release()
pending_count_batch={}
def count_batch(ctx,func):
    sctx=simple_ctx(ctx)
    id=(sctx.simple_id,func)
    tss=pending_count_batch.get(id,[])
    ts=time.time()
    tss.append(ts)
    if(ts-tss[0]>60):   #save every 30 seconds I think should be flexible and suitable for both frequent
        count_multi(ctx,func,tss)   #operations and rare operations
        tss=[]
    pending_count_batch[id]=tss
def count_multi(ctx,func,tss):
    lck.acquire()
    try:
        tmr=receiver_timer('count multi')
        sctx=simple_ctx(ctx)
        
        gid=sctx.group_id
        uid=sctx.user_id        
                                    #{
        d_group=db.get(gid,{})      #group:{
        d_func=d_group.get(func,{})     #function:{
        ls_all=d_func.get('all',[])         #All:[
        add_multi_timestamp_to_list(ls_all,tss)
        d_func['all']=ls_all                #]All-end
        d_users=d_func.get('users',{})      #Users:{
        ls_user=d_users.get(uid,[])             #user:[
        add_multi_timestamp_to_list(ls_user,tss)
        d_users[uid]=ls_user                    #]user-end
        d_func['users']=d_users             #}Usrs-end
        d_group[func]=d_func            #}function-end
        db[gid]=d_group         #}
        tmr.finish()
    except Exception as e:
        lck.release()
        raise e
    lck.release()
def normal_sid(group_id,user_id):
    return "%s-%s"%(group_id,user_id)



@receiver
@threading_cnt('statistics_usage')
@on_exception_send
@start_with("/统计")
def cmd_statistics_usage(ctx,match,rest):
    rest=rest.strip()
    fuckyou=example.plot_bar_chart_horizontal

    if(not rest):
        sctx=simple_ctx(ctx)
        gid=sctx.group_id
        items=[]            #{
        d_group=db.get(gid,{}) #group:{
        for func in d_group:        #function:{
            all_ls=d_group.get(func,{}).get('all',[])
            cnt=len_timestamp_list(all_ls)
            #mx_cnt=max(mx_cnt,cnt)
            if(cnt):
                items.append((func,cnt))
        if(not items):
            simple_send(ctx,'没有使用信息')
            return
        im=fuckyou(items,'七天内功能统计',name_format=lambda name,num:"%s: %d"%(name,num))
        simple_send(ctx,im)
    else:
        func=rest
        sctx=simple_ctx(ctx)
        gid=sctx.group_id   #{
        d_group=db.get(gid,{})  #group:{
        d_func=d_group.get(func,{}) #function:{
        d_users=d_func.get('users',{})      #Users:{
        items=[]
        for uid,ls in d_users.items():
            cnt=len_timestamp_list(ls)
            name=sid2name.get(normal_sid(gid,uid),'未知用户名')
            if(cnt):
                items.append((name,cnt))
        if(not items):
            simple_send(ctx,'没有使用信息')
            return
        im=fuckyou(items,'七天内%s使用用户统计'%func,name_format=lambda name,num:"%s: %d"%(name,num))
        simple_send(ctx,im)
@receiver
@threading_cnt('count say')
def cmd_count_say(ctx):
    try:
        tmr=receiver_timer('发言计数')
        count_batch(ctx,'发言')
        sctx=simple_ctx(ctx)
        sid=normal_sid(sctx.group_id,sctx.user_id)
        sid2name[sid]=sctx.user_name
        tmr.finish()
    except Exception:
        traceback.print_exc()