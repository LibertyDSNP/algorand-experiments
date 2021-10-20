const convict = require("convict");

const config = convict({
  env: {
    doc: "The application environment.",
    format: ["production", "development", "test"],
    default: "development",
    env: "NODE_ENV",
  },
  algorand: {
    wallets: {
      wallet1: {
        doc: "wallet 1",
        nmonic:
          "amount oval fabric pave tip stand essay apart galaxy embark invite become bracket maximum innocent horror pelican cage eager sing uniform material cereal ability bottom",
      },
      wallet2: {
        doc: "wallet 2",
        nmonic:
          "glance monkey turkey work crime drum spread ride guide crucial wood pencil burst borrow vessel actress vanish oyster quick media bullet fat inform about raven",
      },
      wallet3: {
        doc: "wallet 3",
        nmonic:
          "way credit device coin detect twice impose echo vague december fork right obscure defy ghost fine coin tube hello add lake laugh ostrich about advance",
      },
      wallet4: {
        doc: "wallet 4",
        nmonic:
          "neutral tenant topic upset smile vapor stand shed siege limb analyst pave demand humor nature file undo rigid inch polar resist pupil scrub absorb myth",
      },
    },
    client: {
      network: {
        doc: "the nework to connect to",
        format: String,
        default: "testnet",
        env: "ALGORAND_CLIENT_NETWORK",
      },
      host: {
        doc: "IP address",
        format: "ipaddress",
        default: "127.0.0.1",
        env: "ALGORAND_CLIENT_HOST",
      },
      token: {
        doc: "The token for Algorand client.",
        format: String,
        default:
          "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        env: "ALGO_CLIENT_TOKEN",
      },
      port: {
        doc: "The port to bind.",
        format: "port",
        default: "4001",
        env: "ALGORAND_CLIENT_PORT",
      },
    },
  },
});

module.exports = config;
