import discord as d
import re;
import traceback


client = d.Client()

regex = r"(?i)(discord\.gg/[a-z0-9]+|discordapp\.com/invite/[a-z0-9]+|add\W*me\W*(?:pl[sz]\W*)?.*\(tag\)\W*\d+)"
pattern = re.compile(regex)

channelRegex = r"<#[0-9]+>"
channelPattern = re.compile(channelRegex)

# Auth: https://discordapp.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&scope=bot&permissions=8
# Create an app at https://discordapp.com/developers/applications/me
token = None
id = None

channels = {}
admins = ["363018555081359360"]

helpMessage = "Hello! I'm a bot created by Olivia#0740. I block spam users with invites in their names. Code: <https://github.com/LunarWatcher/BlockerBot/> Bot server invite ID: bpj3V75"


class SizeLimitedStack:

    def __init__(self, size):
        self.size = size;
        self.data = []
        assert size > 0

    def add(self, item):
        if(len(self.data) < self.size):
            self.data.append(item)
        else:
            self.data.pop(0);
            self.data.append(item)

    def pop(self, index):
        self.data.pop(index)

    def get(self, index):
        return self.data[index]

    def getSize(self):
        return len(self.data)

    def isNotEmpty(self):
        return self.getSize() != 0

    def isEmpty(self):
        return self.getSize() == 0

    def clear(self):
        self.data.clear()


botMessages = SizeLimitedStack(50)
nukableUsers = SizeLimitedStack(10)


@client.event
async def on_ready():
    print("Logged in successfully.")


@client.event
async def on_member_join(member: d.Member):
    username = member.display_name
    print("Checking user " + username);
    if(re.findall(pattern, username)):
        print("***Match detected***")
        server = member.server
        await sendMessage("Matching user detected. Nuking user " + member.id + "...", server);
        try:
            await client.ban(member, 1)

        except:
            await sendMessage("Failed to nuke user. Check my permissions, please", server)
            return
        try:
            count = await nukeMessages(member)
            await sendMessage("Messages nuked: " + str(count), server)
        except d.Forbidden:
            await sendMessage("Failed to remove messages! Check my permissions", server)
            tb = traceback.format_exc()
            print(tb)
        except d.HTTPException:
            await sendMessage("An HTTP error occured when removing messages", server)
            tb = traceback.format_exc()
            print(tb)

        await sendMessage("User nuked", server)


async def nukeMessages(member):
    count = 0
    username = member.display_name
    userid = member.id

    if(botMessages.isNotEmpty()):
        for message in botMessages.data:

            messageContent = message.content
            if "<@" + userid + ">" in messageContent or "<@!" + userid + ">" in messageContent:
                print("Message found! Author: " + message.author.display_name);
                print("Content:" + messageContent)
                print()
                await client.delete_message(message)
                count += 1

            elif username.lower() in messageContent.lower():
                print("Message found! Plaintext mode. Author: " + message.author.display_name)
                print("Content:" + messageContent)
                print()
                await client.delete_message(message)
                count += 1
        botMessages.clear()
    nukableUsers.add(member)
    return count


async def sendMessage(content: str, server: d.Server):

    # Check if the server has a defined channel to send the message to.
    if (str(server.id) in channels):
        await client.send_message(client.get_channel(str(channels[str(server.id)])), content)
        return;
    # If none defined, go for other options:
    for c in server.channels:
        if c.name == 'blocker-bot':
            await client.send_message(c, content)
            return;
    for c in server.channels:
        if(c.name == "general"):
            await client.send_message(c, content);
            return;
    for c in server.channels:
        if(c.name == "chat"):
            await client.send_message(c, content);
            return;


@client.event
async def on_message(message):


    if(message.author.bot):
        botMessages.add(message)
        if(nukableUsers.isNotEmpty()):
            for user in nukableUsers.data:
                try:
                    await nukeMessages(user)
                except:
                    continue
            nukableUsers.clear()
        return;

    if(message.content.startswith("!!")):
        if(message.content.startswith("!!help")):
            await client.send_message(message.channel, helpMessage)
        elif(message.content.startswith("!!join")):
            await client.send_message(message.channel, "https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8".format(id))
        elif message.content.startswith("!!alive"):
            await client.send_message(message.channel, "Nah, I'm dead")
        elif message.content.startswith("!!github"):
            await client.send_message(message.channel, "")
        elif message.content.startswith("!!output"):
            if(str(message.author.id) not in admins and not message.author.server_permissions.administrator):
                await client.send_message(message.channel, "You need to be a server admin to do that");
                return
            items = message.content.split(" ", 1)
            if (len (items) != 2):
                await client.send_message(message.channel, "Where?")
                return
            channel = str(items[1])
            if not re.match(channelPattern, channel):
                await client.send_message(message.channel, "Please specify the channel by doing #channelname")
                return;

            channel = channel[2:len(channel) - 1]
            raw = client.get_channel(channel)
            try:
                await client.send_message(raw, "Registered channel")
            except d.Forbidden:
                await client.send_message(message.channel, "No access.")
            channels[str(message.server.id)] = int(channel)
        elif message.content.startswith("!!say"):
            items = message.content.split(" ", 1)
            if (len (items) != 2):
                await client.send_message("What?")
                return
            await client.send_message(message.channel, items[1])
        elif message.content.startswith("!!exit"):
            if(message.author.id not in admins):
                await client.send_message(message.channel, "No")
                return;
            await save()
            exit(1);
            return;


if(token == None or id == None):
    raise AssertionError("Set the necessary attribs, please");

async def save():

    file = open("data.dat", "w")
    builder = ""
    for server, channel in channels.items():
        builder += server + "," + str(channel) + "\n"
    file.write(builder)
    file.close()

def load():
    try:
        file = open("data.dat", "r")
        content = file.read()
        map = content.split("\n")
        if(len(map) == 0):
            return;
        for item in map:
            if(len(item) == 0):
                continue;
            sub = item.split(",")
            if(len(sub) != 2):
                print("Wrong len! " + item)
                continue;
            channels[sub[0]] = int(sub[1])
        file.close()
    except:
        pass;


load()
print("Stored channels:")
print(channels)
client.run(token)
