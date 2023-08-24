import os
import time

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from table_clearer import table_data_mover

class slack_bot:
    
    session_dict = {
        'odds':{'path':'bb-api-odds-data-ryan','file':'betfair_run.py'},
        'scores' : {'path':'bb-api-score-data-ryan','file':'score_downloader.py'},
        'strat': {'path':'bb-strategies','file':'create_orders.py'},
        'orders': {'path':'bb-order-infastructure','file':'place_orders.py'}}

   
    
    def __init__(self):
        self.bot_slack_token : str = '######'
        self.user_slack_token : str = '######'
        self.channel : str = '######'
        self.bot_client = WebClient(token=self.bot_slack_token)
        self.user_client = WebClient(token=self.user_slack_token)
        self.table_data_mover = table_data_mover()

# Function to send a message to a specific channel
    def send_message(self, error : str, file : str = ''):
        if file != '':
            message : str = f'{file} has stopped running due to the following error : {error}' 
        else:
            message : str = error
        try:
            response = self.bot_client.chat_postMessage(
                channel=self.channel,
                text=message
            )
            print("Message sent successfully: ", response["ts"])
        except SlackApiError as e:
            print("Error sending message:", e.response["error"])
            
    def read_messages(self,count,channel_id = '######'):        
        try:
            response = self.user_client.conversations_history(channel=channel_id, limit=count)
            messages = response["messages"]
            
            # Process and print the messages
            for message in messages:
                if "text" in message:
                    
                    text = message["text"]
                    return text
    
        except Exception as e:
            self.send_message(f'Error reading messages : {e}')
        
    
    def restart(self,session):
        file = self.session_dict[session]['file']
        command = f'screen -r {session}_session -X stuff "python3 {file}^M"'
        print(command)
        try:
            os.system(command)
            self.send_message(f'{session}_session restarted')
        except:
            self.send_message('Error executing command')
        os.system(f'screen -d {session}_session')
        
    
    def kill(self,session):
        command = f'screen -r {session}_session -X stuff "^Z^M"'
        print(command)
        os.system(command)
        self.send_message(f'{session}_session killed')
    
    def git_pull(self,session):
        command = f'screen -r {session}_session -X stuff "git pull^M"'
        print(command)
        os.system(command)
        self.send_message(f'{session}_session pulled')
        
    def recreate_sessions(self):
        #for session in self.session_dict.keys():
        for session in self.session_dict.keys():
            path = self.session_dict[session]['path']
            os.system(f'screen -d -m -S {session}_session')
            print('created session') 
            os.system(f'screen -r {session}_session -X stuff "cd ..^M"')
            os.system(f'screen -r {session}_session -X stuff "cd {path}^M"')
            self.send_message(f'{session}_session created')
            
        
        
    def check_last_message(self):
        last_message = 0
        try:
            while True:
                print(last_message)
                new_message : str = self.read_messages(1)
                print(new_message)
                if new_message != last_message:
                    last_message = new_message
                    if last_message[:3] == 'bb ':
                        command = last_message[3:]
                        if 'restart' in command:
                            session = command.split(' ')[-1]
                            if session == 'all':
                                for session_ in list(self.session_dict.keys()):
                                    self.restart(session_)
                            else:
                                self.restart(session)
                        elif 'kill' in command:
                            session = command.split(' ')[-1]
                            if session == 'all':
                                for session_ in list(self.session_dict.keys()):
                                    self.kill(session_)
                            else:
                                self.kill(session)
                        elif 'clear tables' in command:
                            self.table_data_mover.clearer()
                            self.send_message('Tables cleared')
                        elif 'pull' in command:
                            session = command.split(' ')[-1]
                            self.git_pull(session)
                        elif 'recreate' in command:  
                            print('spotted restart')
                            self.recreate_sessions()
                            
                            

                    else:
                        time.sleep(20)
                else:
                    time.sleep(20)
        except Exception as e:
            self.send_message(f'Chat reader died: {e}')
            
if __name__ == '__main__':
    slack_bot().check_last_message()
    
        
        
