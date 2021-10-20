const algosdk = require("algosdk");
const config = require("./config");

const algodToken = config.get("algorand.client.token");
const algodHost = config.get("algorand.client.host");
const algodServer = `http://${algodHost}`;
const algodPort = config.get("algorand.client.port");

let client = new algosdk.Algodv2(algodToken, algodServer, algodPort);

module.exports = client;
