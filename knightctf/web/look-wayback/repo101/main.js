const { Player } = require('discord-player');
const { Client, Intents } = require('discord.js');

global.client = new Client({
    intents: [
        Intents.FLAGS.GUILDS,
        Intents.FLAGS.GUILD_MEMBERS,
        Intents.FLAGS.GUILD_MESSAGES,
        Intents.FLAGS.GUILD_VOICE_STATES
    ],
    disableMentions: 'everyone',
});

client.config = require('./config');

global.player = new Player(client, client.config.opt.discordPlayer);

require('./src/loader');
require('./src/events');

bot.on("guildMemberAdd", (member) => {
  let ctx = db.get(`welchannel_${member.guild.id}`);
  if (ctx === null) {
    return; 
  }
  const emb1 = new Discord.MessageEmbed()
    .setColor("RED")
    .setAuthor(member.user.username, member.user.avatarURL())
    .setDescription(`Welcome Buddy!!!Have Fun!!`);
  bot.channel.cache.get(ctx).send(emb1);
});

client.login(client.config.app.token);