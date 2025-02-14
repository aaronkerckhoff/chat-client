from better_profanity import profanity

profanity.load_censor_words()

def filter_new_message(msg):
    if profanity.contains_profanity(msg):
        return "Message was deleted, because of inappropriate content"
    else:
        return msg
    
msg = "hi"
print(filter_new_message(msg))