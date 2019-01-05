#!/usr/bin/env python
import csv
import MySQLdb
import cgi, json, os, sys,string
from optparse import OptionParser
import json
import random

__version__="1.0"
__status__ = "Dev"

#***********    SAVING QUESTION TO DATABASES START HERE     *************#
##################################################
def save_Question_to_DB():
# truncate or delete everything that's in t_question and t_choice
    dbh = connectionWithGameDB()
    sql_script = "truncate t_question;truncate t_choice"
    
    cursor = dbh.cursor()
    cursor.execute(sql_script)
    dbh.commit
    cursor.close()

    question_file = open("csv/linuxQuestionFile.csv", "r")
    
    #print(question_file.readlines()[0])

    for line in question_file:
        question_list =line.strip().split(",")
        randomizChoice(question_list)

    question_file.close()
    return #"Everything has been saved or reset"
#########################################
def randomizChoice (question_list):
    #print "question_list ==> ", question_list
    if (len(question_list) == 6):
        question = str(question_list[0])
        
        ques_level = question_list[1]
        
        txt_answer = str(question_list[2])
        
        text_choice = [
            str(question_list[2]),
            str(question_list[3]),
            str(question_list[4]),
            str(question_list[5])
        ]
        
        rnd_index = random.randint(0,3)
        lbl_answer = str(lbl_choice[rnd_index])

        question_id=save_to_t_question(question, ques_level, lbl_answer)
        if (rnd_index is not 0):
            hold_answer = text_choice[rnd_index]
            text_choice[rnd_index] = text_choice[0]
            text_choice[0] = hold_answer

        #print "text_choice ==> ", text_choice
        save_to_t_choice_table(question_id, text_choice)
    
    return 
##############################################
def save_to_t_question(question, ques_level, lbl_answer):
    # save the question, level, and answer into t_question and then retrive the question_id where question='question'
    
    dbh = connectionWithGameDB()

    sql_script = "insert into t_question (question,level, answer) value ('%s','%s','%s')" %(question, ques_level, lbl_answer)
    
    cursor = dbh.cursor()
    cursor.execute(sql_script)
    dbh.commit()
    cursor.close()

    sql_script2 = "select id from t_question where question='%s'" %(question)
    cursor2 = dbh.cursor()
    cursor2.execute(sql_script2)
    dbh.commit()
    fetched_data = cursor2.fetchall()

    cursor2.close()
    question_id = fetched_data[0][0]     #((question_id,),)
    #print "question_id ==>",question_id

    return question_id
##########################################
def save_to_t_choice_table(question_id, txt_choice):
    dbh = connectionWithGameDB()
    for i in xrange(0,len(lbl_choice)):
        sql_script = "insert into t_choice (question_id, choice_label, choice_text) value ('%d','%s','%s')" % (question_id, lbl_choice[i],txt_choice[i])
        cursor = dbh.cursor()
        cursor.execute(sql_script)
        dbh.commit()
    cursor.close()

    return
#*****************    SAVING QUESTION TO DATABASES END HERE     *************#
##################################################
def connectionWithGameDB(): 
    
    db_name = "drop_down_game"
    db_userid = "root"
    db_password = "pass123"
    db_host = "127.0.0.1" # localhost
    
    dbh = MySQLdb.connect(host=db_host, user=db_userid, passwd = db_password, db =db_name)

    return dbh

#############################
def saveCVSFileToDB(file_path,table_name):
    
    dbh = connectionWithGameDB()

    sql_script = "load data local infile '%s' into table %s fields terminated by ',' lines terminated by '\n' (questions,answers,level)" %(file_path, table_name)
    
    cursor = dbh.cursor()
    cursor.execute(sql_script)
    dbh.commit()
    
    cursor.close()

    return

###################################
def saveSignleColumnToDB(dbh, table_name, column_name, value):
    
    sql_script = "insert into %s (%s) value ('%s')" % (table_name, column_name, value)
    cursor = dbh.cursor()
    cursor.execute(sql_script)
    dbh.commit()
    
    cursor.close()

    return

###################################
def retrieveDataFromDB(dbh, restriction):
    # dbh ==> is the connection made with your database
    
    # restriction format ==> [ [table_name1, table_name2], [column1, column2, or just *], {key1:value1, key2:value2}]
    table_name = ""
    selected_Column = ""
    where_value = ""
    commaNum = 0
    andNum = 0

    for i in xrange(0, len(restriction)):

        size = len(restriction[i])
        if i == 0: #list[] for the table name where to select 
            if size == 1:
                table_name = restriction[i][0]
            else: # if the table you're trying to select are from more than 1
                for j in xrange(0, size):
                    table_name = restriction[i][j]
                    
                    commaNum += 1
                    if commaNum < size:
                        table_name += ", "
                
            
        if i == 1: #list[] for what column to select
            if size == 1:
                selected_Column = restriction[i][0]
            else:
                commaNum = 0
                for j in xrange(0,size):
                    selected_Column += restriction[i][j]
                
                    commaNum += 1 
                    if commaNum < size:
                        selected_Column += ", "
        elif i == 2: #disctinary{} for where [column]=''
            
            if size >= 1:
                where_value += " WHERE " # make sure to have space before and after the word "WHERE"
                for key in restriction[i]:
                    
                
                    where_value += key
                    where_value += "='"
                    where_value += restriction[i][key]
                    where_value += "'"
                
                    andNum += 1 
                    if andNum < size:
                        where_value +=" AND " # make sure to have space before and after the word "AND"
                    
                    
            

    #print "selected_Column", selected_Column
    #print "where_value", where_value
    

    
    sql_script = "SELECT %s FROM %s %s" % (selected_Column, table_name, where_value)
    cursor = dbh.cursor()
    cursor.execute(sql_script)
    dbh.commit()
    fetched_data = cursor.fetchall() 
    
    
    cursor.close()                
    

    return fetched_data
##################################################
def JoinTable(level):
    dbh = connectionWithGameDB()

    sql_script = "SELECT t_question.id, t_question.question, t_choice.choice_label, t_choice.choice_text FROM t_question INNER JOIN t_choice on t_question.id = t_choice.question_id AND t_question.level=%s" %(level)# % (selected_Column, table_name, where_value)
    cursor = dbh.cursor()
    cursor.execute(sql_script)
    dbh.commit()
    fetched_data = cursor.fetchall() 
    # format of fetched_data is ((t_question.id, t_question.question, t_choice.label, t_choice.text),(., ., ., .), .....) 
    out_obj = {"questions":{}}

    for row in fetched_data:
        q_id = row[0]
        q_txt = row[1]
        c_lbl = row[2]
        c_txt = row[3]
        if (q_id not in out_obj["questions"]):
            out_obj["questions"][q_id] = {"question": q_txt, "choice_list":[]}
        out_obj["questions"][q_id]["choice_list"].append({"choice_label": c_lbl, "choice_text":c_txt})
            
            
    
    cursor.close()                
    
    #print out_obj
    return out_obj




################################################
def getQuestion(level):
    table_name = ["t_question A", "t_choice B"]
    selected_column = ["t_question.id", "A.question", "B.choice_label", "B.choice_text"]
    
    fetched_question = retrieveDataFromDB(connectionWithGameDB(), [table_name, selected_column, {"B.question_id":"A.id"}]) 
    
    print fetched_question
    return fetched_question
##################################
def check_Answer(playerAnswerObj):
    buttonId = playerAnswerObj.keys()[0]
    player_answer = playerAnswerObj[buttonId]
    question_id = getId(buttonId)
    restriction = [["t_question"],["answer"],{"id":question_id}]

    answer_for_current_id =  retrieveDataFromDB(connectionWithGameDB(), restriction)[0][0] # ex. fetchData comes (('A',),) so add this [0][0] to get A

    ##print "********************answer_for_current_id ==>" , answer_for_current_id
    player_answer_status = ""; 
    
    if (player_answer == answer_for_current_id): # You can write your own equal method
        player_answer_status = "Correct"
    elif (player_answer is not answer_for_current_id):
        player_answer_status = "Incorrect"
    else:
        player_answer_status = "You have an error coming from web server :- check_Answer() method | MySQL"

    return player_answer_status
#############################################
def getId(buttonId):
    # buttonId format ==> id_[question_id]
    question_id = buttonId[3:]
    ##print "***************question_id ==> ", question_id
    
        
    return question_id
#############################################
###############################################
def main():


    
    usage = "\n%prog  [options]"
    parser = OptionParser(usage,version="%prog " + __version__)
    parser.add_option("-j","--inJson",action="store",dest="inJson",help="File name")

    FHASH = cgi.FieldStorage()
    keylist = FHASH.keys();
    mode = "remote" if len(keylist) > 0 else "local"

    inJson = {}
    #randomize = rset the value of randomize to be 0 every day
    (options,args) = parser.parse_args()
    if mode == 'local':
        for key in ([options.inJson]):
            if not (key):
                parser.print_help()
                sys.exit(0)
            inJson = json.loads(options.inJson)
    else:
        inJson = json.loads(FHASH["inJson"].value) if "inJson" in FHASH else {}
        
    global lbl_choice 
    lbl_choice = ["A","B","C","D"]
   # print save_Question_to_DB()
    

    outJson = {}
    
    if inJson["action"] == "getFirstPage":
        outJson = {"levelObj":{1:1,2:2,3:3}}
        outJson["taskStatus"] = 1
        #save_Question_to_DB()
    elif inJson["action"] == "getSecondPage":
        outJson = JoinTable(inJson["level"])
        outJson["taskStatus"] = 1
        
    elif inJson["action"] == "checkForAnswer":
        outJson = {"answerStatusFor_"+inJson["playerAnswerObj"].keys()[0]+"": check_Answer(inJson["playerAnswerObj"])}
        outJson["taskStatus"] = 1

    #We print out some content type infor   
    print "Content-Type: text/html"
    print
    print """"""
   
    print json.dumps(outJson, sort_keys=True, indent=4, separators=(',', ': '));


    """
        sql script used during 8/4/2018 class
    
    select A.id, A.question, B.choice_label, B.choice_text FROM t_question A, t_choice B where A.id = B.question_id; 
    insert into t_choice (question_id, choice_label, choice_text) values (33, 'A', '54');
    insert into t_question (question, level, answer) values ('How many countries in Africa?', 1, '');

    update t_question set answer = 'A' where id = 33;
    
    alter table t_question drop column answers;

    alter table t_question add column answer varchar(1);

    select A.id, A.question, B.choice_label, B.choice_text FROM t_question A, t_choice B where A.id = B.question_id;

    delete from t_question where id > 1; 

    alter table t_question add column id int primary key auto_increment;


    """


if __name__ == '__main__':
    main()


