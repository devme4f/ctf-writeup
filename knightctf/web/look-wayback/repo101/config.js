module.exports = {
  app: {
    px: "PREFIX",
    token: "YOUR-PERSONAL-TOKEN",
    playing: "by Saif ❤️",
  },

  opt: {
    DJ: {
      enabled: false,
      roleName: "DJ",
      commands: [
        "back",
        "clear",
        "filter",
        "loop",
        "pause",
        "resume",
        "seek",
        "shuffle",
        "skip",
        "stop",
        "volume",
      ],
    },
    maxVol: 100,
    loopMessage: false,
    discordPlayer: {
      ytdlOptions: {
        quality: "highestaudio",
        highWaterMark: 1 << 25,
      },
    },
  },
};
