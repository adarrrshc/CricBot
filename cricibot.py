# -*- coding: utf-8 -*-

from datetime import datetime
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import json
from telegram.ext import Updater, CommandHandler
import requests
import math

admin_id = 000000

users = []
users_data = []

bot_token = ''
updater = Updater(token='')
dispatcher = updater.dispatcher
jq = updater.job_queue

url = "https://www.cricbuzz.com/match-api/livematches.json"


def init_bknd():
    print("initStarted")
    live_match_url = "https://scrcbuzz.000webhostapp.com/scr2.php?url=https://www.cricbuzz.com/match-api/livematches.json"

    try:
        res = requests.get(live_match_url)

        json_match_data = json.loads(res.text)

        matches = json_match_data["matches"]

    

        live_matches_string = ""

        # match names
        minilist = []
        for i in matches:
            match_name = "/"+i + "\n*"+matches[str(i)]["series"]["short_name"]+"*"
            if(matches[str(i)]["series"]["category"] == "International" or matches[str(i)]["series"]["category"] == 'League'):
                minilist.append(i)
    

        print(minilist)

        dispatcher.add_handler(CommandHandler(minilist, match_clicked_detected))
        print("initCompleted!")
    except Exception as e:
        print(e)


def bringup_match_keyboard(bot, update):

    live_match_url = "https://scrcbuzz.000webhostapp.com/scr2.php?url=https://www.cricbuzz.com/match-api/livematches.json"

    res = requests.get(live_match_url)
    json_match_data = json.loads(res.text)
    matches = json_match_data["matches"]
    live_matches_string = ""

    main_lis = []
    minilis = []
    # match names
    t={
        "Chennai":"CSK",
        "Kolkata":"KKR",
        "Delhi":"DC",
        "Punjab":"KXIP",
        "Mumbai":"MI",
        "Rajasthan":"RR",
        "Bangalore":"RCB",
        "Hyderabad":"SRH"
    }


    for i in matches:
        team1_name = matches[str(i)]["team1"]["s_name"]
        team2_name = matches[str(i)]["team2"]["s_name"]
        try:
            team1_name=t[team1_name]
            team2_name=t[team2_name]
        except:
            pass
        #print(team1_name+" "+team2_name)
        vs = team1_name+" vs "+team2_name
        match_name = "/"+i + "\n"+vs
        if(matches[str(i)]["series"]["category"] == "International" or matches[str(i)]["series"]["category"] == 'League'):
            minilis.append(match_name)

    for i in minilis:
        micro_list = []
        micro_list.append(i)
        main_lis.append(micro_list)
    # print(main_lis)

    bot.send_message(chat_id=update.message.chat_id, text="Choose Match",
                     reply_markup=ReplyKeyboardMarkup(keyboard=main_lis, one_time_keyboard=True, resize_keyboard=True))

old_comment=""

def send_score(bot, update, message, name=None):
    global old_live_score
    global old_comment
    match_id = message
    # print("debug:"+name)
    print("\nchecking:"+str(name))
    flag_super_over=0

    commentary_url = "https://scrcbuzz.000webhostapp.com/scr2.php?url=https://www.cricbuzz.com/match-api/" + \
        match_id+"/commentary.json"

    try:

        res = requests.get(commentary_url)
        match_data = json.loads(res.text)
        state = match_data["state"]
        status = match_data["status"]
        match_type = match_data["type"]
        state_title = match_data["state_title"]
        start_time_stamp = match_data["start_time"]
        start_time_with_date = datetime.utcfromtimestamp(
            int(start_time_stamp)).strftime('%Y-%m-%d %H:%M:%S')
        
        live_score = match_data["score"]["batting"]["score"]
        innings = match_data["score"]["batting"]["innings"][0]["id"]
        runs = match_data["score"]["batting"]["innings"][0]["score"]
        overs = match_data["score"]["batting"]["innings"][0]["overs"]
        wicket = match_data["score"]["batting"]["innings"][0]["wkts"]
        crr = match_data["score"]["crr"]
        try:
            rrr="   RRR:"+match_data["score"]["rrr"]
        except:
            rrr=""
        prev_overs = match_data["score"]["prev_overs"].split('|')
        prev_over = prev_overs[len(prev_overs)-1].split(" ")
        prev_ball = prev_over[len(prev_over)-2]
        batting_team_id = match_data["score"]["batting"]["id"]
        # print(prev_ball)
        # print(batting_team_id)
        
        l=overs.split('.')
        
        if(len(l)==1):
            rem_ovr=str(20-int(l[0]))+".0"
        else:
            rem_ovr=str(19-int(l[0]))+"."+str(6-int(l[1]))    
        
        prj_scr=str( math.floor(float(runs)+(float(rem_ovr)*float(crr))) )

        # print("rem over:"+rem_ovr)
        # print("projected score:"+prj_scr)
            
        
            
        team1_id = match_data["team1"]["id"]
        team2_id = match_data["team2"]["id"]
        
        team1_name = match_data["team1"]["s_name"]
        team2_name = match_data["team2"]["s_name"]

        four_six_wicket = ""
        

        try:
            last_comment = match_data["comm_lines"][0]["comm"]
            if(last_comment.find("href=") > 0):
                last_comment = ""

        except Exception as e:
            last_comment = match_data["comm_lines"][0]["evt"]
            if(last_comment.find("href=") > 0):
                last_comment = ""
        try:
            if(batting_team_id == team1_id):
                bat_team_codename = match_data["team1"]["s_name"]
                next_player_id = match_data["team1"]["squad"][int(wicket)+2]

            else:
                bat_team_codename = match_data["team2"]["s_name"]
                next_player_id = match_data["team2"]["squad"][int(wicket)+2]
        except Exception as e:
            next_player_id = 0
            print(e)

        # print(next_player_id)
        

        try:
            batsman1_id = match_data["score"]["batsman"][0]["id"]
            batsman1_strike=match_data["score"]["batsman"][0]["strike"]
            batsman1_runs=match_data["score"]["batsman"][0]["r"]
            batsman1_balls=match_data["score"]["batsman"][0]["b"]
            batsman1_4s=match_data["score"]["batsman"][0]["4s"]
            batsman1_6s=match_data["score"]["batsman"][0]["6s"]
            if(int(batsman1_balls)==0):
                batsman1_sr=0
            else:
                batsman1_sr=str(round((float(batsman1_runs)/float(batsman1_balls))*100,2))

            batsman2_id = match_data["score"]["batsman"][1]["id"]
            batsman2_strike=match_data["score"]["batsman"][1]["strike"]
            batsman2_runs=match_data["score"]["batsman"][1]["r"]
            batsman2_balls=match_data["score"]["batsman"][1]["b"]
            batsman2_4s=match_data["score"]["batsman"][1]["4s"]
            batsman2_6s=match_data["score"]["batsman"][1]["6s"]
            if(int(batsman2_balls)==0):
                batsman2_sr=0
            else:
                batsman2_sr=str(round((float(batsman2_runs)/float(batsman2_balls))*100,2))

            bowler1_id=match_data["score"]["bowler"][0]["id"]
            bowler1_wickets=match_data["score"]["bowler"][0]["w"]
            bowler1_runs=match_data["score"]["bowler"][0]["r"]
            bowler1_overs=match_data["score"]["bowler"][0]["o"]
        except Exception as e:
            print(e)
            pass

        
        try:
            for i in match_data["players"]:
                if(int(i["id"]) == int(next_player_id)):
                    next_player_name = i["f_name"]
                if(int(i["id"])==int(batsman1_id)):
                    batsman1_name=i["f_name"]
                if(int(i["id"])==int(batsman2_id)):
                    batsman2_name=i["f_name"]
                if(int(i["id"])==int(bowler1_id)):
                    bowler1_name=i["f_name"]

            batsman1_name=batsman1_name.split(" ")
            batsman1_name=batsman1_name[len(batsman1_name)-1]
            batsman2_name=batsman2_name.split(" ")
            batsman2_name=batsman2_name[len(batsman2_name)-1]
            bowler1_name=bowler1_name.split(" ")
            bowler1_name=bowler1_name[len(bowler1_name)-1]

            if(int(batsman1_strike)==1):
                batsman1_name=batsman1_name+"*"
            if(int(batsman2_strike)==1):
                batsman2_name=batsman2_name+"*"
        

            
        except Exception as e:
            batsman1_name=""
            batsman2_name=""
            batsman1_details=""
            batsman2_details=""
            bowler_details=""
            print(e)

        
        batsman1_details=batsman1_name+"  "+ batsman1_runs+"("+batsman1_balls+")"+"  4("+batsman1_4s+")  6("+batsman1_6s+")  SR("+batsman1_sr+")"
        batsman2_details=batsman2_name+"  "+batsman2_runs+"("+batsman2_balls+")"+"  4("+batsman2_4s+")  6("+batsman2_6s+")  SR("+batsman2_sr+")"
        bowler_details=bowler1_name+"  "+bowler1_wickets+"-"+bowler1_runs+"("+bowler1_overs+")"
        #print("next player:"+next_player_name)
        spl_event=""
        if(prev_ball == "W" or prev_ball == "W1"):
            # print("wicket!")
            four_six_wicket = "<strong>WICKET!</strong>\n"+last_comment
            spl_event="OUT!"
        elif(prev_ball == "6"):
            # print("six!")
            spl_event="SIX!"
            four_six_wicket = "<strong>SIX!</strong>\n"+last_comment
        elif(prev_ball == "4"):
            # print("Four!")
            spl_event="FOUR!"
            four_six_wicket = "<strong>FOUR!</strong>\n"+last_comment
        elif(prev_ball == "1"):
            # print("single")
            four_six_wicket == ""
        elif(prev_ball == " "):
            #print("no run!")
            four_six_wicket = ""
        elif(prev_ball == "Wd"):
            # print("Wide!!")
            spl_event="WIDE!"
            four_six_wicket = "<strong>WIDE!</strong>\n"+last_comment
        elif(prev_ball == "."):
            #print("No Run!!")
            four_six_wicket = ""
        elif(prev_ball == "N"):
            spl_event="NO BALL!"
            #print("No Ball!!")
            four_six_wicket = "<strong>NO BALL!</strong>\n"+last_comment
        # elif(last_comment.find("b>Time Out: </b>") > 0 or last_comment.find("b>strategic break</b>") > 0 or last_comment.find("b>time-out</b>") ):
        #     four_six_wicket = "<strong>TIME OUT!</strong>\n"+last_comment
        else:
            four_six_wicket = ""
            spl_event=""

        


        try:
            remaining_over = match_data["score"]["overs_left"]
        except:
            remaining_over = ""
    


            player_details_tosend=batsman1_details+"\n"+batsman2_details+"\n"+bowler_details+"\n\nRecent Balls\n"+match_data["score"]["prev_overs"]+"\n\n"+four_six_wicket     
            print(player_details_tosend)
        
    except Exception as e:
        print(e)

    
    
    t={
        "Chennai":"CSK",
        "Kolkata":"KKR",
        "Delhi":"DC",
        "Punjab":"KXIP",
        "Mumbai":"MI",
        "Rajasthan":"RR",
        "Bangalore":"RCB",
        "Hyderabad":"SRH"

        }

    bat_team_codename=t[bat_team_codename]

    if(state == "complete"):
        live_score = status
        final_text_to_send = live_score
        print("complete")
    elif(state == "inprogress"):
        print("inprogress")
        print(str(innings)+str(runs)+str(overs)+str(wicket))
        live_score = "<strong>" + bat_team_codename +" "+spl_event+ "\n" +  live_score + "   CRR:"+crr+rrr+"   PJT_SCR:"+prj_scr+"</strong>"
        if(int(innings) == 1):
            print("1st innings")
        else:
            live_score = live_score+"\n"+status
        final_text_to_send = live_score +"\n\n"+ player_details_tosend
    elif(state == "preview"):
        print("preview")
        live_score = state_title + ": match on " + start_time_with_date
        final_text_to_send = live_score
    else:
        live_score = status
        final_text_to_send = live_score

    if(status=="Match tied (Super Over in progress)"):
        final_text_to_send=final_text_to_send+"\n"+last_comment
        if(old_comment != last_comment):
            flag_super_over=1



    

    if(str(name) == "notsubscribebackend"):
        print("\nnormal!\n")
        bot.send_message(chat_id=update.message.chat_id, text=final_text_to_send,
                         parse_mode='HTML', disable_web_page_preview=True)

    elif(old_live_score != live_score or flag_super_over == 1):
        if(str(name) == "here"):
            print("here")
            completed = []
            for i in users_data:
                flag = 0
                if(int(i[1]) == 1 and str(match_id) == str(i[2])):
                    for j in completed:
                        if(str(j) == str(i[0])):
                            flag = 1
                            break
                if(flag == 0 and int(i[1]) == 1):
                    print("sending to:"+str(i[0]))
                    completed.append(i[0])
                    bot.send_message(chat_id=i[0], text=final_text_to_send,
                                     parse_mode='HTML', disable_web_page_preview=True)

    print(users_data)
    old_live_score = live_score
    old_comment=last_comment


def match_clicked_detected(bot, update):
    global users_data
    flag = 0

    for i in users_data:
        if(i[0] == str(update.message.chat_id)):
            print(i[0])
            flag = 1
            break
    if(flag == 0):
        print("added user")
        users_data.append([str(update.message.chat_id), 0, ""])
        print(users_data)
    else:
        print("user present")

    user_input = update.message.text.split("\n")[0].replace("/", "")
    sub_text = "/subscribe "+user_input
    unsub_text = "/unsubscribe "+user_input
    back_text = "/back"

    listt = [[sub_text], [unsub_text], [back_text]]
    bot.send_message(chat_id=update.message.chat_id, text="Want to Subscribe?", reply_markup=ReplyKeyboardMarkup(
        keyboard=listt, one_time_keyboard=True))

    chatid = update.message.chat_id

    live_match_url = "https://scrcbuzz.000webhostapp.com/scr2.php?url=https://www.cricbuzz.com/match-api/livematches.json"

    res = requests.get(live_match_url)
    json_match_data = json.loads(res.text)
    matches = json_match_data["matches"]
    live_matches_string = ""
    send_score(bot, update, user_input, "notsubscribebackend")


def sub_unsub_back(bot, update, args):

    recieved_text = update.message.text.split(" ")[0].replace("/", "")
    if(recieved_text == "subscribe"):
        bot.send_message(chat_id=update.message.chat_id,
                         text="Subscribed To Match "+args[0], parse_mode='Markdown')
        for i in users_data:
            if(i[0] == str(update.message.chat_id)):
                i[1] = 1
                i[2] = args[0]

    elif(recieved_text == "unsubscribe"):
        bot.send_message(chat_id=update.message.chat_id,
                         text="Unsubscribed!", parse_mode='Markdown')
        for i in users_data:
            if(i[0] == str(update.message.chat_id)):
                i[1] = 0
    elif(recieved_text == "back"):
        bringup_match_keyboard(bot, update)


def start(bot, update, job_queue):
    print("started!")
    global sub_job
    global old_live_score
    old_live_score = ""
    # print(update.message.chat.first_name)

    texxt = "Hello "+ update.message.chat.first_name + "\n" + \
        "Thanks for trying CriccBot!\nFastest Score Fetcher In Town!"
    bot.send_message(chat_id=update.message.chat_id,
                     text=texxt, parse_mode='Markdown')
    bringup_match_keyboard(bot, update)

    
    if(admin_id == int(update.message.chat_id)):
        print("started sunscribe bknd")
        bot.send_message(chat_id=admin_id,
                         text="initialised subscribe backend")
        sub_job = jq.run_repeating(
            score_sender_for_subscibed, interval=6, first=0, context=update)
    print("Start Complete!")


def score_sender_for_subscibed(bot, job):
    global users_data
    flag = 0
    # print("checking1")
    completed_sending_matches = []
    for i in users_data:
        flag = 0
        match_id = i[2]
        for j in completed_sending_matches:
            if(str(match_id) == str(j)):
                print("same match found!")
                flag = 1
                break
        if(flag != 1 and int(i[1]) == 1):
            completed_sending_matches.append(match_id)
            send_score(bot, job.context, match_id, "here")


def killswitch(bot, update, job_queue):
    global sub_job
    if(admin_id == int(update.message.chat_id)):
        try:
            sub_job.schedule_removal()
            print("\nkill subscrption backend")
            bot.send_message(chat_id=update.message.chat_id,
                             text="killed everyones subscription")

        except:
            print("\nsubscribe backend not started")
            bot.send_message(chat_id=update.message.chat_id,
                             text="subscribe backend not started yet ")

    # print("dkfdfhj")
    # url2="http://mapps.cricbuzz.com/cbzios/match/livematches"
    # res = requests.get(url2)
    # print(res)
    # json_match_data = json.loads(res.text)
    # matches = json_match_data["matches"][0]["match_id"]

    # bot.send_message(chat_id=update.message.chat_id,
    #                          text=matches)
    # print(matches)


def initter(bot, update):
    print("initStarted")
    live_match_url = "https://scrcbuzz.000webhostapp.com/scr2.php?url=https://www.cricbuzz.com/match-api/livematches.json"

    try:
        res = requests.get(live_match_url)

        json_match_data = json.loads(res.text)

        matches = json_match_data["matches"]

    except Exception as e:
        print(e)

    live_matches_string = ""

    # match names
    minilist = []
    for i in matches:
        match_name = "/"+i + "\n*"+matches[str(i)]["series"]["short_name"]+"*"
        if(matches[str(i)]["series"]["category"] == "International" or matches[str(i)]["series"]["category"] == 'League'):
            minilist.append(i)

    print(minilist)

    dispatcher.add_handler(CommandHandler(minilist, match_clicked_detected))
    print("initCompleted!")


# dispatchers
dispatcher.add_handler(CommandHandler('start', start, pass_job_queue=True))
dispatcher.add_handler(CommandHandler('livescore', bringup_match_keyboard))
dispatcher.add_handler(CommandHandler(
    ["subscribe", "unsubscribe", "back"], sub_unsub_back, pass_args=True))

dispatcher.add_handler(CommandHandler(
    'killswitch', killswitch, pass_job_queue=True))

dispatcher.add_handler(CommandHandler(
    'initstarter', initter))

updater.start_polling()


if __name__ == "__main__":
    init_bknd()
