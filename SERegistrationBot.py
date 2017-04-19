import discord
import asyncio
import random
import requests
import time
import json
from operator import itemgetter
import sc_to_json
from bs4 import BeautifulSoup 


# Startup and reference values
client = discord.Client()


# All data titles are in proper cases i.e. Data Titles or command e.g. ;asteroid

def check_for_os(string):
    if 'os' in string.replace('.',' ').split():
        return True
    else:
        return False

def jsonwrite(json_dic, datafile):
    with open(datafile, 'w') as target:
        json.dump(json_dic, target, indent=4, separators=(',',':'))
    
with open('explorer_data.json') as scoreboard:
    score = json.load(scoreboard)

@client.event
async def on_message(message):
    if message.author != client.user:
        maid = message.author.id

        # Register a system
        if message.content.startswith(';register'):
            time_list = score['time']
            if message.author.id in list(time_list.keys()):
                last = time_list[message.author.id]
            else:
                last = 0
            time_passed = time.time()- last
            if time_passed > 300:
                part = message.content.split()
                if len(part) > 1:
                    file = part[1]
                    if file.startswith('https://') and file.endswith('.sc'):
                        systemname = file.split('/')[-1].replace('.sc','').replace('_',' ')
                        if systemname not in score['system_list']:
                            opened = requests.get(file).text
                            messaged = await client.send_message(message.channel, 'Caching file...')
                            cache_name = 'cache' + '.txt' 
                            with open(cache_name, 'w') as cache_file:
                                cache_file.write(opened)
                            if len(part) > 2:
                                nickname = ' '.join(part[2::])
                            else:
                                nickname = systemname
                            res = sc_to_json.to_json(cache_name, 'se_data', systemname, nickname)
                            op_js = res[0]
                            t_v = res[1]
                            b_c = 0
                            for key in op_js['body_count'].keys():
                                b_c += op_js['body_count'][key]
                            if 'Star' in list(op_js['body_count'].keys()):
                                s_c = str(op_js['body_count']['Star'])
                            else:
                                s_c = 0
                            if 'Planet' in list(op_js['body_count'].keys()):
                                p_c = str(op_js['body_count']['Planet'])
                            else:
                                p_c = 0
                            if maid in list(score['users'].keys()):
                                score['users'][maid]['systems_discovered'] += 1
                                score['users'][maid]['points'] += t_v
                                sys_score = int(t_v)
                                score['users'][maid]['username'] = message.author.name
                                score['system_list'][systemname] = op_js
                                bm = ''
                            else:
                                score['users'][maid] = {}
                                score['users'][maid]['systems_discovered'] = 1
                                sys_score = int(int(t_v)*1.5)
                                score['users'][maid]['points'] = sys_score
                                score['users'][maid]['username'] = message.author.name
                                score['system_list'][systemname] = op_js
                                bm = ' **Congratulations in uploading your first system! You earned a 1.5x multiplier for first time!**'
                            cur_sc = score['users'][maid]['points']
                            reg_time = time.time()
                            score['system_list'][systemname]['value'] = int(t_v)
                            score['time'][message.author.id] = reg_time
                            score['system_list'][systemname]['nick'] = nickname
                            score['system_list'][systemname]['time_discovered'] = reg_time
                            score['system_list'][systemname]['discovered_by'] = message.author.id
                            jsonwrite(score, 'explorer_data.json')
                            edited_message = '{0} registered to database.\n{1} bodies registered with {2} stars and {3} planets.\n{4} points have been added to {5}\'s account.\nCurrent: {7} points.{6}'.format(nickname, b_c, s_c, p_c, sys_score, message.author.mention, bm, cur_sc)
                            await client.edit_message(messaged, edited_message)
                        else:
                            await client.send_message(message.channel, "Sorry, that system had already been discovered by {0}!".format(message.author.display_name))
                else:
                    await client.send_message(message.channel, 'Register in the format:\n```;register (link to .sc file) (system name)```')
            else:
                await client.send_message(message.channel, "{0}, please wait another {1} seconds before registering another system.".format(message.author.mention, int(300-time_passed)))

        # See balance
        elif message.content == ';score':
            if maid in list(score['users'].keys()):
                await client.send_message(message.channel, "{0}, you currently have {1} points from {2} systems.".format(message.author.mention, score['users'][maid]['points'], score['users'][maid]['systems_discovered']))
            else:
                await client.send_message(message.channel, "{0}, you have not registered a single system. Use ;register to register an exported system!".format(message.author.mention)) 
        # List systems
        elif message.content == ';systems':
            if maid in list(score['users'].keys()):
                sy = score['system_list']
                print([k for k in sy])
                sr = [sy[k] for k in sy if sy[k]['discovered_by'] == maid]
                sl = []
                for sdic in sr:
                    sl.append('{0}. {1} - {2} Stars and {3} planets ({4} points)'.format(sr.index(sdic)+1,sdic['nick'],
                                                                                        sdic['body_count']['Star'],
                                                                                        sdic['body_count']['Planet'], sdic['value']))     
                s = '```{0}```'.format('\n'.join(sl))
                c = 0
                while len(s) > 1999:
                    sl = sl[1:] 
                    c += 1
                    s = '```{0}```'.format('\n'.join(sl))
                await client.send_message(message.channel, s)
                if c != 0:
                    await client.send_message(message.channel, 'and {0} more...'.format(c))
            else:
                await client.send_message(message.channel, 'You have no registered systems.')
        
        elif message.content == ';help':
            await client.send_message(message.channel, 'Use ;register (link) (system name) to register a system, ;score to see score, and ;system to see registered names!\nIn order to upload a system, use the "Export System" option and upload the .sc file to Discord before getting the link!')
                            
#Just to know it's running    
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    # await client.send_message(client.get_channel(str(217142893440270346)), 'I\'m online, use ;register to register your systems!')
        

#Runs the whole thing
client.run(client_id)

